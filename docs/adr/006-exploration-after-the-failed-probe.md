# ADR-006: What to Explore After the Block 31 Probe Failed

**Status:** Proposed 2026-11-15. Not yet reviewed by the Teacher.
**Date:** 2026-11-15
**Depends on:** ADR-003 (probe layer choice), ADR-004 (external detectors and Qwen-Scope), the [eight-game result](../../analysis/results/eight-game-reasoning-end/README.md), the [detailed project plan](../feedback/2026-11-15-detailed-project-plan.md).
**Supersedes:** ADR-004 decision 5 ("Use Qwen-Scope only to describe what the activations encode"), which this ADR widens to include one comparison of probes.

## Context

The block 31 probe failed the rule fixed before scoring. On eight games with 185 promises and 23 breaches, AUROC rose from 0.840 to 0.864 against a required gain of +0.050. The 64-block sweep found a similar gain across much of the model, so the choice of block 31 does not explain the result.

Three explanations remain open:

1. **The readout method.** The probe read one block at one token.
2. **The monitor's access.** The text baseline read the model's written reasoning, which may already state most of what the activations carry.
3. **The labels and the sample.** There are 23 breaches, and a breach under the rubric is not evidence of intent when the promise was made.

The project plan filed on 15 Nov scopes weeks 12 and 13 as exploration. This ADR records which directions that exploration takes, in what order, and what the literature says about each.

## Sources

Each entry says how far I checked it. "Abstract read" means I read the arXiv abstract page on 15 Nov 2026. "Search summary" means the claim came from a search result and I have not read the paper. "From the primer" means the claim is marked verified in [`docs/primers/linear-probes-vs-saes.md`](../primers/linear-probes-vs-saes.md).

### Probes against text monitors

