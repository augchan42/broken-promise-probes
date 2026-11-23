# Does the same situation always end the same way?

> **Public copy.** This folder is copied from the private working repository, which holds the game data. The script `resample.py` is not included because it imports modules that are only there. `score.json` holds counts only.

Exploratory, run 18 and 19 November 2026. The verdict on the first test stays **fail**. The protocol (`protocol.md`) and the script (`resample.py`) were committed and pushed before any sample was generated.

## What was done

12 of the 185 scored promises were drawn with the fixed seed: 6 that were broken and 6 that were kept. For each, Qwen3.5-27B was given the exact saved order prompt again, five times, with sampling seeds 1 to 5. The model, the settings and the prompt were the same each time; only the seed changed. Each answer was scored with the first test's breach rule.

Generation ran on the Mac with MLX, from 12:05 HKT on 18 November to 15:39 HKT on 19 November: 60 samples, about 28 minutes each, with no errors or retries.

## Result

| Original outcome | Cases | Breached in resamples | Pattern |
| --- | --- | --- | --- |
| Broken | 6 | 17 of 30 | 4 mixed, 1 always broken, 1 always kept |
| Kept | 6 | 0 of 29 valid | all always kept |

Breaches in five samples, per originally broken case: 0, 2, 3, 3, 4, 5.

One sample of a kept case gave invalid orders. It is not counted as a breach or a keep. Four samples reached the 8,192-token reasoning limit and were closed with the forced closing text. All four gave valid orders. The invalid sample was not one of them.

## What it shows

- **For promises that were broken, the outcome is mostly not fixed by the order prompt.** Four of six gave both outcomes from the same prompt. Over all 30 samples they breached 17 times. One case never breached again in five tries.
- **For promises that were kept, no resample broke the promise.** 29 valid samples, no breach.
- **The Mac replay does not disagree in one direction.** Kept cases stayed kept, and broken cases breached about half the time. So the protocol's third reading (the replay does not reproduce the original generation) does not apply.

Read against the protocol: the outcome varies within a fixed situation for most broken promises. A test of whether something in the order call, its reasoning or its activations, predicts which way a fixed prompt goes is worth designing. At the same time, the situation clearly matters: no kept case broke, and broken cases broke about half the time. A probe at promise time can pick up that difference in situation without reading any plan.

## Limits

- 12 cases and five samples each. A kept case that breaks one time in ten would usually show no breach here.
- The original games ran with vLLM on a GPU. The Mac replay uses the same checkpoint and settings, and different random draws.
- This resamples the order call only. The promise and everything before it are fixed by the saved prompt.
- The same seed numbers were used for every case, and each sample's answer seed equals the next sample's reasoning seed. The prompts differ, so the draws differ, but samples are not strictly independent across cases.
- **Replay bug on the reasoning-limit path** (found in PR #53). When reasoning reaches 8,192 tokens, the generation loop has already fed the last token into the model, and the answer step feeds it again before the forced closing text. This affects the four samples that hit the limit: two from broken cases (one breached, one kept) and two from kept cases (both kept). Without those four, broken cases breached in 16 of 28 samples, kept cases in 0 of 27 valid ones, and the patterns are unchanged: 4 mixed, 1 always broken, 1 always kept, 6 always kept. The four answers have not been regenerated.
- A varying outcome does not show a plan. A fixed outcome does not show its absence earlier in the round.

## Files

- `protocol.md`, written before generation.
- `resample.py`: `check`, `run` and `score`.
- `score.json`: counts only. No case IDs, prompts or generated text. The samples stay in private storage under `~/tara-runs/order-resample-2026-11-18/`.
