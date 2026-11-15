"""Exploratory reasoning-end sweep using the frozen eight-game comparison inputs."""

import argparse
import json
from pathlib import Path

import numpy as np

BASELINE = "text_board_monitor"


def sweep(root, out):
    from analysis.backend_check import load_mlx_dev
    from analysis.development_intent_rescore import add_kernels, predict
    from analysis.development_layer_sweep import board_features, board_kernels
    from analysis.promise_probe_pilot import STRICT, keyed_rows
    from analysis.promise_probe_score import CUTOFFS, fit_text, kernels, normalize_residual, text_matrix
    from analysis.score_eight_game_reasoning import BLOCKS, freeze, per_game, read, write_once
    from analysis.text_monitor import _judge_kernel
    from portable.tara_inputs import sha256

    run = root / "eight-game-reasoning"
    handoff = run / "handoff/scoring-inputs"
    staged = handoff / "eight-game-reasoning/staged"
    audit = handoff / "eight-game-audit"
    judged = handoff / "eight-game-reasoning/judged"
    judge_receipt = judged.parent / "judge-receipt.json"
    capture = run / "capture-mlx"
    development = root / "development"
    frozen_path = run / "one-time-score/score.json"
    private_path = frozen_path.with_name("scores-private.json")
    frozen = read(frozen_path)
    saved = read(private_path)
    source_hashes = [sha256(path) for path in (frozen_path, private_path)]
    stage = read(staged / "stage-manifest.json")
    records_path = staged / "records.json"
    outcome_path = audit / "eligible-private.jsonl"
    dev_capture = development / "capture-mlx"
    receipts = {
        "stage": sha256(staged / "stage-manifest.json"),
        "development": sha256(development / "staged/records.json"),
        "development_capture": sha256(dev_capture / "capture-manifest.json"),
        "judges": sha256(judge_receipt),
        "outcomes": sha256(outcome_path),
    }
    if receipts != frozen["receipts"] or sha256(records_path) != stage["records_sha256"]:
        raise ValueError("Inputs differ from the frozen comparison")
    monitor = freeze(staged, judged, judge_receipt)["monitor"]
    outcomes = keyed_rows(outcome_path)
    records = read(records_path)
    eligible = {case for case, row in outcomes.items() if row["classification"] in STRICT
                and row["outcome"] in ("kept", "breached")}
    keep = [i for i, row in enumerate(records) if row["decision_id"] in eligible]
    test_records = [records[i] for i in keep]
    test_y = np.array([int(outcomes[row["decision_id"]]["outcome"] == "breached") for row in test_records])
    if ([row["decision_id"] for row in test_records] != [row["decision_id"] for row in saved]
            or not np.array_equal(test_y, [row["breach"] for row in saved])):
        raise ValueError("Scored cases or labels differ from the saved comparison")

    _, dev_records, dev_res = load_mlx_dev(development / "staged", dev_capture)
    capture_path = capture / "capture-manifest.json"
    manifest = read(capture_path)
    if (sha256(capture_path) != frozen["capture"]["manifest_sha256"]
            or sha256(capture / "residuals.npz") != manifest["residuals_sha256"]
            or manifest["decisions"] != [row["decision_id"] for row in records]):
        raise ValueError("Capture differs from the frozen comparison")
    position = CUTOFFS.index("reasoning_end")
    with np.load(capture / "residuals.npz", allow_pickle=False) as archive:
        test_res = archive["residuals"][keep, position]
    if test_res.shape != (len(saved), 64, 5120) or not np.isfinite(test_res).all():
        raise ValueError("Invalid reasoning-end capture")

    y = np.array([row["label"] for row in dev_records])
    rows = dev_records + test_records
    train, test = np.arange(len(y)), np.arange(len(y), len(rows))
    text_rows = [(dict(diplomacy=r["diplomacy"], recipient=r["sender"]), r, None) for r in rows]
    spec = fit_text(text_rows[:len(y)], "reasoning_end")
    text = kernels(text_matrix(text_rows[:len(y)], spec), text_matrix(text_rows[len(y):], spec))
    absolute, relative = zip(*(board_features(r["diplomacy"]["user_prompt"], r["sender"]) for r in rows))
    board = add_kernels(board_kernels(absolute, train, test), board_kernels(relative, train, test))
    dev_monitor = development / "text-monitor/judged/monitor"
    p = np.clip(
        [read(dev_monitor / f"{r['decision_id']}.json")["value"] for r in dev_records]
        + [monitor[r["decision_id"]] for r in test_records], 0.01, 0.99,
    )
    baseline = add_kernels(add_kernels(text, board), _judge_kernel(np.log(p / (1 - p)), train, test))
    games = stage["games"]
    test_groups = np.array([r["game"] for r in test_records])

    def verify(name, scores):
        expected = np.array([r["scores"][name] for r in saved])
        np.testing.assert_allclose(scores, expected, rtol=0, atol=1e-9)
        return float(np.max(np.abs(scores - expected)))

    baseline_scores = predict(baseline, y, train)
    parity = {BASELINE: verify(BASELINE, baseline_scores)}
    base_games, _ = per_game(baseline_scores, test_y, test_groups, games)
    blocks = []
    for block in range(64):
        x_train, x_test, _, _ = normalize_residual(
            dev_res[:, position, block].astype(float), test_res[:, block].astype(float),
        )
        scores = predict(add_kernels(baseline, kernels(x_train, x_test)), y, train)
        if block in BLOCKS:
            name = f"{BASELINE}_block{block}"
            parity[name] = verify(name, scores)
        rows, _ = per_game(scores, test_y, test_groups, games)
        auc_delta = np.array([r["auroc"] - b["auroc"] for r, b in zip(rows, base_games, strict=True)])
        catch_delta = np.array([r["catches"] - b["catches"] for r, b in zip(rows, base_games, strict=True)])
        blocks.append({
            "block": block, "mean_auroc_gain": float(auc_delta.mean()),
            "extra_catches": float(catch_delta.sum()),
            "game_auroc_gains": auc_delta.tolist(), "game_extra_catches": catch_delta.tolist(),
            "games_with_auroc_gain": int(np.count_nonzero(auc_delta > 1e-12)),
            "games_with_more_catches": int(np.count_nonzero(catch_delta > 1e-12)),
            "leave_one_game_out_mean_gain_range": [
                float(f(auc_delta.sum() - auc_delta) / (len(games) - 1)) for f in (min, max)
            ],
        })
    if source_hashes != [sha256(path) for path in (frozen_path, private_path)]:
        raise ValueError("Frozen score files changed during the sweep")
    write_once(out, {
        "exploratory": True, "cutoff": "reasoning_end", "frozen_score_sha256": source_hashes[0],
        "frozen_verdict": frozen["primary"]["verdict"], "reference_max_abs_score_differences": parity,
        "development_cases": len(y), "cases": len(test_y), "breaches": int(test_y.sum()),
        "baseline": {k: frozen["models"][BASELINE][k] for k in ("mean_auroc", "catches", "slots")},
        "games": [{k: row[k] for k in ("cases", "breaches", "auroc", "catches", "slots")} for row in base_games],
        "blocks": blocks,
    })


