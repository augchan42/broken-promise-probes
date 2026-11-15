# Head-to-head evidence: SAE-feature methods vs supervised probes and other baselines, for detection and steering (as of Nov 2026)

Verification convention (session of 9 Nov 2026): "[verified]" = I opened the primary page (arXiv abstract/HTML, AF post, or lab blog) this session and the number comes from it. "[snippet]" = from a search-result summary only, primary not opened. "[UNVERIFIED]" = secondary source or not checked. Dates: results from 2024–mid 2025 are "older" relative to Nov 2026 and are marked with their date. This file extends, and does not repeat in full, `research_notes/Broken promise probes related work/deception_probes.md`.

## Q1. Detection / classification: do SAE-feature probes beat raw-activation probes?

### Takeaway
On detection, the best-controlled studies (Kantamneni et al., 113 datasets; GDM harmful-intent; AxBench; Apollo) find SAE-feature probes match or lose to logistic regression on raw activations, with the clearest loss under distribution shift (OOD). Win rates for SAE probes are in the 2–20% range of datasets, and the wins do not survive ensembling. The one notable reported win is a commercial PII guardrail (Goodfire/Rakuten, synthetic-to-real transfer), which is not independently verified.

### Cited Findings
**Kantamneni, Engels, Rajamanoharan, Tegmark, Nanda, "Are Sparse Autoencoders Useful? A Case Study in Sparse Probing", arXiv 2502.16681 (23 Feb 2025; older) [verified]**
- Setup: 113 binary classification datasets; main model Gemma-2-9B with Gemma Scope SAEs (widths 16k, 131k, 1M), replication on Llama-3.1-8B with Llama Scope (128k, L0 55). Baselines: logistic regression, PCA regression, KNN, XGBoost, MLP; SAE probes use logistic regression on latents. Layer 20 best for baselines — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Regimes: data scarcity (20 train sizes, 2 to 1024), class imbalance (19 positive ratios, 0.05 to 0.95), label noise (11 corruption levels, 0 to 0.5), covariate shift (8 OOD datasets, 300 shifted test examples each) — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Standard conditions: SAE probes chosen as best method on 14 of 113 tasks, and adding them to the toolkit ("quiver of arrows") slightly lowered performance — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Data scarcity, class imbalance, label noise: no average improvement from SAEs, although SAEs were selected for up to 40 datasets per regime — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Covariate shift: baselines beat SAE probes — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Multi-token: last-token SAE probes beat baselines on 2.2% of datasets; max-pooled SAE probes (k=128, 60 datasets) won 19.6% vs last-token baselines; after adding an attention-pooled baseline, SAE win rate fell to 8.7% — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Architecture: 8 SAE architectures (Oct 2023 to Dec 2024) show only a slight, non-significant upward trend in probing; binarizing latents did not help — [arXiv HTML](https://arxiv.org/html/2502.16681)
- Abstract conclusion: SAEs occasionally win on individual datasets, but no SAE+baseline ensemble consistently beat baseline-only ensembles — [arXiv](https://arxiv.org/abs/2502.16681)

**GDM mech interp team, "Negative Results for SAEs On Downstream Tasks and Deprioritising SAE Research (Progress Update #2)", Smith, Rajamanoharan, Conmy, McDougall, Lieberum, Kramár, Shah, Nanda, 26 Mar 2025 (older) [verified]**
- Task: detect harmful user intent on Gemma-2-9B-IT layer 20; 4,046 train, 1,014 val, 3,850 OOD examples — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft)
- Dense linear probe: AUROC 1.0 train, 1.0 val, 0.999 OOD — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft)
- Single-latent SAE probes failed to fit training data; k-sparse SAE probes fit at about k=20 and generalised in-distribution but transferred worse OOD (exact OOD AUROC not given in text I read) — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft)
- Probe on SAE reconstruction vs raw residual: AUROC gap 0.00087 train, 0.0018 test, 0.048 OOD (GemmaScope); finetuning the SAE on chat data closed about half the gap (OOD gap 0.039) — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft)
- Conclusion: team is "deprioritising fundamental SAE research for the moment"; SAEs still useful for debugging, e.g. finding spurious correlations in datasets — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft); also on [DeepMind Safety Medium](https://deepmindsafetyresearch.medium.com/negative-results-for-sparse-autoencoders-on-downstream-tasks-and-deprioritising-sae-research-6cadcfc125b9)

**AxBench concept detection (Wu et al., arXiv 2501.17148, Jan 2025, v3 Mar 2025; ICML 2025; older) [verified]**
- Mean AUROC over 500 concepts (Concept500), avg over Gemma-2-2B L10/L20 and 9B L20/L31: DiffMean 0.942, linear Probe 0.940, ReFT-r1 0.938, Prompting 0.929, BoW 0.914, SSV 0.912, SAE-A (SAE latents chosen with labels) 0.917, SAE (latent chosen by its auto-interp label) 0.695, LAT 0.712, PCA 0.652, Integrated Gradients 0.426, Input×Gradient 0.246 — [arXiv HTML](https://arxiv.org/html/2501.17148v3)
- So: with supervised latent selection SAEs are about 0.025 AUROC below difference-of-means; with label-based selection they are about 0.25 below — [arXiv HTML](https://arxiv.org/html/2501.17148v3)

**Apollo deception probes (Goldowsky-Dill et al., arXiv 2502.03407, Feb 2025; ICML 2025; older) [verified in prior notes]**
- SAE-feature probes underperformed raw-activation probes on Llama-3.3-70B deception datasets — [arXiv HTML](https://arxiv.org/html/2502.03407) (see deception_probes.md Q1 for raw-probe AUROCs 0.964–0.999)

**Among Us (Golechha & Garriga-Alonso, arXiv 2504.04072, Apr 2025, v3 Feb 2026; NeurIPS 2025) [verified]**
- Goodfire-API SAE features on Llama-3.3-70B, selected on DishonestQA, tested on impostor vs crewmate: best "honesty" feature AUROC 0.967; "acts of deception" 0.851; other deception features 0.675, 0.638, 0.526; several honesty features 0.500; one "contexts involving deception/lying" feature 0.182 (below chance, maybe tracking deception being discussed rather than done) — [arXiv HTML](https://arxiv.org/html/2504.04072)
- Linear probes (logistic regression, Phi-4 layer 20, trained on RepEng, tested on Among Us): AUC 0.94 lying, 0.99 deception — [arXiv HTML](https://arxiv.org/html/2504.04072)
- Caution: probes and SAE features were run on different models (Phi-4 vs Llama-3.3-70B), so this is not a controlled head-to-head — [arXiv HTML](https://arxiv.org/html/2504.04072)

**Cases reported as SAE wins**
- Goodfire + Rakuten PII guardrail: SAE probes "won out" when moving from synthetic training data to real production data; 15–500x cost savings vs LLM-as-judge at comparable performance — [Goodfire customer story](https://www.goodfire.ai/customer-stories/rakuten) [snippet; page not opened]. A 96% F1 and a Llama-3.1-8B "sidecar" model are reported by trade press [UNVERIFIED] — [StartupHub](https://www.startuphub.ai/news/rakuten-deploys-new-guardrail-for-sae-pii-detection)
- A Jan 2026 preprint on board-state probing reports linear probes on the residual stream "decisively outperform" SAE-based probes [snippet, not opened] — [Preprints.org](https://www.preprints.org/frontend/manuscript/940b242abb6b3fe2846c1b9d844699d4/download_pub)
- "Stop Probing, Start Coding" (PMLR v337, 2026) argues both linear probes and SAEs fail at compositional generalization and proposes per-sample sparse coding [snippet] — [PMLR](https://proceedings.mlr.press/v337/barin-pacela26a.html)

### Inferences
- Default expectation for a new detection task: a raw-activation logistic-regression or difference-of-means probe will match or beat an SAE-latent probe; the SAE gap is small in-distribution (≈0.002–0.03 AUROC) and widens OOD (≈0.04–0.05 AUROC in the GDM case).
- The Rakuten result is the only reported win under synthetic-to-real shift, which is the opposite of the GDM/Kantamneni OOD finding. It is a vendor case study without a public head-to-head table, so it should be cited as a claim, not as a benchmark.

### Gaps
- Gallifant et al. on SAE probes for safety classification: not found in this session.
- I found no peer-reviewed 2025–2026 paper with a controlled head-to-head where SAE-latent probes beat raw-activation probes on average.
- Exact OOD AUROC for GDM's k-sparse SAE probes is in figures, not text.

## Q2. Benchmarks: SAEBench, AxBench, discovery benchmarks, 2026 follow-ups

### Takeaway
SAEBench (ICML 2025) shows SAE architecture rankings depend on the metric and that the sparsity-fidelity proxy does not predict downstream metrics; a May 2026 audit (Chanin) finds two of its downstream metrics (SCR, TPP) unreliable. AxBench shows SAEs lag simple baselines on both detection and steering; a May 2026 rebuttal claims better feature selection brings SAE steering near LoRA but still below prompting.

### Cited Findings
**SAEBench (Karvonen, Rager, Lin, Tigges, Bloom, Chanin, Lau, Farrell, McDougall, Ayonrinde, Till, Wearden, Conmy, Marks, Nanda; arXiv 2503.09532, Mar 2025, v4 Jun 2025; ICML 2025; older) [verified]**
- 200+ open SAEs across 8 architectures/training methods — [arXiv](https://arxiv.org/abs/2503.09532)
- 8 metrics: Core (loss recovered + L0), Automated Interpretability, Sparse Probing (top-k latents), RAVEL (attribute disentanglement via intervention), Feature Absorption, Unlearning (WMDP-bio forgotten, MMLU kept), Spurious Correlation Removal (SCR; ablate e.g. gender latents to improve target probe), Targeted Probe Perturbation (TPP; ablating one class's latents should mainly hurt that class's probe) — [arXiv HTML](https://arxiv.org/html/2503.09532v4)
- Gains on proxy metrics do not reliably translate to practical performance; metric rankings disagree (e.g. Gated beats p-anneal on loss recovered, p-anneal beats Gated on absorption). No correlation coefficient given — [arXiv](https://arxiv.org/abs/2503.09532); [HTML](https://arxiv.org/html/2503.09532v4)
- Matryoshka BatchTopK: weaker on sparsity-fidelity frontier but best on Absorption, RAVEL, Sparse Probing, SCR (and TPP in appendix); hierarchical architectures beat others on SCR and absorption "by margins of 30-40%"; advantage grows with scale — [arXiv HTML](https://arxiv.org/html/2503.09532v4)
- Sparse probing: all SAEs beat a baseline of probing K raw residual channels (0.65 on Gemma-2-2B layer 12), but SAEs trained on a randomly initialized model score "close to or worse than" raw residual probing; sparse probing differentiates architectures poorly. Authors state "baseline methods outperform SAEs on several of the benchmark tasks" (Appendix D) — [arXiv HTML](https://arxiv.org/html/2503.09532v4)
- Note: the sparse-probing baseline is K raw neurons, not a full dense probe; the dense-probe comparison is Kantamneni et al. (Q1) — [arXiv HTML](https://arxiv.org/html/2503.09532v4)

**"Are Sparse Autoencoder Benchmarks Reliable?", David Chanin, arXiv 2605.18229 (18 May 2026) [verified]**
- Tests SAEBench metrics for reseed noise, correlation with ground truth on synthetic SAEs, and discriminability across training — [arXiv](https://arxiv.org/abs/2605.18229)
- TPP and SCR fail multiple tests at canonical settings and "should not be used to evaluate SAEs"; other metrics are noisier and less discriminative than assumed; the sae-probes k-sparse probing variant is the most reliable but still struggles to separate variants of one architecture — [arXiv](https://arxiv.org/abs/2605.18229)

**AxBench (Wu, Arora, Geiger, Wang, Huang, Jurafsky, Manning, Potts; arXiv 2501.17148; ICML 2025; older) [verified]**
- Detection numbers in Q1. Steering numbers in Q3. Steering judged by an LLM on concept incorporation, instruction relevance and fluency (0–2 each), overall = harmonic mean (0–2); 10 AlpacaEval instructions per concept, 14 steering factors, half the instructions to pick the factor — [arXiv HTML](https://arxiv.org/html/2501.17148v3)
- Concept16K: datasets for ~16K GemmaScope concepts, used to train SAE-scale supervised dictionaries (DiffMean, ReFT-r1) — [arXiv HTML](https://arxiv.org/html/2501.17148v3)

**Jørgensen & Hansen, "Steering LLMs? Actually, Sparse Autoencoders can outperform simple baselines", arXiv 2605.31183 (29 May 2026) [verified abstract only]**
- Supervised feature selection and labelling pipeline brings SAE steering "close to on par with the reference LoRA performance" on AxBench; still not competitive with prompting; argues low L0 may not matter for steering — [arXiv](https://arxiv.org/abs/2605.31183); prompting gap noted in [arXiv HTML](https://arxiv.org/html/2605.31183v1) [snippet]

**Discovery benchmarks**
- HypotheSAEs (Movva, Peng, Garg, Kleinberg, Pierson; arXiv 2502.04382; ICML 2025; older): SAE on text embeddings, select target-predictive latents, LLM labels them as hypotheses; reports beating baselines on synthetic data, more significant findings on real data, and 1–2 orders of magnitude less compute than LLM-based hypothesis generation; novel findings on Congressional speech partisanship and headline engagement [snippet; abstract not opened] — [arXiv HTML](https://arxiv.org/html/2502.04382v2); [PMLR](https://proceedings.mlr.press/v267/movva25a.html)
- Other 2025–2026 benchmarks seen in search only: CE-Bench (contrastive interpretability eval, arXiv 2509.00691); SAEScientist-Bench (agents doing SAE research, arXiv 2609.09113); "Enhancing SAE-based steering via neighbor integrated feature selection" (arXiv 2602.06855) [all UNVERIFIED] — [CE-Bench](https://arxiv.org/pdf/2509.00691); [SAEScientist-Bench](https://arxiv.org/pdf/2609.09113)

### Inferences
- A primer should not cite SAEBench SCR/TPP scores as evidence of SAE usefulness without the Chanin 2026 caveat.
- SAEBench measures SAEs against each other more than against dense probes; it cannot answer "SAE vs probe" alone.

### Gaps
- No AxBench v2 or official 2026 leaderboard found.
- Exact Jørgensen & Hansen steering scores not read (full text not opened).
- SAEBench numeric SCR/TPP/unlearning scores per architecture not extracted (in figures).

## Q3. Steering comparisons

### Takeaway
On AxBench steering (Gemma-2 2B/9B, 500 concepts), prompting (0.894) beats all representation methods; finetuning-style methods (LoReFT 0.741, SFT 0.676, LoRA 0.615) come next; SAE latent steering (0.165) is below difference-of-means (0.239) but above PCA, LAT and probe directions (0.098). Several papers report SAE or probe features that detect a concept well but do not steer behavior.

### Cited Findings
- AxBench steering overall score (0–2), avg over 4 model/layer settings: Prompt 0.894; LoReFT 0.741; SFT 0.676 (2B only, 20 concepts); LoRA 0.615; ReFT-r1 0.543; DiffMean 0.239; SAE 0.165; SAE-A 0.157; LAT 0.127; PCA 0.105; Probe 0.098 — [arXiv HTML](https://arxiv.org/html/2501.17148v3)
- Abstract: "prompting outperforms all existing methods, followed by finetuning"; SAEs not competitive on either task — [arXiv](https://arxiv.org/abs/2501.17148)
- DiffMean in AxBench is the same construction as CAA (Rimsky et al.), difference of class-mean activations, applied as an additive vector; AxBench does not label it "CAA" [inference from method description] — [arXiv HTML](https://arxiv.org/html/2501.17148v3)
- Detection-steering mismatch in AxBench: the linear probe is second-best at detection (0.940) and last at steering (0.098) — [arXiv HTML](https://arxiv.org/html/2501.17148v3)
- SAE-Targeted Steering (Chalnev, Siu, Conmy; arXiv 2411.02193, Nov 2024; older): fits a linear map from steering vectors to their SAE-feature effects and solves for vectors that hit chosen features; reports better steering-strength/coherence trade-off than CAA and direct SAE feature steering [snippet; numbers not extracted] — [arXiv HTML](https://arxiv.org/html/2411.02193v2)
- FGAA (arXiv 2501.09929) builds on SAE-TS with CAA vectors in SAE space on Gemma-2-2B/9B; reports steering-scale vs capability trade-offs common to all tested methods [snippet] — [arXiv PDF](https://arxiv.org/pdf/2501.09929.pdf)
- Among Us: steering Llama-3.3-70B with top SAE deception/honesty features (Goodfire AutoSteer) left impostors unchanged at small strength and caused hallucination at large strength; no quantitative reduction in lying — [arXiv HTML](https://arxiv.org/html/2504.04072)
- "Decodability is Not Causality" (Tiwari, Davis, Sinha, Weaver, Shah, Chaudhary; arXiv 2609.18080, 16 Sep 2026) [verified abstract]: on Gemma2-9B-IT truth/deception, SAE features ranked by probe alignment and by gradient sensitivity overlap ~12% (Spearman 0.10); ablating shared features flips output up to 27%, probe-only features 6%, random 1%; combining probe info with activation statistics flips 17.6% vs 6.1% — [arXiv](https://arxiv.org/abs/2609.18080)
- Refusal Residue (arXiv 2607.13346, Jul 2026): steering along a detected alignment-faking probe direction barely changes compliance (see deception_probes.md) — [arXiv](https://arxiv.org/abs/2607.13346)

### Inferences
- For steering, the order prompting > finetuning > DiffMean/CAA > SAE latent clamping > probe direction is the best-supported ranking as of Nov 2026; the 2026 Jørgensen & Hansen result may move supervised-selected SAE steering up to about LoRA level, pending full numbers.
- High detection AUROC (for a probe or an SAE feature) is weak evidence of a steering lever; a primer should treat detection and steering as separate claims.

### Gaps
- No direct published CAA-vs-SAE head-to-head with Rimsky et al.'s own datasets found in this session.
- Matryoshka SAE steering comparisons: not found.

## Q4. Where SAEs added value that baselines did not

### Takeaway
The strongest positive cases are unsupervised or exploratory: auditing a model with a hidden objective, debugging datasets, and hypothesis generation. Even there, gains are partly matched by non-SAE tools (semantic search over training data, logistic-regression inspection).

### Cited Findings
- Anthropic auditing game (Marks et al., arXiv 2503.10965, Mar 2025; older) [verified abstract]: 4 blinded teams, 3 found the hidden objective (RM-sycophancy) using SAEs, behavioral attacks and training-data analysis; the failing team had API-only access; an unblinded follow-up studied 8 auditing techniques — [arXiv](https://arxiv.org/abs/2503.10965); [Anthropic](https://www.anthropic.com/research/auditing-hidden-objectives)
- Anthropic auditing agents (Jul 2025; older) [verified]: in the PT+SFT+RL setting, adding SAE interpretability tools raised investigator-agent win rates ~10–20pp from near 0%, partly by surfacing pretraining data; less added value when the agent already had semantic search; best all-tools agent won 13% (17% with a hint); a 10-agent "super-agent" reached 42%; an SAE trained on all three data stages produced zero wins — [Anthropic Alignment blog](https://alignment.anthropic.com/2025/automated-auditing/)
- Dataset debugging (Kantamneni et al.): SAE latent for GLUE CoLA (AUC 0.76) led to LLM-judge relabelling suggesting ~25% of CoLA labels wrong (vs 13% disagreement reported by original authors); AI-vs-human text latent (AUC 0.82) revealed a punctuation artifact; pruning spurious latents improved OOD AUC by 0.024 and 0.052 on 2 of 3 tasks. In each case logistic regression found the same problems — [arXiv HTML](https://arxiv.org/html/2502.16681)
- GDM lists finding spurious correlations in datasets as a remaining SAE use — [Alignment Forum](https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/sae-progress-update-2-draft)
- HypotheSAEs: discovery of interpretable predictors at 1–2 orders of magnitude less compute than LLM baselines [snippet] — [PMLR](https://proceedings.mlr.press/v267/movva25a.html)
- Model diffing: a 2026 paper on reference feature atlases describes pairwise diffing in a shared dictionary, citing Lindsey et al. 2025 and Minder et al. 2025 [snippet; not opened] — [arXiv PDF](https://arxiv.org/pdf/2607.22570)

### Inferences
- SAEs' value is clearest when the target concept is not known in advance (no labels to train a probe). Once a hypothesis exists, a supervised probe is usually as good or better.

### Gaps
- No quantified head-to-head for SAE/crosscoder model diffing vs a non-SAE baseline found.
- Per-toolset win-rate numbers in the auditing-agents post are only in figures.

## Q5. Combined pipelines: SAE proposes, raw probe confirms

### Takeaway
I found no paper that formally benchmarks "SAE generates hypothesis, then train a raw-activation probe" as a pipeline. The closest examples are Kantamneni et al.'s dataset-debugging case studies, HypotheSAEs (SAE then LLM label, with labels validated as predictors), and the 2026 "Decodability is Not Causality" work that uses SAEs to decompose a trained probe.

### Cited Findings
- Kantamneni et al.: SAE latents flagged CoLA label noise and a punctuation shortcut; logistic regression probes confirmed the same issues — [arXiv HTML](https://arxiv.org/html/2502.16681)
- HypotheSAEs: three-stage pipeline (SAE on embeddings, select predictive latents, LLM interpretation as hypothesis) [snippet] — [arXiv HTML](https://arxiv.org/html/2502.04382v2)
- Tiwari et al. 2026: decompose a truth probe into SAE features to separate features that drive behavior from those that only drive the probe readout — [arXiv](https://arxiv.org/abs/2609.18080)
- Auditing agents used SAE feature search together with grep/semantic search over training data; without grep or semantic search, SAE tools won less often — [Anthropic Alignment blog](https://alignment.anthropic.com/2025/automated-auditing/)

### Inferences
- For the promise-probe project (Qwen-Scope SAEs exist for Qwen3.5-27B, see deception_probes.md Q4): train the raw-activation probe as the primary detector; use SAE latents to (a) inspect what the probe picks up (betrayal topic vs intent) and (b) propose confound features to control for, following the Kantamneni and Tiwari patterns. Do not expect an SAE-latent probe to beat the raw probe, especially across games/opponents (OOD).

### Gaps
- No published benchmark of the hypothesis-then-probe pipeline as a method; this is a gap a primer can state.
