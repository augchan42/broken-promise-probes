"""Cross scout-report phrasing and board state in matched private forecast cases."""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re

from analysis.kui_forecast_pilot import REPORTS, TOKEN_LIMIT, packet, parse_probability, write_json
from analysis.promise_probe_pilot import keyed_rows, legal_options
from gpu.capture_promise_probe import file_hash


PARAPHRASES = {
    "toward": "According to the scout, the unit's supply wagons were seen departing camp on the road leading to the specified destination.",
    "away": "According to the scout, the unit's supply wagons were seen coming back to camp on the road leading away from the specified destination.",
}
WORDINGS = {"original": REPORTS, "paraphrase": PARAPHRASES}
BOARDS = ("vacant", "occupied")
DIRECTIONS = ("toward", "away")
BOARD_START = "POWER BALANCE:\n"
BOARD_END = "\nNEGOTIATION PHASE"


def prompt_sections(prompt):
    head, start, tail = prompt.partition(BOARD_START)
    board, end, rest = tail.partition(BOARD_END)
    if not start or not end:
        raise ValueError("Archived prompt does not have the expected board section")
    return head, start + board, end + rest


def matched_boards(run, games_root):
    handoff = run / "handoff/scoring-inputs"
    audit = handoff / "eight-game-audit"
    source = keyed_rows(audit / "source-private.jsonl")
    messages = keyed_rows(handoff / "eight-game-reasoning/staged/monitor-cases.jsonl")
    games = {game["game_id"]: game["path"] for game in json.loads((audit / "game-split.json").read_text())["games"]}
    candidates = defaultdict(lambda: defaultdict(list))
    for key, message in messages.items():
        record = source[key]
        game, round_number = record["game_id"], record["round"]
        sender, other = message["sender"].lower(), message["recipient"].lower()
        board = games_root / games[game] / f"round_{round_number:02d}"
        ownership = json.loads((board / "pre_ownership.json").read_text())
        sender_options = legal_options((board / "observations" / f"{sender}.txt").read_text())
        opponent_options = legal_options((board / "observations" / f"{other}.txt").read_text())
        _, board_text, _ = prompt_sections(message["user"])
        rows = re.findall(r"^  (\w+): (\d+) SCs \[(.*?)(?: \+ corridors: ([^\]\n]*))?\]", board_text, re.M)
        centers = set()
        for owner, count, names, _ in rows:
            places = [] if names == "(none)" else names.split(", ")
            if len(places) != int(count) or any(ownership.get(p) != owner.lower() for p in places):
                raise ValueError("Archived prompt and board disagree about supply centers")
            centers.update(places)
        if not rows:
            raise ValueError("No supply center data in the archived prompt")
        for unit, options in opponent_options.items():
            if ownership.get(unit) != other:
                continue
            for dest in options["move"] & centers:
                if ownership.get(dest) == sender:
                    state = "occupied" if dest in sender_options else "vacant"
                    candidates[(game, sender, other, unit, dest)][state].append((round_number, key))

    matched = []
    for game in games:
        pairs = [(abs(v[0] - o[0]), key, v, o)
                 for key, options in candidates.items() if key[0] == game
                 for v in options["vacant"] for o in options["occupied"]]
        if not pairs:
            continue
        _, key, vacant, occupied = min(pairs)
        _, _, other, unit, dest = key
        anchor = messages[vacant[1]]
        head, _, tail = prompt_sections(anchor["user"])
        contexts = {}
        for state, (_, decision) in zip(BOARDS, (vacant, occupied), strict=True):
            _, board_text, _ = prompt_sections(messages[decision]["user"])
            contexts[state] = {"system": anchor["system"], "user": head + board_text + tail,
                               "other": other, "unit": unit, "destination": dest}
        matched.append(contexts)
        if len(matched) == 2:
            return matched
    raise ValueError("Expected matched board pairs from two independent games")


def comparison_packets(contexts, *, explicit_references=False):
    variants = {}
    for state in BOARDS:
        case = contexts[state]
        for wording, reports in WORDINGS.items():
            for direction in DIRECTIONS:
                report = reports[direction]
                if explicit_references:
                    unit = f"{case['other']}'s unit stationed at {case['unit']}"
                    report = report.replace("the unit", unit, 1)
                    report = re.sub(r"the (?:named|specified) destination", case["destination"], report)
                variants[f"{state}-{wording}-{direction}"] = packet(case, report)
    return variants


def run(args):
    from mlx_lm import load
    from mlx_lm.generate import batch_generate, wired_limit

    manifest = json.loads((args.run / "capture-mlx/capture-manifest.json").read_text())
    for field, filename in (("index", "model.safetensors.index.json"), ("config", "config.json")):
        if file_hash(args.model / filename) != manifest[f"model_{field}_sha256"]:
            raise ValueError("Forecast checkpoint differs from the saved replay")
    pairs = [(i, comparison_packets(contexts, explicit_references=args.explicit_pair is not None))
             for i, contexts in enumerate(matched_boards(args.run, args.games), 1)
             if args.explicit_pair is None or args.explicit_pair == i]
    os.umask(0o077)
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"model": manifest["model_index_sha256"], "limit": TOKEN_LIMIT,
               "decode": "greedy, thinking disabled",
               "input_sha256": hashlib.sha256(json.dumps(pairs, sort_keys=True).encode()).hexdigest()}
    plan_path = args.out / "plan.json"
    if plan_path.exists() and json.loads(plan_path.read_text()) != receipt:
        raise ValueError("Existing results use a different forecast plan")
    write_json(plan_path, receipt)

    jobs = [(i, state, {arm: messages for arm, messages in pair.items() if arm.startswith(state + "-")})
            for i, pair in pairs for state in BOARDS]
    pending = [(i, state, variants) for i, state, variants in jobs
               if not (args.out / f"pair-{i}-{state}.json").exists()]
    if pending:
        model, tokenizer = load(str(args.model))
        with wired_limit(model):
            for i, state, variants in pending:
                prompts = [tokenizer.apply_chat_template(messages, add_generation_prompt=True, enable_thinking=False)
                           for messages in variants.values()]
                result = batch_generate(model, tokenizer, prompts, max_tokens=TOKEN_LIMIT, prefill_step_size=512,
                                        prefill_batch_size=4, completion_batch_size=4)
                write_json(args.out / f"pair-{i}-{state}.json", {
                    arm: {"response": text, "probability": parse_probability(text)}
                    for arm, text in zip(variants, result.texts, strict=True)
                })
                print(f"Saved forecasts for pair {i}, {state} target", flush=True)
    summary = []
    for i, state, variants in jobs:
        saved = json.loads((args.out / f"pair-{i}-{state}.json").read_text())
        if saved.keys() != variants.keys():
            raise ValueError("Saved arms do not match the comparison plan")
        summary.append({"pair": i, "target": state,
                        **{arm.removeprefix(state + "-"): row["probability"] for arm, row in saved.items()}})
    write_json(args.out / "summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "games", "model", "out"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    parser.add_argument("--explicit-pair", type=int, choices=(1, 2),
                        help="Rerun one pair with the player, unit location and destination named in the report")
    run(parser.parse_args())
