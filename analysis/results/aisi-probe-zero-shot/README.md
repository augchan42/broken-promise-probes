# Zero-shot test of the AISI Apollo probe on Qwen3.5-27B promise breaches

Scored once on 11 Nov 2026 under the protocol frozen in commit `f781168` (protocol, [ADR-004](../../../docs/adr/004-external-detectors-and-model-choice.md)). This is exploratory. It does not change the [held-out transfer verdict](../held-out-transfer/README.md).

**Reading: inconclusive.** The primary endpoint did not reach p < 0.05 in either set.

## Probe and activations

- **Probe:** `ai-safety-institute/apollo-qwen-qwen3.5-27b` at `a51e6fe`, primary checkpoint `l_32_ar_dim`, raw score = activation · direction.
- **Activations:** saved token IDs replayed on the M2 Max with MLX 0.32.4 / mlx_lm 0.32.2 in bf16, using `mlx-community/Qwen3.5-27B-bf16` at `5ad6b65`, with chunked prefill (1,024 tokens). Post-block residuals are averaged in float32 over each token set. All 196 cases were captured, none was dropped from any token set, and no case needed a retry.
- **Hashes:** in `score.json` under `inputs`; the capture settings are in `capture-manifest.json`.

## Primary endpoint: message field, block 31

Mean per-game AUROC. The p-value is one-sided, from 10,000 within-game permutations.

| Set | Cases | Breaches | Games | Mean AUROC | Per-game AUROC | p | Leave-one-game-out range |
|---|---|---|---|---|---|---|---|
| Development | 90 | 15 | 4 | 0.633 | 0.41, 0.73, 0.70, 0.70 | 0.066 | 0.60–0.71 |
| Held-out | 106 | 10 | 5 | 0.645 | 0.38, 0.42, 0.94, 0.75, 0.73 | 0.116 | 0.57–0.69 |

## Secondary measures (these do not change the reading)

**Catches** (top quarter per game), compared with the text and board baseline:

| Set | Probe | Baseline | Baseline + score |
|---|---|---|---|
| Development | 6 of 15 | 6 of 15 | 7 of 15 |
| Held-out | 4 of 10 | 5 of 10 | 7 of 10 |

The baseline plus the probe score has a mean AUROC of 0.630 on development (baseline alone 0.615) and 0.751 on held-out (baseline alone 0.709). That baseline does not see the answer text, so beating it does not show the probe adds information.

**Stored threshold (−4.035):** no case is flagged in either set: 0 of 25 breaches and 0 of 171 kept promises. Every raw score falls below the Alpaca-calibrated threshold.

**Other token sets and the other block index** (mean AUROC, p):

| Token set @ block | Development | Held-out |
|---|---|---|
| message @ 32 | 0.660, p = 0.031 | 0.719, p = 0.029 |
| reasoning @ 31 | 0.462, p = 0.66 | 0.537, p = 0.39 |
| reasoning @ 32 | 0.482, p = 0.57 | 0.552, p = 0.34 |
| full answer @ 31 | 0.571, p = 0.21 | 0.590, p = 0.23 |
| full answer @ 32 | 0.565, p = 0.23 | 0.639, p = 0.13 |
| thinking @ 31 | 0.580, p = 0.19 | 0.706, p = 0.040 |
| thinking @ 32 | 0.566, p = 0.23 | 0.683, p = 0.062 |

- The message field at block 32 is below 0.05 in both sets. The protocol made block 32 a secondary indexing check that "cannot rescue the primary result", so this is reported only.
- It does raise the question of whether AISI's layer 32 means the output of block 32, not block 31. That training convention is still unverified.
- Seven secondary comparisons per set are uncorrected.

**Length:** the message length alone gives a mean AUROC of 0.30 on development and 0.32 on held-out, so breach messages tend to be shorter. Within-game Spearman correlations between the score and the message length are −0.27 on development and +0.17 on held-out. So the score doesn't simply track length in the same direction in both sets.

**Other layers (exploratory):** the highest mean AUROCs come from thinking-token readouts: L50 at block 49 (0.718) on development, and L13 at block 13 (0.731) on held-out. No layer is consistently highest in both sets. The full grid is in `score.json`.

## What this does and does not show

- It does not replicate the probe zero-shot on this task at the pre-registered readout. With 15 and 10 breaches, and three held-out games holding one breach each, the test has low power. A miss does not show that the activations lack a deception signal.
- The direction of the effect is above 0.5 in 6 of 9 games at the primary readout. The stored threshold is far too high for game text.
- The p-values assume cases within a game are exchangeable. They are not evidence of generalization across games.

## Files

- `score.json`: all aggregates.
- `capture-manifest.json`: capture settings and hashes.
- **Private** (not in git): case-level scores in `~/tara-runs/aisi-probe/scores-private.json` and pooled activations in `~/tara-runs/aisi-probe/capture/`. Both are mirrored to R2 a private bucket with SHA256SUMS.
