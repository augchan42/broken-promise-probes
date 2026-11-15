# ADR-001 text monitor on the 90 development promise cases

Scored once on 11 Nov 2026 under the [frozen protocol](../../../docs/superpowers/plans/2026-11-11-text-monitor-development.md). This is exploratory and uses development games only.

**Judge:** `claude-opus-5-5`, run through the `claude` CLI with an empty context. It read the agent's prompt, its reasoning to the end of thinking, and the promise message, but not the orders. All 90 cases were judged in both passes. Calls that failed under concurrency were retried and none is missing.

## Results

| Model | Mean per-game AUROC | Breaches caught in 24 reviews | Caught among the 13 breaches rated silent |
|---|---|---|---|
| Original baseline (text and board) | 0.615 | 6 of 15 | 5 |
| Enhanced baseline (+ blinded reasoning annotations) | 0.605 | 7 of 15 | 6 |
| Probe (enhanced + reasoning-end block 2) | 0.707 | 9 of 15 | 7 |
| **Judge alone** | **0.713** (p = 0.007) | 7.1 of 15 | 5.1 |
| Enhanced + judge | 0.713 | 8 of 15 | 6 |
| Probe + judge | 0.751 | 9 of 15 | 7 |

- The baseline and probe rows reproduce the intent re-score exactly.
- The p-value is one-sided, from 10,000 within-game permutations.
- Per-game AUROCs are in `score.json`.

**Explicitness** (how openly the reasoning states an intention to act against the recipient this round):

| Score | Breached | Kept |
|---|---|---|
| 1 (not considered) | 1 | 39 |
| 2 (vague or hypothetical) | 12 | 33 |
| 3 (live option, unsettled) | 2 | 3 |
| 4–5 (stated plan) | 0 | 0 |

## What this shows

1. **The reasoning before the message almost never states a plan to break the promise.** None of the 90 traces was rated 4 or 5. 13 of the 15 breaches are in the silent subset (1–2), which holds 85 of the 90 cases. Under ADR-001's design, the "silent" headline subset is nearly the whole dataset.
2. **A strong text judge does about as well as the probe on ranking and slightly worse on catches.** AUROC is 0.713 for the judge and 0.707 for the probe, with 7.1 against 9 catches. Under the frozen reading rules, the judge does not catch clearly more breaches than the probe. Its p-value is the first development result below 0.01 that needed no layer selection.
3. **The probe and the judge partly add up.** Together they reach AUROC 0.751, against 0.707 and 0.713 separately. Catches stay at 9, and a gain of one or two catches is within noise with 15 breaches.
4. **The probe is favoured here**, because block 2 was selected on these games and the judge was not tuned. The held-out result for that probe was 5 of 10, the same as the baseline (ADR-004). At mid-depth block 31 the probe adds nothing (see below), so readings 2 and 3 depend on that selection.

Reading 1 fits study R1's hypothesis: many breaches may be decided at order time, after the message, rather than planned when the promise is written.

## Added after scoring: the probe at mid-depth block 31

Block 2 is two blocks into 64. At the last token it mostly reflects the current token and the text near it, so it is a poor place to look for a plan. It was chosen only by its fit on these four games. The comparison was re-run with the probe at reasoning-end block 31, the mid-depth index fixed in advance for the AISI test. This is post hoc, and the judge outputs are unchanged.

| Model | Mean per-game AUROC | Catches |
|---|---|---|
| Enhanced baseline | 0.605 | 7 of 15 |
| Probe at block 31 | 0.607 | 7 of 15 |
| Judge alone | 0.713 | 7.1 of 15 |
| Probe at block 31 + judge | 0.713 | 9 of 15 |

At block 31 the activations add nothing to the baseline, and the judge ranks breaches better than either. The probe's apparent tie with the judge depended on the block 2 selection. In `score-block31-post-hoc.json` the probe rows keep the key `probe_reasoning_2`, but they use block 31 (`"probe_block": 31`).

## Files

- `score.json`: aggregates, per-game results and the explicitness table.
- `score-block31-post-hoc.json`: the same scoring with the probe at block 31.
- **Private** (not in git): `~/tara-runs/development/text-monitor/`, which holds the inputs, every judge answer with its reason, prompt hash and usage, and the logs.
- Reproduce with:

```sh
python -m analysis.text_monitor score --staged DEV/staged --capture DEV/capture \
  --review DEV/blinded-intent-review --judged DEV/text-monitor/judged --out score.json
```
