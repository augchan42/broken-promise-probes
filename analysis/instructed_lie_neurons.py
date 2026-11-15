"""Look for individual MLP responses to the synthetic instructed-lie contrast."""

import argparse
import json
import os
from pathlib import Path
import time

import numpy as np

from analysis.instructed_lie_transfer import assess_synthetic, read, write_json
from gpu.capture_promise_probe import CUTOFFS, file_hash, token_hash


def capture_segment(text, mx, ids, picks, caches, last_block, every, all_tokens=False):
    from mlx_lm.models.qwen3_5 import create_attention_mask, create_ssm_mask
    from mlx_lm.models.qwen3_next import swiglu

    hidden = text.embed_tokens(mx.array([ids]))
    layers = text.layers[:last_block + 1]
    fa_index = next((i for i, layer in enumerate(layers) if not layer.is_linear), None)
    ssm_index = next((i for i, layer in enumerate(layers) if layer.is_linear), None)
    fa = create_attention_mask(hidden, caches[fa_index]) if fa_index is not None else None
    ssm = create_ssm_mask(hidden, caches[ssm_index]) if ssm_index is not None else None
    rows = []
    for block, (layer, cache) in enumerate(zip(layers, caches, strict=True)):
        mask = ssm if layer.is_linear else fa
        if block in picks:
            attention = layer.linear_attn if layer.is_linear else layer.self_attn
            skip = hidden + attention(layer.input_layernorm(hidden), mask, cache)
            mlp = layer.mlp
            inputs = layer.post_attention_layernorm(skip)
            neurons = swiglu(mlp.gate_proj(inputs), mlp.up_proj(inputs))
            if every == 1:
                mx.eval(skip, neurons)
            hidden = skip + mlp.down_proj(neurons)
            mx.eval(hidden, neurons, cache.state if cache is not None else [])
            position = slice(None) if all_tokens else -1
            rows.append((np.array(neurons[0, position, picks[block]].astype(mx.float32)),
                         np.array(hidden[0, -1].astype(mx.float32))))
        else:
            hidden = layer(hidden, mask=mask, cache=cache)
            if (block + 1) % every == 0:
                mx.eval(hidden, cache.state if cache is not None else [])
    return rows


def capture(text, mx, ids, picks, every=4, all_tokens=False):
    last = max(picks)
    return capture_segment(text, mx, ids, picks, [None] * (last + 1), last, every, all_tokens)


def capture_chunked(text, mx, ids, picks, size=512):
    from mlx_lm.models.cache import ArraysCache, KVCache

    last = max(picks)
    caches = [ArraysCache(size=2) if layer.is_linear else KVCache() for layer in text.layers[:last + 1]]
    for start in range(0, len(ids), size):
        end = min(start + size, len(ids))
        rows = capture_segment(text, mx, ids[start:end], picks if end == len(ids) else {},
                               caches, last, every=1)
    return rows


