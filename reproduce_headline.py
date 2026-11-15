"""Reproduce the eight-game result from the numbers-only score table.

Usage: python reproduce_headline.py [data/eight-game-score-table.npz]

Needs only numpy. The table holds labels, anonymous game numbers, kernel matrices for the
text and board features and the monitor, and the block 31 activation for each promise.
It holds no game text.
"""

import sys

import numpy as np

C = 1.0
SEED = 20261112
TIE_TOLERANCE = 1e-10


def fit_logistic(gram, y, c):
    """L2 logistic regression in the span of the training rows, with a free intercept."""
    values, vectors = np.linalg.eigh((gram + gram.T) * 0.5)
    keep = values > max(1.0, float(values[-1])) * 1e-12
    basis, roots = vectors[:, keep], np.sqrt(values[keep])
    design = np.column_stack((basis * roots, np.ones(len(y))))
    penalty = np.full(design.shape[1], 1 / c)
    penalty[-1] = 0
    weights = np.zeros(design.shape[1])
    weights[-1] = np.log(y.mean() / (1 - y.mean()))

    def objective(w):
        logits = design @ w
        return (np.logaddexp(0, logits) - y * logits).sum() + (penalty * w**2).sum() / 2

    for _ in range(100):
        probability = 1 / (1 + np.exp(-np.clip(design @ weights, -700, 700)))
        gradient = design.T @ (probability - y) + penalty * weights
        if np.linalg.norm(gradient, ord=np.inf) < 1e-8:
            return basis @ (weights[:-1] / roots), float(weights[-1])
        curvature = probability * (1 - probability)
        step = np.linalg.solve((design.T * curvature) @ design + np.diag(penalty), gradient)
        previous, scale = objective(weights), 1.0
        while objective(weights - scale * step) > previous + 1e-13 and scale > 1e-8:
            scale /= 2
        weights -= scale * step
    raise ValueError("The logistic fit did not converge")


def predict(gram, y):
    dual, intercept = fit_logistic(gram[0], y, C)
    return gram[1] @ dual + intercept


def auroc(scores, labels):
    positives, negatives = scores[labels == 1], scores[labels == 0]
    if not len(positives) or not len(negatives):
        return None
    diff = positives[:, None] - negatives
    tie = np.isclose(diff, 0, atol=1e-10, rtol=0)
    return float(np.mean((diff > 0) & ~tie) + np.mean(tie) / 2)


def review_weights(scores):
    """Review the top quarter of a game's promises, rounding up. Ties share the last slots."""
    budget = (len(scores) + 3) // 4
    boundary = np.sort(scores)[-budget]
    tied = np.abs(scores - boundary) <= TIE_TOLERANCE
    above = scores > boundary + TIE_TOLERANCE
    return above.astype(float) + tied * ((budget - above.sum()) / tied.sum())


def per_game(scores, labels, games):
    rows = []
    for game in sorted(set(games)):
        index = games == game
        y = labels[index]
        rows.append({"game": int(game), "cases": int(index.sum()), "breaches": int(y.sum()),
                     "auroc": auroc(scores[index], y),
                     "catches": float(review_weights(scores[index]) @ y)})
    return rows


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def block_kernel(train, test):
    """Standardise each of the 5,120 numbers on the development cases, then take dot products."""
    train, test = train.astype(float), test.astype(float)
    mean, scale = train.mean(axis=0), train.std(axis=0)
    scale = np.where(scale > 0, scale, 1) * np.sqrt(train.shape[-1])
    a, b = (train - mean) / scale, (test - mean) / scale
    return a @ a.T, b @ a.T


def main(path):
    t = np.load(path)
    dev_y, dev_game = t["dev_breach"].astype(float), t["dev_game"]
    test_y, test_game = t["test_breach"].astype(float), t["test_game"]
    baseline = add((t["text_board_train"], t["text_board_cross"]), (t["monitor_train"], t["monitor_cross"]))
    block31 = block_kernel(t["dev_block31"], t["test_block31"])
    assert np.allclose(block31[0], t["block31_train"]) and np.allclose(block31[1], t["block31_cross"])
    probe = add(baseline, block31)

    base_rows = per_game(predict(baseline, dev_y), test_y, test_game)
    probe_rows = per_game(predict(probe, dev_y), test_y, test_game)
    print(f"{len(test_y)} promises, {int(test_y.sum())} breaches, fitted on {len(dev_y)} development promises\n")
    print("game  promises  breaches  baseline AUROC  +block 31 AUROC  baseline caught  +block 31 caught")
    for a, b in zip(base_rows, probe_rows):
        print(f"{a['game']:>4}  {a['cases']:>8}  {a['breaches']:>8}  {a['auroc']:>14.3f}  {b['auroc']:>15.3f}"
              f"  {a['catches']:>15.2f}  {b['catches']:>16.2f}")
    deltas = [b["auroc"] - a["auroc"] for a, b in zip(base_rows, probe_rows)]
    base_auc = np.mean([r["auroc"] for r in base_rows])
    probe_auc = np.mean([r["auroc"] for r in probe_rows])
    base_catch = sum(r["catches"] for r in base_rows)
    probe_catch = sum(r["catches"] for r in probe_rows)
    rng = np.random.default_rng(SEED)
    low, high = np.quantile(rng.choice(deltas, (10_000, len(deltas)), replace=True).mean(axis=1), [0.025, 0.975])

    rng = np.random.default_rng(SEED)
    null = []
    for _ in range(1_000):
        shuffled = dev_y.copy()
        for game in sorted(set(dev_game)):
            index = dev_game == game
            shuffled[index] = rng.permutation(dev_y[index])
        null.append(sum(r["catches"] for r in per_game(predict(probe, shuffled), test_y, test_game))
                    - sum(r["catches"] for r in per_game(predict(baseline, shuffled), test_y, test_game)))
    threshold = float(np.quantile(null, 0.95))

    gain, extra = float(np.mean(deltas)), probe_catch - base_catch
    print(f"\nMean AUROC across games: baseline {base_auc:.3f}, with block 31 {probe_auc:.3f}")
    print(f"Gain {gain:+.3f}, 95% bootstrap interval over games {low:+.3f} to {high:+.3f}. The rule required +0.050.")
    print(f"Breaches caught: baseline {base_catch:.0f}, with block 31 {probe_catch:.0f}. Extra catches {extra:.0f}.")
    print(f"The rule required at least 2 extra catches and more than the shuffle threshold of {threshold:.0f}.")
    checks = [gain >= 0.05 - 1e-12, extra >= 2 - 1e-12, extra > threshold + 1e-12]
    print("Verdict:", "pass" if all(checks) else "fail")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/eight-game-score-table.npz")
