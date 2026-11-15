# Methodology and tooling for probing Qwen3.5-27B activations to predict broken peace promises

Scope: a 30-40 hour project. Qwen3.5-27B self-plays a Diplomacy-like game with vLLM on a rented H100. Afterwards, a forward pass caches residual activations over each peace-promise message. Logistic-regression probes, split by game, then predict whether the next orders break the promise.

Verification status: I opened every arXiv abstract page cited below unless the entry is marked "[search listing only]". I opened the RunPod pricing page on 28 Oct 2026. Where I only read an abstract, the entry says so.

**Correction to the plan's architecture description:** the official model card does not say "24 of 32 layers linear attention, 8 full". It gives **64 layers** with hidden size 5120, laid out as "16 × (3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))". That is 48 Gated DeltaNet (linear) layers and 16 full gated-attention layers, with full attention every 4th layer. The card also lists the model as a "Causal Language Model with Vision Encoder" (multimodal) and says thinking mode is on by default — [HF model card](https://huggingface.co/Qwen/Qwen3.5-27B). The Qwen-Scope SAE card agrees on 64 layers and d_model 5120 — [HF SAE card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50).

## 1. Probe validity: controls, selectivity, confounds, causal checks, generalisation. What is the minimal convincing set?

### Takeaway
Reviewers will expect three things: a probe that beats strong metadata-only baselines (speaker, turn, board state, message length), results that hold out of distribution (held-out games at minimum), and one causal or specificity check. The 2026 negative results show the main way such probes fail: they read the situation rather than the coming action.

