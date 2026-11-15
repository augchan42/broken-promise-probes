# ADR-003: Which Layer the Promise Probe Reads

**Status:** Accepted 2026-11-10.
**Date:** 2026-11-10
**Depends on:** [development layer sweep](../../analysis/results/development-layer-sweep/README.md), [held-out score protocol](../superpowers/plans/2026-11-10-held-out-transfer-score.md) (committed 02f37b3), map call C57.

## Context

Qwen3.5-27B has 64 post-block layers (48 linear-attention, 16 full-attention), numbered from zero. The development sweep tried every layer at prompt end, reasoning half and reasoning end on the 90 development cases from four games. Reasoning-end layer 2 came out best:

- 9 of 15 breaches caught in the top quarter per game, against 7 of 15 for the annotation-enhanced baseline. The gain equalled the 95th percentile of within-game label shuffles, so it did not pass the development screen.
- Mean AUROC rose from 0.615 to 0.700 over the text and board baseline.

Call C57 chose reasoning-end layer 2 as the one readout for the one-time held-out score. Layer 2 is about 3% of the way through the network. It was picked from 192 layer and cutoff pairs.

## What the literature says about depth

These citations are from memory and need checking before the write-up quotes them.

- **Early layers (first 10–15% of depth)** rebuild word identity from sub-word tokens and mix in nearby context ("detokenization", Lad et al. 2024). Surface and syntax features peak early in BERT probing (Tenney et al. 2019).
- **Middle layers (about 25–65% of depth)** carry the most linearly readable abstract features:
  - truth of a statement (Marks & Tegmark 2023; Azaria & Mitchell 2023);
  - honesty directions from representation engineering (Zou et al. 2023);
  - the refusal direction (Arditi et al. 2024);
  - steering vectors (Rimsky et al. 2024, around layer 13 of 32 in Llama-2-7B);
  - general-purpose features (Skean et al. 2025).
- **Deception probes in particular:** Apollo's strategic-deception probe on Llama-3.3-70B read layer 22 of 80, about 27% of depth (Goldowsky-Dill et al. 2025). Orgad et al. (2024) also find the best readout in early-middle to middle layers.
- **Late layers** convert the representation into the next-token prediction (logit lens; tuned lens, Belrose et al. 2023). Probes for abstract properties often plateau or drop in the last few layers.

## Decision

1. **Keep reasoning-end layer 2 as the held-out primary.** The protocol froze it before the labels were opened. Changing it now would spend the one-time score on a choice made after seeing the depth argument.
2. **Read a layer-2 result as a text effect first.** The vector is taken at the last reasoning token. An early layer there mostly encodes that token and its neighbours. A gain over the TF-IDF and length baseline most likely means local wording the baseline misses, not a represented plan to break the promise. The write-up says this whether the probe passes or fails.
3. **Middle layers are exploratory only on the held-out games.** The all-layer table in the held-out score is labelled exploratory. A middle-layer result there is a lead, not a finding.
4. **On any new data, name the layer band before looking.** Use a fixed middle band (layers 16–40 of 64, about 25–63% of depth), averaged or chosen on development folds only. Do not pick a single best layer out of 64.

## Consequences

- If layer 2 passes, the claim is limited to "early-layer features at the reasoning end add to a text baseline". The write-up then checks whether that gain survives a richer text baseline before calling it an intent signal.
- If layer 2 fails, the depth argument and the selection from 192 pairs are part of the explanation. The exploratory table shows whether middle layers did any better.
- Future protocols state a layer band in advance, so a lone early layer cannot win by chance.
