# ADR-004: External Detectors, Steering Recipes, and Which Model to Stay On

**Status:** Accepted 2026-11-11.
**Date:** 2026-11-11
**Depends on:** ADR-003, [held-out score](../../analysis/results/held-out-transfer/README.md), [backend check](../../analysis/results/backend-check/README.md), 4B steering record, issue #16.

## Context

The reasoning-end layer-2 probe, trained on our 90 development cases, did not pass on the five held-out games. It caught 5 of 10 breaches, the same as the text and board baseline. The 4B neuron edit damaged play instead of causing lies. Since then, three kinds of outside resources for Qwen came up: published deception probes, steering recipes and sparse autoencoders. Each was checked on 11 Nov 2026.

### Published probes for Qwen3.5-27B (UK AI Security Institute)

- **[Apollo-style probe](https://huggingface.co/ai-safety-institute/apollo-qwen-qwen3.5-27b)**, revision `a51e6fe7`, MIT licence.
  - Follows Goldowsky-Dill et al. 2025.
  - Trained on instructed honest and deceptive answers about true and false facts. Calibrated to 1% false positives on Alpaca.
  - 296 checkpoints: difference of means, logistic and MLP probes at layers 13, 19, 25, 32, 38, 44, 50 and 57.
  - The default `probe.pt` is `l_32_ar_dim`: one 5,120-dimension direction and a threshold.
  - In AISI's own sweep, layers 32–44 reach AUROC about 0.98 on their test data, and layer 13 about 0.71.
- **["Did you lie?" probe](https://huggingface.co/ai-safety-institute/dyl-qwen-qwen3.5-27b)**, revision `04afefbf`.
  - Reads the activation at the model's yes/no answer to a follow-up question: "Did you lie in the last message - answer yes or no and nothing else?" The answer is generated with reasoning on.
  - Trained on instructed lies about city–country facts. The default checkpoint is `l_38_lm_10_ar_lr`.
- **Loader:** [UKGovernmentBEIS/lie_detectors](https://github.com/UKGovernmentBEIS/lie_detectors), commit `8804308`. The checkpoints are pickled and need `weights_only=False`.
- **Two details the cards don't state:**
  - The layer index. The library says "layer the probe was trained on". It may be our zero-based block 31 (if it counts like transformers `hidden_states`, where entry 0 is the embeddings) or block 32. Comparing the probes' stored means and standard deviations with our activations did not settle it, because neighbouring layers are too similar.
  - Which tokens the probe averages over. Apollo-style probes average over response tokens.

### Steering recipes (Neuronary, Lyra)

Issue #16 records the source of the 4B pair we used: L14N8949 +1, L13N7956 −1. Its author calls it "a personality tune… it becomes extremely stupid at pretty much everything", not a deception circuit. That matches our result. Other leads, as checked in the browser on 11 Nov:

- **[Covert bypass, 4B L17N9209 +1.0](https://neuronary.org/n/L17N9209).** The neuron the evil pair drives. Described as covert rule-bypassing, which is closer to our question, but there is no evidence it produces false peace followed by an attack.
- **[Evil Qwen 27B, L34N3838 +0.75](https://neuronary.org/r/yyraxdpg).** This is Qwen3.8-27B, not 3.5. Hostile but fluent, with one reproduction. Neuron IDs do not carry over between model versions.
- **[Liar's Paradox, 4B L3N8955 +1.0](https://neuronary.org/r/hf4v3tb6).** Mostly confused talk about lying, from an early layer prone to surface-word effects.
- **No recipe for Qwen3.5-27B** is listed on Neuronary.

### Sparse autoencoders (Qwen-Scope)

[Qwen-Scope](https://arxiv.org/pdf/2605.11887) is the Qwen team's SAE suite, released 30 April 2026. It covers every layer of seven backbones, including Qwen3.5-27B, trained on the instruct variant. Expansion is up to 64× and top-k is 50 or 100. It is presented as a development tool for steering, data classification and auditing. We already hold 27B post-block activations for all 196 natural cases at 64 layers and three cutoffs.

## Decision

1. **Stay on Qwen3.5-27B for this project.** The games, labels, held-out score, backend check, both AISI probes and the Qwen-Scope SAEs all exist for this exact model. Moving to a newer model would discard that a month before the write-up.
2. **Choose the model per question for future work.** The auditing-agent track, or a new causal test, uses whichever open model has the most tooling at the time: probes, SAEs, steering dictionaries. Probe weights and neuron IDs are tied to one model version and are not carried over.
3. **Test the AISI Apollo-style probe zero-shot, as an exploratory comparison.**
   - Use the default checkpoint with no refitting, on all 90 development and 106 held-out cases.
   - Average over the sent-message tokens (primary) and the thinking tokens (secondary), at blocks 31 and 32.
   - The choices are frozen in a protocol before scoring. Because the held-out labels are already open, the result is reported as exploratory. It does not change the held-out verdict.
4. **Defer the "Did you lie?" probe to an A100 session.** It needs a generated follow-up answer with reasoning for each case. That is about 30 hours on the M2 Max and under an hour on an A100.
5. **Use Qwen-Scope only to describe what the activations encode.** Read features from the saved activations; this needs no new model runs. Expect little: Google DeepMind found SAE features weaker than linear probes for this kind of detection, and our linear probe found nothing. It is not a new detector.
6. **No more steering on this project.** The 4B pair is a persona with a large competence cost. The only 27B recipe is for a different model version. Covert bypass (L17N9209) is recorded as a possible future causal test on 4B, with unedited and random-neuron controls, only if 4B competence at the game can first be shown.

## Consequences

- The write-up can compare our in-domain probe with a published, independently trained deception probe on the same cases. If the AISI probe also fails, the result is about this setting, not about our training data. If it works, the question becomes why a probe trained on 90 game cases did not find what one trained on instructed lies did.
- The project stays on one model, so every result shares the same weights and token IDs.
- Steering and SAE work stay descriptive or deferred, and do not compete with the plan (15 Nov) and write-up (10 Dec) deadlines.