def synth(model, tokenizer, mx, out):
    _, summary = assess_synthetic(out)
    controls = read(out / "length-control-score.json")
    families = summary["families"] + [c["responses"] for c in controls]
    picks = dict.fromkeys(range(64), slice(None))
    arrays = []
    for i, family in enumerate(families):
        conditions = []
        for j, row in enumerate(family):
            path = out / f"neurons-{i}-{j}.npy"
            ids = tokenizer.apply_chat_template([{"role": "user", "content": row["prompt"]}],
                                                add_generation_prompt=True, enable_thinking=False)
            if len(ids) != row["tokens"] or ("sha256" in row and token_hash(ids) != row["sha256"]):
                raise ValueError("Prompt differs from original synthetic capture")
            if not path.exists():
                values, residual = map(np.stack, zip(*capture(model.language_model.model, mx, ids, picks)))
                if i < len(summary["families"]):
                    expected = np.load(out / f"family-{i}-{j}.npy", allow_pickle=False)
                    np.testing.assert_array_equal(residual, expected)
                tmp = path.with_suffix(".tmp.npy")
                np.save(tmp, values, allow_pickle=False)
                tmp.replace(path)
            conditions.append(np.load(path, allow_pickle=False))
        arrays.append(conditions)
        print(f"Verified neuron capture for synthetic family {i + 1}/{len(families)}", flush=True)
    x = np.asarray(arrays)
    if x.shape != (7, 4, 64, 17408) or not np.isfinite(x).all():
        raise ValueError("Unexpected neuron capture")

    def pairs(indices):
        differences = []
        for i in indices:
            family = families[i]
            for answer in ("yes", "no"):
                matched = {row["instructed_lie"]: j for j, row in enumerate(family)
                           if row["correct"] and row["answer"].casefold() == answer}
                if len(matched) == 2:
                    differences.append(x[i, matched[1]] - x[i, matched[0]])
        return np.stack(differences)

    discovery = pairs(range(3))
    held = pairs(range(3, 5))
    matched = pairs(range(5, 7))
    signed = np.sign(discovery.mean(axis=0))
    # Rank by the smallest same-answer gap over discovery pairs. Use each neuron's
    # within-family variation as its scale, with a floor against tiny fluctuations.
    centered = x[:3] - x[:3].mean(axis=1, keepdims=True)
    scale = np.maximum(np.sqrt(np.mean(centered ** 2, axis=(0, 1))), 0.01)
    rank = (discovery * signed).min(axis=0) / scale
    order = np.argsort(-rank.ravel(), kind="stable")[:3]
    candidates = []
    for index in order:
        block, neuron = map(int, np.unravel_index(index, rank.shape))
        sign = int(signed[block, neuron])
        candidates.append({"block": block, "neuron": neuron, "sign": sign,
                           "discovery_wins": int((discovery[:, block, neuron] * sign > 0).sum()),
                           "held_wins": int((held[:, block, neuron] * sign > 0).sum()),
                           "matched_wins": int((matched[:, block, neuron] * sign > 0).sum())})
    result = {"discovery_pairs": len(discovery), "held_pairs": len(held), "matched_pairs": len(matched),
              "length_matched_board_families": len(controls),
              "length_matched_behaviors_correct": sum(r["correct"] for c in controls for r in c["responses"]),
              "searched_neurons": int(rank.size), "candidates": candidates}
    write_json(out / "neuron-synthetic-score.json", result)
    print(json.dumps(result), flush=True)
    return result