### Cited Findings
- **Control tasks and selectivity.** Hewitt & Liang, "Designing and Interpreting Probes with Control Tasks" (arXiv:1909.03368). Control tasks "associate word types with random outputs". A good probe is *selective*: it achieves "high linguistic task accuracy and low control task accuracy". Selectivity separates what the representation encodes from what the probe can memorise — [arXiv:1909.03368](https://arxiv.org/abs/1909.03368)
- **Probes reading the situation, not the action (the most relevant caution).** Fomin, David & LeVi, "Internal-State Probes Read the Situation, Not the Action: Three Negative Results for Pre-Action Misalignment Monitoring" (arXiv:2606.30449, 29 Jun 2026, ICML 2026 AIWILD workshop). Llama-3.1-8B probes decode prompt domain at AUC 0.999. The best future-behaviour probe reaches only AUC 0.801, which is +5.1 pp accuracy over the majority baseline. Single-source cross-domain transfer is "non-positive on five of six ordered pairs". A Qwen2.5-Coder-32B direction separates fine-tuned from base models at AUC 1.000 but "crosses its threshold on 0/143 audited pre-assistant turn contexts". With Gemma-3-27B, "a shared-prefix minimal pair has indistinguishable states before the first differing input", and steering specificity weakens when compared against unrelated directions (cats, weather, sports, geography). Conclusion: "monitor claims must survive both scenario/action generalization and concept-specificity controls" — [arXiv:2606.30449](https://arxiv.org/abs/2606.30449) (abstract only)
- **Steering along the probe direction with norm-matched baselines.** Cox, Kianersi & Garriga-Alonso compare steering along the probe direction against "norm-matched orthogonal baselines". This tests whether answer flips come from the direction itself or just from the size of the perturbation — [arXiv:2603.01437](https://arxiv.org/abs/2603.01437) (abstract only)
- **Ablation and addition of one direction as a causal test.** Arditi et al., "Refusal in Language Models Is Mediated by a Single Direction" (arXiv:2406.11717), tested 13 open chat models up to 72B. Removing the direction stops refusals, and adding it causes refusals of harmless requests — [arXiv:2406.11717](https://arxiv.org/abs/2406.11717)
- **Probe partly tracking deception-related text.** Goldowsky-Dill et al. (Apollo), "Detecting Strategic Deception Using Linear Probes" (arXiv:2502.03407, ICML 2025). They fit logistic-regression probes on the Llama-3.3-70B residual stream after layer 22 of 80, with L2 regularisation on normalised activations. AUROC was 0.96-0.999 on their evaluation sets, catching 95-99% of deceptive responses at 1% FPR. One of their checks suggests the probe may partly respond to deception-related text in general rather than to actual deception. The authors judge performance insufficient as a robust defence — [arXiv PDF](https://arxiv.org/pdf/2502.03407), [Alignment Forum summary](https://alignmentforum.org/posts/9pGbTz6c78PGwJein/detecting-strategic-deception-using-linear-probes) [search listing only; I did not open the abstract page]

### Inferences
Minimal convincing set for this project, roughly in priority order:
1. **Splits.** Group-split by game (already planned). Also report a held-out-condition split if there is more than one condition (e.g. personas, prompt variants). Cross-condition transfer is where Fomin et al. found probes failing.
2. **Metadata-only baselines.** Train logistic regression on surface features alone: speaker state one-hot, recipient, turn/year, supply-centre counts, adjacency or border-contact with the recipient, message length, and keyword-match strength. Report the probe's AUROC *above* this baseline. Also train a probe on activations residualised against the same features, or on metadata plus activations, to show the activations add information. This is the Diplomacy version of the "reads the situation" failure.
3. **Text-only baseline.** Train a bag-of-words or TF-IDF classifier on the promise message text, plus an embedding-model baseline if time allows. If the activation probe does no better than these, it is reading surface content.
4. **Control task (Hewitt & Liang style).** Shuffle labels within game, or within speaker-state, and retrain. This checks that probe capacity plus the group structure does not produce high AUROC. It is cheap.
5. **Layer sweep and token-position check.** Probe every few layers, with points on both GDN and full-attention layers. Compare the last token of the promise message with the mean over the message. Report activations taken *before* any token of the orders. With thinking mode on, the model may write its plan in `<think>` before the message, so state which tokens the probe can see.
6. **One causal check, if time allows.** Add or subtract the probe direction at the chosen layer during order generation, and compare against norm-matched random or orthogonal directions (Cox et al.). This is the most expensive item and can be dropped if hours run short. Selectivity and baselines should not be dropped.

### Gaps
- I found no published probing study set in a Diplomacy or negotiation game. The search surfaced Apollo's deception probes but no Diplomacy-specific activation work.
- Full-paper details for Fomin et al. and Cox et al. (exact protocols, flip rates) were not read. I saw abstracts only.

## 2. Prior work predicting an LLM's future actions or choices from activations before the action

### Takeaway
There is solid 2023-2026 precedent that answers, tool calls and refusals can be linearly decoded before they are generated, often at AUC 0.8-0.9+, and that steering along the direction flips behaviour. There is an equally recent, directly relevant negative result: such probes often fail to generalise and mostly read context.

### Cited Findings
- **Answers decided before chain of thought.** Cox, Kianersi & Garriga-Alonso, "Post-Hoc Reasoning in Chain of Thought: Decoding and Steering Pre-Committed Answers" (arXiv:2603.01437; v1 2 Mar 2026, v2 23 Jul 2026). Linear probes on the residual stream at the last token before CoT predict the final answer with "more than 0.9 AUC on most tasks", and steering along the probe direction flips answers above baseline rates. The ICML 2026 listing uses an earlier title, "Decoding Answers Before Chain-of-Thought: Evidence from Pre-CoT Probes and Activation Steering" — [arXiv](https://arxiv.org/abs/2603.01437), [ICML listing](https://icml.cc/virtual/2026/79302)
- **Tool-call decisions decoded before reasoning.** Esakkiraja et al., "Therefore I am. I Think" (arXiv:2604.01202, Apr 2026). A linear probe on pre-generation activations decodes tool-calling decisions, "sometimes before any reasoning token". Perturbing the decision direction flips behaviour in "7 - 79%" of examples, depending on model and benchmark, and the CoT often rationalises the flip — [arXiv:2604.01202](https://arxiv.org/abs/2604.01202) (abstract only)
- **Future tokens from a single hidden state.** Pal, Sun, Yuan, Wallace & Bau, "Future Lens: Anticipating Subsequent Tokens from a Single Hidden State" (arXiv:2311.04897). On GPT-J-6B, a single hidden state predicts subsequent tokens (t+2 and later) with over 48% accuracy at some layers — [arXiv:2311.04897](https://arxiv.org/abs/2311.04897)
- **Refusal as one direction.** See Arditi et al. above. This is the standard citation that a future behaviour (refusal) is mediated by a linear direction readable at the prompt — [arXiv:2406.11717](https://arxiv.org/abs/2406.11717)
- **Correctness readable early in reasoning.** David, "Temporal Predictors of Outcome in Reasoning Language Models" (arXiv:2511.14773). Hidden states from very short prefixes (t≈4) linearly predict eventual correctness, with AUC up to 0.8+ on MATH-like data. The paper argues that late-stage accuracy drops are partly a selection effect, because harder problems produce longer CoT — [arXiv HTML](https://arxiv.org/html/2511.14773v1) [search listing only]
- **Multi-step future tool calls in agents.** "Reading the Plan: Multi-Horizon Future-Action Prediction from Frozen Hidden States in LLM Agents" (NeurIPS 2026). Reportedly, future tool calls k=1,3,5 steps ahead are decodable from one residual state at about 3/4 depth — [NeurIPS listing](https://neurips.cc/virtual/2026/166872) [search listing only; no arXiv ID found]
- **Probes on reasoning steps used for steering.** arXiv:2606.11172 reportedly trains probes on intermediate reasoning steps to predict future behaviour at 64%-91% accuracy — [EmergentMind](https://www.emergentmind.com/papers/2606.11172) [search listing only; title not verified]
- **Negative result.** Fomin et al. (arXiv:2606.30449), above: the best future-behaviour probe is +5.1 pp over the majority baseline, and cross-domain transfer mostly fails — [arXiv:2606.30449](https://arxiv.org/abs/2606.30449)

### Inferences
- This project sits between "intent before action" (Cox et al.; Esakkiraja et al.) and "deception detection" (Apollo). Promise-then-betray is a deception-adjacent future action, and the gap from message to orders is long and spans turns. That makes the Fomin et al. concern (probe reads the board situation that makes betrayal likely) the main threat. Baseline #2 in section 1 targets it directly.
- A positive result framed as "AUROC above a metadata baseline, held-out games" is defensible. A raw AUROC alone is not.

### Gaps
- I found no work that probes for *broken commitments* or promise-keeping specifically.
- No verified paper reports how predictability decays with the distance (in tokens or turns) between the probed state and the action. Future Lens and Reading the Plan touch on this for short horizons only.

## 3. Label noise (keyword-detected promises), class imbalance (~14% positives), sample size

### Takeaway
None of my searches returned a probing paper that addresses keyword-label noise or sample size for this setting. The recommendations below are inferences from standard practice and from the numbers in the cited papers.

### Cited Findings
- Apollo's deception probes are logistic regression with L2 regularisation on normalised activations. This is the same probe family as planned and a reasonable reference configuration — [arXiv:2502.03407](https://arxiv.org/pdf/2502.03407) [search listing only]
- Fomin et al. report accuracy over the *majority baseline* (+5.1 pp at AUC 0.801). This shows why imbalanced-label results should be reported against the trivial classifier — [arXiv:2606.30449](https://arxiv.org/abs/2606.30449)

### Inferences
- **Imbalance (~14%).** Report AUROC and AUPRC (AUPRC baseline = 0.14), plus balanced accuracy or TPR at a fixed low FPR (Apollo's 1% FPR framing). Use `class_weight="balanced"` in logistic regression. Report bootstrap CIs resampled by game, not by example, since examples within a game are correlated.
- **Label noise, two sources.** (a) The promise detector: false-positive "promises" dilute positives and negatives alike. Hand-label a random sample of about 100 detected messages, and about 100 non-detected messages for recall, and report precision and recall. Optionally use an LLM judge as a second detector and rerun on the agreement subset. (b) "Broken" detection from orders: define the label mechanically (move into or support against the promisee's units or centres next turn) and spot-check it. Showing results on a clean subset alongside the full noisy set is a standard robustness check.
- **Sample size.** With about 14% positives, about 300 positives needs about 2,100 promise instances. Logistic regression on 5,120-dim features with a few hundred positives needs strong L2 regularisation or PCA to about 50-200 dims first. Tune the regularisation with grouped CV inside the training games. Choose the number of games so that each test fold has at least about 50 positives, or AUROC CIs will be wide. These are rule-of-thumb inferences, not sourced figures.

### Gaps
- I found no source giving the sample sizes needed for activation probes at a given AUROC precision. A power calculation (e.g. Hanley-McNeil AUROC SE) would need to be done by hand.
- I found no source on how others handled keyword-detected labels in probing work.

## 4. Tooling: capturing residual activations (vLLM vs HF transformers / nnsight / TransformerLens), memory, speed, teacher-forced replay fidelity

### Takeaway
The simplest reliable route is to generate with vLLM, then replay prompt+output once as a prefill. Do the replay either with vLLM's built-in `extract_hidden_states`, which saves prompt-token hidden states only (which is exactly a replay), or with plain HF transformers plus `register_forward_hook` on `model.model.layers[L]`. nnsight and TransformerLens support for Qwen3.5 exists but has open bugs. Replayed activations will not be bit-identical to generation-time activations, and need not be.

### Cited Findings
- **vLLM hidden-state extraction (vllm>=0.18.0, PR #33736).** Enable it with `"method": "extract_hidden_states"` in `--speculative_config` and `"kv_connector": "ExampleHiddenStatesConnector"` (kv_role `kv_producer`, `shared_storage_path`). Choose layers via `eagle_aux_hidden_state_layer_ids`. Output is a safetensors file with `token_ids [prompt_seq_len]` and `hidden_states [prompt_seq_len, num_layers, hidden_size]`. "Only the prompt tokens and their hidden states will be saved". The post recommends `max_tokens=1`. Disk writes currently block. Single-node TP/DP is supported. The post does not discuss hybrid models — [vLLM blog](https://vllm.ai/blog/2026-03-30-extract-hidden-states), [API docs](https://docs.vllm.ai/en/stable/api/vllm/v1/spec_decode/extract_hidden_states/)
- **vLLM recipe for Qwen3.5-27B.** Minimum vLLM is 0.17.0. **BF16 is listed for 1x H200 or 2x H100 (TP2)** at `--max-model-len 262144`. The FP8 checkpoint fits a single GPU. `--language-model-only` skips the vision encoder. MTP speculative decoding is supported. Prefix caching for the Mamba-style layers is "experimental" in "align" mode. For a CUDA-graph or Mamba-cache size error, reduce `--max-cudagraph-capture-size`. To disable thinking, use `--default-chat-template-kwargs '{"enable_thinking": false}'`. The recipe gives no throughput numbers — [vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3.5-27B)
- **Transformers version.** The model card says "The latest `transformers` is required for Qwen3.5" — [HF card](https://huggingface.co/Qwen/Qwen3.5-27B). GitHub threads report that transformers 4.x cannot load `qwen3_5` — [verl #5937](https://github.com/verl-project/verl/issues/5937), [TensorRT-LLM #12321](https://github.com/NVIDIA/TensorRT-LLM/issues/12321)
- **TransformerLens.** It has Qwen3.5 and Qwen3Next adapters. Open bug #1868: the adapters don't set `rmsnorm_uses_offset`, so edited or backward-hooked norms drop the `1 +` in `(1 + weight)`. A plain forward pass is unaffected — [TL #1868](https://github.com/TransformerLensOrg/TransformerLens/issues/1868). PR #1950 (merged 26 Oct 2026) updates the Qwen3.5 test fixture — [TL PR #1950](https://github.com/TransformerLensOrg/TransformerLens/pull/1950). A circuit-tracer issue notes that transformer-lens 3.x requires transformers>=5.9, and that the nnsight backend broke under transformers 5 / huggingface_hub 1 — [ARENA circuit-tracer #1](https://github.com/ARENA-education/circuit-tracer/issues/1)
- **nnsight.** Open issue #711: "With multiple-gpus tracer fails with Qwen3.5" — [nnsight #711](https://github.com/ndif-team/nnsight/issues/711) (title only seen)
- **Prefill vs decode kernels differ for GDN layers.** Gated DeltaNet uses a chunked gated-delta-rule kernel for prefill and a recurrent kernel for decode — [MindStudio Qwen3.5 design doc](https://mindstudio-docs-master.readthedocs.io/zh-cn/latest/msmodeling/docs/RFC/rfc_add_qwen3.5_support_en/)
- **vLLM vs HF numerical differences.** The vLLM FAQ attributes logprob differences to batch composition and non-deterministic kernels — [vLLM FAQ](https://docs.vllm.ai/en/v0.6.3.post1/serving/faq.html). `VLLM_BATCH_INVARIANT=1` gives run-to-run determinism regardless of batch (compute capability ≥8.0) — [vLLM batch invariance](https://docs.vllm.ai/en/stable/features/batch_invariance/). A user report describes vLLM logprobs drifting from transformers — [vLLM forum](https://discuss.vllm.ai/t/numerical-difference-between-vllm-logprobs-and-huggingface-logprobs/151). NeMo RL checks vLLM-vs-HF logprob agreement with an error-ratio threshold of 1.05 — [NeMo RL docs](https://docs.nvidia.com/nemo/rl/0.4.0/adding-new-models.html)
- **Hooking with plain transformers.** The Qwen-Scope card's own demo loads the model with transformers and registers a forward hook on `model.model.layers[LAYER]` to read the residual stream — [HF SAE card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)

### Inferences
- **Memory.** 27B params × 2 bytes ≈ 54 GB of bf16 weights. That fits on one 80 GB H100 with about 20 GB left for KV/state and activations. The recipe's 2x H100 recommendation is for the 262K max-model-len. With `--max-model-len` of about 16-32K, `--language-model-only`, and a reduced `--gpu-memory-utilization`, single-H100 bf16 serving should be workable, but this is untested. The Diplomacy prompts are short, so it is plausible. The fallback is the FP8 checkpoint for self-play, with **bf16 HF replay** for activations. In that case the probed model differs slightly from the generating model, which should be documented.
- **Replay fidelity.** Generation runs decode (recurrent GDN kernel, paged KV, batching). Replay is one prefill (chunked kernel). Activations will differ at bf16-noise level and will not be identical. This does not matter for a probe so long as all train and test activations come from the same replay pipeline. Labels come from the actual generated orders. Sanity check: replay a few transcripts and confirm the argmax next token under teacher forcing matches the generated token in nearly all positions (e.g. >99%). That would show the replay is faithful. Seed and log sampling parameters.
- **Recommended pipeline.** (1) Self-play with vLLM, saving full prompt and output text plus token IDs. (2) Replay with HF transformers on the same GPU after stopping vLLM: `torch_dtype=bfloat16`, text-only, batch size 1-4, forward hooks on about 8-16 chosen layers, keeping only the token positions of the promise message (last token plus mean-pooled). Use vLLM `extract_hidden_states` if HF speed is a problem. Its output for all 64 layers is 64×5120×2 B ≈ 655 KB per token, about 0.65 GB per 1K tokens, so select layers. (3) Fit probes on CPU with scikit-learn.
- **Speed.** A single bf16 prefill of about 4K tokens through 27B costs roughly 2×27e9×4e3 ≈ 2e14 FLOPs, which is well under a second at H100 bf16 rates in theory. A few thousand replays should take minutes to tens of minutes, not hours. This is an arithmetic estimate, not measured.
- **Avoid for this project:** nnsight (open Qwen3.5 bug, transformers-5 friction) and TransformerLens (norm-offset bug matters for steering edits). Plain hooks are enough for reading and for adding a steering vector.

### Gaps
- No source confirms that `extract_hidden_states` works with Qwen3.5's hybrid GDN layers, or that its output is the residual stream after the block, as opposed to a pre- or post-norm position.
- I found no measured activation-difference figures between generation-time and teacher-forced replay for GDN or hybrid models.
- No measured HF-transformers prefill speed for Qwen3.5-27B on an H100.

## 5. Qwen-Scope SAEs for Qwen3.5-27B and interp library support

### Takeaway
Qwen-Scope SAEs exist for Qwen3.5-27B: residual stream, all 64 layers, width 81,920, TopK. They are plain `.pt` dicts usable with simple hooks. Neuronpedia hosts the model, but inference there is not enabled. I found no SAELens loader. (Correction, 9 Nov 2026: SAELens has registered all 14 Qwen-Scope groups since 30 Apr 2026, e.g. `qwen-scope-3.5-27b-w80k-l50`; see [the probes vs SAEs primer](../../docs/primers/linear-probes-vs-saes.md).)

### Cited Findings
- `Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50`: residual stream, layers 0-63 (one `layer{n}.sae.pt` per layer), d_sae 81,920 (16× of 5,120), TopK = 50. The dict holds `W_enc (81920,5120)`, `W_dec`, `b_enc`, `b_dec`. Loading uses transformers plus a forward hook. Licence tag "qwen", with a clause that "It is strictly prohibited to use interpretability tools for non-scientific research purposes". The associated paper is dated May 2026, and the collection was updated 14 May — [HF SAE card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)
- The card lists the base model as Qwen/Qwen3.5-27B. A third-party summary says the 27B SAE is trained on the instruct variant and mentions a Top-K 100 variant. These claims are unconfirmed — [lilting.ch summary](https://lilting.ch/en/articles/qwen-scope-sparse-autoencoders) [search listing only]
- Neuronpedia has a Qwen3.5-27B page with a layer-31 Qwen-Scope SAE, with inference not enabled — [Neuronpedia](https://www.neuronpedia.org/qwen3.5-27b) [search listing only]
- Qwen-Scope release date of 30 Apr 2026 per secondary coverage — [lilting.ch](https://lilting.ch/en/articles/qwen-scope-sparse-autoencoders) [search listing only]

### Inferences
- The SAEs are an optional extra: e.g. inspect the top SAE features aligned with the probe direction (cosine with `W_dec` columns) to see whether the probe reads "aggression" or "board threat" features rather than deception or intent. This is a cheap interpretability check that also addresses the confound question. It is not needed for the core result.
- The released Qwen3.5-27B checkpoint is the post-trained (chat, thinking-by-default) model. The SAE "base model" listing therefore probably refers to that checkpoint, but this is not verified.

### Gaps
- SAELens support for Qwen-Scope was not checked. I found no loader. (Corrected 9 Nov 2026: a loader exists; see above.)
- I did not confirm whether a TopK-100 variant exists for 27B.

## 6. RunPod H100 80GB pricing (Oct 2026) and vLLM throughput for ~27B

### Takeaway
RunPod's pricing page (updated 8 Oct 2026) lists H100 PCIe 80GB at $1.99/hr Community / $2.89/hr Secure, and H100 SXM at $2.69 / $3.99. A 30-40 h project with about 10-20 GPU-hours costs roughly $20-80. I found no published vLLM throughput figure for Qwen3.5-27B.

### Cited Findings
- RunPod Pods, on-demand per hour: H100 PCIe 80GB $1.99 (Community) / $2.89 (Secure); H100 SXM 80GB $2.69 / $3.99; H100 NVL 94GB $2.59 / $3.19; H200 141GB $3.59 / $5.29. Serverless H100 $4.79/hr. No spot prices listed. Page says "Updated October 8, 2026". My fetch tool inferred the Community/Secure split from the page's structured data — [RunPod pricing](https://www.runpod.io/gpu-cloud/pricing) (opened 28 Oct 2026)
- Third-party figures differ: Spheron cites spot H100 PCIe at $0.80-1.20/hr, and other blogs give older on-demand prices — [Spheron](https://www.spheron.network/blog/runpod-h100-pricing-2026/) [search listing only; not authoritative]
- The vLLM recipe for Qwen3.5-27B gives no throughput numbers — [vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3.5-27B)

### Inferences
- Cost: 15 GPU-hours × $1.99-2.69 ≈ $30-40, plus storage. Budget about 2× for setup and debugging.
- An H200 ($3.59 Community) runs bf16 at the recipe's settings on one GPU. It may save debugging time compared with squeezing bf16 into 80 GB, at about 1.3-1.8× the hourly cost.
- Throughput: GDN layers keep a fixed-size state instead of a growing KV cache, so long multi-agent transcripts should batch well. No measured tokens/s found. Measure it in the first hour (e.g. `vllm bench serve`) before committing to the number of games.

### Gaps
- No verified vLLM tokens/s for Qwen3.5-27B (bf16 or FP8) on one H100.
- The RunPod page's Community vs Secure labelling came from structured data that my fetch tool interpreted. Re-check the live page at rental time.