- **Hollinsworth, Spies, Diriba, Gleave, Cundy. "Telling FIBS: Probes Effectively Detect Sabotage and Catch Unverbalized Deception."** [arXiv 2610.12445](https://arxiv.org/abs/2610.12445), 8 Oct 2026. Abstract read. Probes reach 98.3% AUROC on SHADE-Arena and 98.0% on BashArena, against 97.7% and 97.6% for text monitors that see only the actions. The abstract does not compare against a monitor that reads the reasoning. Search summary only: the body says the probes did not rely on access to the reasoning, and that earlier comparisons of probes with black-box monitors were mixed.
- **Panfilov et al. "Strategic Dishonesty Can Undermine AI Safety Evaluations of Frontier LLMs."** [arXiv 2509.18058](https://arxiv.org/abs/2509.18058), 22 Sep 2025. Abstract read. Dishonest responses fooled every output-based monitor tested, and linear probes on activations detected them. Search summary only: on one dataset the probes performed on par with a strong monitor that read the reasoning, because the reasoning stated the intent to deceive.
- **"Benchmarking Deception Probes via Black-to-White Performance Boosts."** [arXiv 2507.12691](https://arxiv.org/abs/2507.12691). Title only. Not read. It appears to measure the gain from adding probe scores to a black-box monitor, which is the same comparison as ours.
- **"DeceptGuard."** [arXiv 2603.13791](https://arxiv.org/abs/2603.13791), Mar 2026. Search summary. White-box monitors outperformed the black-box baseline, most in categories where the text gave little signal.

### Probe design

- **Nordby, Pais, Parrack. "Linear Probe Accuracy Scales with Model Size and Benefits from Multi-Layer Ensembling."** [arXiv 2604.13386](https://arxiv.org/abs/2604.13386), 15 Apr 2026. Abstract read. Single-layer probes are fragile because the best layer varies by model and task. Combining probes from several layers recovered strong performance where single-layer probes failed. The authors report that deception directions rotate gradually across layers.
- **Goldowsky-Dill et al. "Detecting Strategic Deception Using Linear Probes."** [arXiv 2502.03407](https://arxiv.org/abs/2502.03407). From the primer. Logistic regression probes rejected control data best, and probes on sparse autoencoder features did worse than probes on raw activations.
- **McKenzie et al.**, cited in the primer. From the primer. Pooling per-token scores is the main change in probe design since 2025, and a readout at the last token performed poorly.

### Sparse autoencoders

- **"Qwen-Scope: Turning Sparse Features into Development Tools for Large Language Models."** [arXiv 2605.11887](https://arxiv.org/abs/2605.11887). From the primer and ADR-004. Residual-stream sparse autoencoders for every layer of seven backbones, including all 64 layers of Qwen3.5-27B, trained on the instruct variant. [Hugging Face card for the 27B set](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50), search summary: 81,920 features, 16× expansion, top-k 50.
- **Kantamneni, Engels et al.**, [arXiv 2502.16681](https://arxiv.org/abs/2502.16681). From the primer. Across 113 datasets, probes on sparse autoencoder features were the best method on 14 and did not improve ensembles.
- **Moustafa, Feser, Mai. "Beyond Liars' Bench: The Impact of Lie Typology, Depth, and Sparsity on Deception Detection in LLMs."** [arXiv 2607.20479](https://arxiv.org/abs/2607.20479), 29 May 2026. Abstract read. Sparse autoencoder features performed similarly to dense hidden states for deception detection.
- **"Transcoders for Investigating Deception in Language Models."** [arXiv 2607.14791](https://arxiv.org/abs/2607.14791). Title only. Not read.
- **"Decodability is Not Causality: Dissociating Probe Readouts from Behavioral Drivers via SAE Decomposition."** [arXiv 2609.18080](https://arxiv.org/abs/2609.18080). Title only. Not read. Relevant to the single-neuron swaps, where a reading that tracked the instruction had a negligible effect on the answer.

## Decision

Explore in this order during weeks 12 and 13. Each step uses the saved games. Every result on the eight scored games is exploratory, and the verdict on the block 31 test stays as recorded.

1. **Rescore against a monitor that cannot read the reasoning.** This tests explanation 2. If the probe adds more when the baseline loses the reasoning, the first test measured a case where the text already held the signal. First check whether the saved feature tables allow this without new model runs.
2. **Describe the saved activations with Qwen-Scope features, and fit one probe on them.** Qwen-Scope reads the same post-block residual stream that we saved at all 64 blocks, so this needs no new model runs. The sources above predict that the feature probe will not beat the raw probe. The main use is to see which features separate kept from broken promises, and whether they describe the situation or the coming action.
3. **Fit a probe that combines several blocks.** This tests explanation 1 and uses the saved activations. Pooling across reasoning tokens needs a new capture, because we saved three cutoffs per case. Do that only if step 3 shows a gain from combining blocks.
4. **Stop the single-neuron search.** The three shortlisted neurons had a negligible effect on the answer and did not carry over to the games. Report them as done.

Fix each comparison in a short protocol before running it, as in the earlier tests. Fit on the four development games and report on the eight scored games.

I may drop, reorder or replace a step after Teacher feedback or after reading the papers marked "not read". Record each change in this ADR with the date and the reason.

## Consequences

- No step can produce a new pass or fail claim, because the eight games are already scored. A confirmed result would need new games.
- Steps 1 to 3 need no paid compute. A token-pooled capture or new games would, and that decision waits for the 28 Nov checkpoint in the plan.
- Explanation 3 is not tested by any step. More labelled breaches would need new games or generated cases, which ADR-005 covers.
- Exploration stops on 5 Dec so the one-page report and the talk are written from results that exist.

## Open questions

1. Do the saved feature tables separate the reasoning-derived features from the rest, so that step 1 needs no new runs?
2. Does 2507.12691 report a comparison close enough to ours to reuse its metric?
3. Which block or blocks should the Qwen-Scope description start from? Block 31 matches the first test, and the sweep's largest gain was at block 36.
