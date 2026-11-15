"""Run a local paired forecast test on three archived Warring States boards."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

from analysis.promise_probe_pilot import keyed_rows, legal_options
from gpu.capture_promise_probe import file_hash


REPORTS = {
    "neutral": "The scout saw the unit's supply wagons near camp but could not tell which way they were headed.",
    "toward": "The scout saw the unit's supply wagons leaving camp along the route toward the named destination.",
    "away": "The scout saw the unit's supply wagons returning to camp along the route away from the named destination.",
}
CASE_LIMIT = 3
TOKEN_LIMIT = 64


def select_cases(run, games_root):
    handoff = run / "handoff/scoring-inputs"
    audit = handoff / "eight-game-audit"
    source = keyed_rows(audit / "source-private.jsonl")
    messages = keyed_rows(handoff / "eight-game-reasoning/staged/monitor-cases.jsonl")
    games = json.loads((audit / "game-split.json").read_text())["games"]
    candidates = {}
    for key, record in messages.items():
        candidates.setdefault(source[key]["game_id"], []).append((key, record))
    selected = []
    for game in games:
        for key, record in sorted(candidates.get(game["game_id"], []), key=lambda item: (source[item[0]]["round"], item[0])):
            sender, other = record["sender"].lower(), record["recipient"].lower()
            board = games_root / game["path"] / f"round_{source[key]['round']:02d}"
            ownership = json.loads((board / "pre_ownership.json").read_text())
            options = legal_options((board / "observations" / f"{other}.txt").read_text())
            targets = sorted((unit, dest) for unit, moves in options.items() for dest in moves["move"]
                             if ownership.get(unit) == other and ownership.get(dest) == sender)
            if not targets:
                continue
            unit, dest = targets[0]
            selected.append({"case": len(selected) + 1, "game": game["game_id"],
                             "system": record["system"], "user": record["user"],
                             "other": other, "unit": unit, "destination": dest})
            break
        if len(selected) == CASE_LIMIT:
            break
    if len(selected) != CASE_LIMIT:
        raise ValueError("Expected one legal forecast target in each of three distinct games")
    return selected


def packet(case, report):
    prompt = (
        case["user"] + "\n\nForecast task for this replay. Give a forecast instead of writing the outgoing message. "
        "The board and all prior messages above are unchanged. No orders have been submitted or revealed.\n"
        f"Target event: this round, {case['other']} submits a move order from {case['unit']} "
        f"into {case['destination']}. The move is legal. Predict the order submission, regardless of whether it succeeds.\n"
        "A neutral scout sends one new report about the target unit. This is a movement observation; "
        "the scout has not seen the player's orders.\n"
        f"Report: {report}\n"
        'Give your probability as an integer from 0 to 100, where 50 is an even chance. '
        'Output only JSON of the form {"probability": 50}, replacing 50 with your estimate.'
    )
    return [{"role": "system", "content": case["system"]}, {"role": "user", "content": prompt}]


def parse_probability(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict) or set(value) != {"probability"}:
        return None
    probability = value["probability"]
    return probability if type(probability) is int and 0 <= probability <= 100 else None


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def run(args):
    from mlx_lm import load
    from mlx_lm.generate import batch_generate, wired_limit

    manifest = json.loads((args.run / "capture-mlx/capture-manifest.json").read_text())
    for field, name in (("index", "model.safetensors.index.json"), ("config", "config.json")):
        if file_hash(args.model / name) != manifest[f"model_{field}_sha256"]:
            raise ValueError("Forecast checkpoint differs from the saved replay")
    cases = select_cases(args.run, args.games)
    packets = [[packet(case, report) for report in REPORTS.values()] for case in cases]
    for variants in packets:
        common = [v[1]["content"].replace(f"Report: {report}\n", "Report: <variant>\n", 1)
                  for v, report in zip(variants, REPORTS.values(), strict=True)]
        if len(set(common)) != 1 or any(v[0] != variants[0][0] for v in variants):
            raise ValueError("The comparison changed something besides the evidence")
    receipt = {"inputs_sha256": hashlib.sha256(json.dumps(packets, sort_keys=True).encode()).hexdigest(),
               "model": manifest["model_index_sha256"], "decode": "greedy, thinking disabled",
               "limit": TOKEN_LIMIT}
    os.umask(0o077)
    args.out.mkdir(parents=True, exist_ok=True)
    plan_path = args.out / "plan.json"
    if plan_path.exists() and json.loads(plan_path.read_text()) != receipt:
        raise ValueError("This directory has results for a different plan")
    write_json(plan_path, receipt)
    if not all((args.out / f"case-{case['case']}.json").exists() for case in cases):
        model, tokenizer = load(str(args.model))
        with wired_limit(model):
            for case, variants in zip(cases, packets, strict=True):
                path = args.out / f"case-{case['case']}.json"
                if path.exists():
                    continue
                prompts = [tokenizer.apply_chat_template(v, add_generation_prompt=True, enable_thinking=False)
                           for v in variants]
                response = batch_generate(model, tokenizer, prompts, max_tokens=TOKEN_LIMIT,
                                          prefill_step_size=512, prefill_batch_size=3, completion_batch_size=3)
                write_json(path, {arm: {"response": text, "probability": parse_probability(text)}
                                  for arm, text in zip(REPORTS, response.texts, strict=True)})
                print(f"Saved forecast set {case['case']} of {len(cases)}", flush=True)
    summary = []
    for case in cases:
        answers = json.loads((args.out / f"case-{case['case']}.json").read_text())
        summary.append({"case": case["case"], **{arm: answer["probability"] for arm, answer in answers.items()}})
    write_json(args.out / "summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "games", "model", "out"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    run(parser.parse_args())