def games(model, mx, out, run, result):
    from analysis.score_eight_game_reasoning import read as read_score

    candidates = [row for row in result["candidates"]
                  if row["held_wins"] == result["held_pairs"] and row["matched_wins"] == result["matched_pairs"]]
    if not candidates:
        print("None of the three candidates cleared both synthetic checks.", flush=True)
        return
    # One pair per game, chosen by decision ID before reading any game activation.
    frozen_path = run / "one-time-score/score.json"
    saved_path = frozen_path.with_name("scores-private.json")
    hashes = [file_hash(path) for path in (frozen_path, saved_path)]
    frozen = read_score(frozen_path)
    folder = run / "capture-mlx"
    manifest_path = folder / "capture-manifest.json"
    manifest = read(manifest_path)
    if file_hash(manifest_path) != frozen["capture"]["manifest_sha256"]:
        raise ValueError("Game capture differs from frozen score")
    prefixes = read(folder / "prefixes.json")
    staged = run / "handoff/scoring-inputs/eight-game-reasoning/staged"
    stage_path = staged / "stage-manifest.json"
    records_path = staged / "records.json"
    if (file_hash(stage_path) != frozen["receipts"]["stage"]
            or file_hash(records_path) != read(stage_path)["records_sha256"]):
        raise ValueError("Game stage differs from frozen score")
    records = read(records_path)
    saved = read_score(saved_path)
    if not manifest["decisions"] == [row["decision_id"] for row in prefixes] == [
        row["decision_id"] for row in records
    ] == [row["decision_id"] for row in saved]:
        raise ValueError("Game case order differs")
    if (len(saved), sum(row["breach"] for row in saved)) != (185, 23):
        raise ValueError("Unexpected game counts")
    by_game = {}
    for i in sorted(range(len(saved)), key=lambda i: saved[i]["decision_id"]):
        by_game.setdefault(records[i]["game"], {}).setdefault(saved[i]["breach"], i)
    game_ids = read(stage_path)["games"]
    if len(game_ids) != 8 or set(by_game) != set(game_ids):
        raise ValueError("Unexpected game groups")
    for row in candidates:
        row["by_game"] = []
    picks = {}
    for row in candidates:
        picks.setdefault(row["block"], []).append(row["neuron"])
    picks = dict(sorted(picks.items()))
    for number, game in enumerate(game_ids, 1):
        scores = []
        for label in (0, 1):
            i = by_game[game][label]
            prefix = prefixes[i]
            ids = prefix["token_ids"]
            if token_hash(ids) != prefix["prefix_token_ids_sha256"] or len(ids) != prefix["cutoffs"]["reasoning_end"]:
                raise ValueError("Incorrect game replay tokens")
            checkpoint = out / f"game-{number}-{label}.json"
            if not checkpoint.exists():
                for attempt in range(3):
                    try:
                        observed = capture_chunked(model.language_model.model, mx, ids, picks, size=512)
                        break
                    except RuntimeError:
                        if attempt == 2:
                            raise
                        mx.clear_cache()
                        time.sleep(3)
                original = np.load(folder / "parts" / f"{prefix['decision_id']}.npy", allow_pickle=False)
                values = {"relative_block_errors": []}
                for (block, neurons), (neur, residual) in zip(picks.items(), observed, strict=True):
                    expected = original[CUTOFFS.index("reasoning_end"), block]
                    error = float(np.linalg.norm(residual - expected) / np.linalg.norm(expected))
                    if not np.isfinite(error) or not np.isfinite(neur).all():
                        raise ValueError("Invalid chunked game replay")
                    values["relative_block_errors"].append(error)
                    values[str(block)] = dict(zip(map(str, neurons), map(float, neur), strict=True))
                write_json(checkpoint, values)
            scores.append(read(checkpoint))
        for row in candidates:
            b, n = str(row["block"]), str(row["neuron"])
            difference = (scores[1][b][n] - scores[0][b][n]) * row["sign"]
            row["by_game"].append(int(np.sign(difference)))
        print(f"Verified neuron transfer sample {number}/8", flush=True)
    if hashes != [file_hash(path) for path in (frozen_path, saved_path)]:
        raise ValueError("Frozen results changed")
    error = [value for number in range(1, 9) for label in (0, 1)
             for value in read(out / f"game-{number}-{label}.json").get("relative_block_errors", [])]
    write_json(out / "neuron-transfer-score.json", {"pairs": 8, "selection": "first decision ID per outcome per game",
                                                   "chunked_cases": len(error) // len(picks),
                                                   "max_chunked_relative_block_error": max(error, default=0.0),
                                                   "frozen_verdict": frozen["primary"]["verdict"],
                                                   "frozen_score_sha256": hashes[0], "candidates": candidates})


if __name__ == "__main__":
    from mlx_lm import load
    from mlx_lm.generate import wired_limit
    import mlx.core as mx

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("model", "run", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--viewer", type=Path, help="Export synthetic token traces to this standalone HTML file")
    parser.add_argument("--measure-writes", action="store_true",
                        help="Include measured effects of removing synthetic neuron firings in the viewer")
    args = parser.parse_args()
    if args.measure_writes and not args.viewer:
        parser.error("--measure-writes requires --viewer")
    os.umask(0o077)
    hashes = read(args.out / "plan.json")["model"]
    for field, name in (("index", "model.safetensors.index.json"), ("config", "config.json")):
        if file_hash(args.model / name) != hashes[f"model_{field}_sha256"]:
            raise ValueError("Model differs from the saved synthetic capture")
    model, tokenizer = load(str(args.model))
    with wired_limit(model):
        if args.viewer:
            from tools.activation_viewer.instructed_lie import export

            export(model, tokenizer, mx, args.out, args.viewer, measure_writes=args.measure_writes)
        else:
            result = synth(model, tokenizer, mx, args.out)
            games(model, mx, args.out, args.run, result)
