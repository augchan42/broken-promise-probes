# CUDA vs MLX backend check

Exploratory, run on 11 Nov 2026 after the [one-time held-out score](../held-out-transfer/README.md). It does not change that verdict. Full output: `backend-check.json`. Code: `analysis/backend_check.py`.

## Question

The held-out score trained on development activations captured on an A100 (CUDA) and scored held-out activations captured on the M2 Max (MLX). Could that mismatch explain why the probe did not pass?

## What was done

The 90 development cases were re-staged from the cap-21 archive. The records and prefixes matched the hashes of the A100 capture exactly (`497eab09…`, `ea4f41b4…`). The same token IDs were then replayed on the M2 Max with MLX, capturing all 64 layers at all three cutoffs.

## Results

**1. Activation distance.** Median relative L2 distance between the CUDA and MLX residuals across the 90 cases:

| Cutoff | Layer 2 | Layer 30 | Layer 63 | Largest single case, any layer |
|---|---:|---:|---:|---:|
| Prompt end | 0.19% | 2.0% | 4.7% | 6.0% |
| Reasoning half | 0.17% | 0.6% | 1.5% | 6.9% |
| Reasoning end | 0.19% | 1.1% | 2.6% | 4.8% |

The gap grows with depth, as bf16 rounding accumulates. At layer 2 it is under 0.2%.

**2. Development leave-one-game-out** (baseline vs baseline + reasoning-end layer 2):

| Activations | Baseline catches | Probe catches | Baseline mean AUROC | Probe mean AUROC |
|---|---:|---:|---:|---:|
| CUDA | 6 of 15 | 8 of 15 | 0.615 | 0.700 |
| MLX | 6 of 15 | 9 of 15 | 0.615 | 0.694 |

The CUDA row reproduces the published development numbers.

**3. Held-out score refit on MLX development activations**, so training and testing share a backend:

| Model | Catches (CUDA-trained, official) | Catches (MLX-trained) | Mean AUROC (official → MLX-trained) |
|---|---:|---:|---:|
| Baseline | 5 | 5 | 0.709 → 0.709 |
| Baseline + reasoning-end layer 2 | 5 | 5 | 0.658 → 0.658 |
| Baseline + prompt-end layer 63 | 4 | 4 | 0.706 → 0.716 |
| Enhanced baseline | 4 | 4 | 0.769 → 0.769 |
| Enhanced + layer 2 | 4 | 4 | 0.710 → 0.710 |

Every comparison still fails the pass rule, with the same per-game catch changes.

## Conclusion

The backend mismatch does not explain the held-out result. With training and testing on the same backend, the layer-2 probe gives the same catches and the same AUROC to three decimals. The deep layers move more between backends (up to about 5%), which shifts the prompt-end layer 63 control slightly, but not its catches.

## Private files

The MLX development activations are in the private R2 bucket (name withheld) under `dev-mlx-capture-2026-11-11/`, with `SHA256SUMS`:

| File | SHA-256 |
|---|---|
| `residuals.npz` `[90, 3, 64, 5120]` | `f7cf826a18dbcaa3a4a12e7e86ac466656591eaabcf4c860bf2b9587f4a572c8` |
| `capture-manifest.json` | `50b4754cd55786fee37f2ca2538cf8246eef95a07027ac67c58221cdaf338195` |