def plot(path, out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    result = json.loads(path.read_text())
    rows = result["blocks"]
    x = [r["block"] for r in rows]
    auc = [r["mean_auroc_gain"] for r in rows]
    catches = [r["extra_catches"] for r in rows]
    fig, axes = plt.subplots(3, 1, figsize=(12, 8.8), sharex=True, layout="constrained")
    fig.suptitle("Exploratory reasoning-end sweep on eight games", fontsize=17, weight="bold")
    for ax in axes[:2]:
        ax.axhline(0, color="#64748b", linewidth=0.8)
        ax.grid(axis="y", alpha=0.18)
        for block in (2, 24, 31):
            ax.axvline(block, color="#64748b", alpha=0.25, linestyle=":")
    axes[0].plot(x, auc, color="#245c91", marker=".", linewidth=1.5)
    axes[0].axhline(0.05, color="#9a3412", linestyle="--", linewidth=1, label="Original AUROC margin")
    axes[0].legend(loc="lower right", frameon=False)
    axes[0].set_ylabel("Mean per-game\nAUROC gain")
    axes[1].bar(x, catches, color=["#087f68" if n > 0 else "#b45a51" for n in catches], width=0.82)
    axes[1].set_ylabel("Extra breaches caught\n(49 review slots)")
    by_game = np.array([r["game_auroc_gains"] for r in rows]).T
    limit = np.abs(by_game).max()
    heat = axes[2].imshow(by_game, aspect="auto", cmap="RdBu",
                          norm=TwoSlopeNorm(vcenter=0, vmin=-limit, vmax=limit))
    axes[2].set_yticks(range(len(by_game)), [f"Game {i + 1}" for i in range(len(by_game))])
    axes[2].set_xticks([0, 2, 8, 16, 24, 31, 40, 48, 56, 63])
    axes[2].set_xlabel("Transformer block (zero-based)")
    fig.colorbar(heat, ax=axes, shrink=0.36, anchor=(0, 0), label="Per-game AUROC gain")
    fig.savefig(out, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    scoring = commands.add_parser("score")
    scoring.add_argument("--run-root", type=Path, required=True)
    scoring.add_argument("--out", type=Path, required=True)
    plotting = commands.add_parser("plot")
    plotting.add_argument("--score", type=Path, required=True)
    plotting.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "score":
        sweep(args.run_root, args.out)
    else:
        plot(args.score, args.out)
