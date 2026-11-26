---
scope: range main..analysis/before-after-reasoning
diff: git diff main..analysis/before-after-reasoning
files_changed: 4
lines_changed: 391
lanes: correctness, protocol-fidelity, leakage, chance-line, reporting, simplification
reviewer: "codex-cli (GPT-6)"
reviewed_at: 2026-11-18T03:25:05Z
---

## Findings

### [medium] The shuffle range does not establish little signal or baseline dependence
**Where:** `analysis/exploratory/2026-11-18-before-after-reasoning/README.md:25` · **Lane:** chance-line

The conclusion that “the activation alone carries little” and “the earlier gain depended on the baseline” exceeds what these results establish. The script correctly implements the protocol’s training-label shuffles and refits. Assuming labels are exchangeable within development games, this supplies a conditional randomization reference for the fitted probe’s evaluation AUROC. Falling inside its central 95% range does not establish negligible predictive information or dependence on another model’s baseline. No baseline comparison or interaction is measured here.

This interpretive error is inherited from `protocol.md:43`, rather than an implementation deviation. Replace the conclusion with the supported observation: neither readout exceeds its shuffled-training-label 97.5th percentile. Qualify line 29 similarly, and explicitly correct the protocol’s interpretation without changing the recorded protocol.

### [low] The single-breach limitation understates how many games are affected
**Where:** `analysis/exploratory/2026-11-18-before-after-reasoning/README.md:33` · **Lane:** reporting

The sentence describes one single-breach game and an AUROC step of about 0.06. The JSON contains four such games, with 19, 22, 24 and 12 cases. Without ties, their AUROC increments are respectively 1/18, 1/21, 1/23 and 1/11: approximately 0.056, 0.048, 0.043 and 0.091. This limitation affects half the games contributing equally to mean AUROC. Replace the sentence with: “Four games have a single breach; their AUROC increments range from about 0.043 to 0.091 without ties.”

## Verification limitations

Review comprised the requested diff, repository dependencies and independent arithmetic checks on the committed aggregates. All table values, rounding, paired differences, catch totals and game win/loss counts agree with `score.json`.

Static inspection found correct cutoff and block axes, development-only normalization and fitting, disjoint-game checks, pair weighting, catch allocation and paired whole-game bootstrap logic. No scoring implementation deviation from the protocol was identified.

No private data was accessed, scoring script executed or file modified. Consequently, capture provenance, actual token boundaries, case-level rankings, shuffle quantiles and the seeded bootstrap interval were not independently reproduced. The aggregate JSON cannot establish the background claims about dispositions or the timing of later order-writing calls.

## Verdict

needs revision

## Disposition

- [medium] The shuffle range does not establish little signal or baseline dependence — ACCEPTED. The result note now states only that neither readout exceeded its shuffled-label 97.5th percentile. The protocol has a dated correction note and its original text is unchanged.
- [low] The single-breach limitation understates how many games are affected — ACCEPTED. The limit now says four games have a single breach, with steps of about 0.04 to 0.09.

