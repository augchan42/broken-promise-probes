# Qwen-Scope sparse autoencoders (fact sheet, as of 9 Nov 2026)

Notes: "verified" below means I read it on the primary page (arXiv HTML, HF card, HF API JSON, repo files, SAELens registry). Some arXiv details came through a summarising fetch tool and are marked where the extraction was garbled.

## Paper: authors, dates, claims and quantitative results

### Takeaway
arXiv 2605.11887 has one version (v1, 12 May 2026), 18 authors led by Boyi Deng. It presents Qwen-Scope as SAEs used as development tools in four areas: steering, evaluation analysis, data workflows, post-training. Its numeric results are mostly on Qwen3-1.7B/8B/30B-A3B, not on Qwen3.5-27B. The weights went up on Hugging Face about two weeks before the paper.

### Cited Findings
- Title: "Qwen-Scope: Turning Sparse Features into Development Tools for Large Language Models". Categories cs.CL (primary), cs.LG. Only v1, submitted Tue 12 May 2026 10:01 UTC — [arXiv abs](https://arxiv.org/abs/2605.11887)
- Authors (18): Boyi Deng, Xu Wang, Yaoning Wang, Yu Wan, Yubo Ma, Baosong Yang, Haoran Wei, Jialong Tang, Huan Lin, Ruize Gao, Tianhao Li, Qian Cao, Xuancheng Ren, Xiaodong Deng, An Yang, Fei Huang, Dayiheng Liu, Jingren Zhou — [arXiv abs](https://arxiv.org/abs/2605.11887)
- Release timeline before the paper: the HF repo `Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50` was created 27 Apr 2026 (last modified 13 May 2026) — [HF API](https://huggingface.co/api/models/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50). The `Qwen/QwenScope` Space was created 29 Apr 2026, and its README cites the work as "Qwen Team, April 2026" — [HF Space API](https://huggingface.co/api/spaces/Qwen/QwenScope). SAELens added the loaders on 30 Apr 2026 (commit "feat: add Qwen Scope TopK SAEs (#677)") — [SAELens commits](https://github.com/decoderesearch/SAELens/commits/main/sae_lens/pretrained_saes.yaml). MarkTechPost covered the release on 1 May 2026 — [MarkTechPost URL](https://www.marktechpost.com/2026/05/01/qwen-ai-releases-qwen-scope-an-open-source-sparse-autoencoders-sae-suite-that-turns-llm-internal-features-into-practical-development-tools/) (page returned 403; date taken from the URL only)
- Framing: the abstract names four areas: inference-time steering, evaluation analysis, data-centric workflows, and post-training optimisation — [arXiv abs](https://arxiv.org/abs/2605.11887)
- Steering (qualitative only): suppressing a Chinese-language feature (#6159) removes unwanted Chinese from English output, and a Classical-Chinese feature (#36398) moves a modern Chinese story toward classical style. The paper gives no numbers for these. Ablation takes the form x′ ← x − λd — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Benchmark redundancy: across 17 benchmarks and 26 checkpoints, feature-based redundancy correlates with performance-based redundancy at Spearman ρ ≈ 0.85. 63% of GSM8K's features are covered by MATH, against 10% the other way. SuperGPQA (26,529 questions) shows low redundancy. Across 28 inter-benchmark pairs, direct correlation is Pearson 68.4 / Spearman 60.7, and partial correlation controlling for MMLU is Pearson 75.5 / Spearman 71.3 — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Data classification (toxicity): Qwen3-1.7B (32K SAE) and Qwen3-8B (64K SAE), 13 languages, about 5,000 examples per language (4,000 for feature discovery, 1,000 for evaluation). English best F1 exceeds 0.90 for both models. Transfer from English works well for Russian and French and less well for Arabic, Chinese and Amharic. Discovery on 10% of the data keeps about 99% of the performance — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Data synthesis (safety), Qwen3-8B, layer-30 SAE with about 65K latents: feature-driven synthesis reaches 99.74% target-feature coverage at matched budget. In Table 3, "Safety 44k + Feature synth 44k" gives ASR 24.0, RR 20.5, Acc 77.75, IFEval 53.23. "Safety 44k + Random synth 44k" gives ASR 20.0, RR 36.0, Acc 72.00, IFEval 48.98. Alpaca-only gives ASR 73.0 — [arXiv HTML](https://arxiv.org/html/2605.11887v1) (the extraction garbled one row label, 8k vs 88k)
- Code-switching (SASFT: SFT plus a regulariser on the pre-activations of language features). In Table 4, the code-switch ratio for Qwen3-1.7B-Base at 210k data falls zh 0.81→0.22 (−72%), ru 0.19→0.03 (−85%), ko 0.36→0.00 (−100%). For Qwen3-8B-Base at 210k: zh 0.96→0.66 (−31%), ru 0.16→0.07, ko 0.43→0.07. Table 5 shows general benchmarks roughly unchanged (Qwen3-1.7B: MMLU 37.47→38.38, HumanEval 90.29→89.04, MGSM 32.91→30.85). The paper says SASFT was evaluated on five models across Gemma-2, Llama-3.1 and Qwen3 — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Repetition and RL: the method adds a repetition-feature direction (h′ ← h + αd) to make one steered negative rollout per group, on DAPO without Dynamic Sampling. Table 7 (before RL / vanilla RL / RL+SAE): Qwen3-1.7B MGSM 46.80 / 46.48 / 52.36. Qwen3-30B-A3B MGSM 76.56 / 77.64 / 82.40. Qwen3-8B IFEval 71.04 / 70.42 / 68.96, a fall. The authors call downstream effects "mixed and task-dependent". Repeat ratios appear only in a figure — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Limitations the authors state: repetition features also fire on benign repetition, so they did not suppress them during SFT. Early steering for positive rollouts hurt multi-step reasoning and fluency. Feature coverage is a coarse estimate. Cross-lingual transfer is uneven. Interpretability research lacks safeguards against misuse — [arXiv HTML](https://arxiv.org/html/2605.11887v1)

### Inferences
- Each application result uses Qwen3 models (1.7B, 8B, 30B-A3B). None of the quantitative results I extracted uses the Qwen3.5-27B SAEs. A primer should not credit any headline number to the 27B SAEs.
- The "over 50% code-switching reduction" figure in secondary coverage matches the Qwen3-1.7B rows (−55% to −100%) but not the Qwen3-8B zh rows (−26%, −31%).

### Gaps
- I could not find the exact token count, context length, learning rate or batch size for SAE training. Three passes through the HTML gave only "in-house pretraining data" and an auxiliary loss with weight 1/32 (Gao et al. 2024). They may sit in the PDF or in figures.
- No official Qwen blog post or GitHub repo found. `github.com/QwenLM/Qwen-Scope`, linked from a QevosAgent blog, returns 404 via the GitHub API.

## Coverage: models, hookpoints, layers, widths, k, checkpoints, metrics

### Takeaway
There are 14 repos (SAE groups) over 7 backbones. All are residual-stream (`resid_post`), all layers, TopK with k = 50 or 100. Expansion is 16× except the two 128K MoE groups at 64×. Every backbone used a Base checkpoint except Qwen3.5-27B, which used the post-trained checkpoint. The paper and cards report no per-SAE reconstruction metrics I could find.

### Cited Findings
- Paper Table 1. All SAEs are residual-stream SAEs on all layers. "Qwen3.5-27B is the only backbone whose SAEs are trained on the instruct variant." "For MoE models, we additionally release wider SAEs" — [arXiv HTML](https://arxiv.org/html/2605.11887v1):

| Backbone | Checkpoint | Layers | d_model | Width | k |
|---|---|---|---|---|---|
| Qwen3-1.7B | Base | 28 | 2048 | 32K | 50, 100 |
| Qwen3-8B | Base | 36 | 4096 | 64K | 50, 100 |
| Qwen3.5-2B | Base | 24 | 2048 | 32K | 50, 100 |
| Qwen3.5-9B | Base | 32 | 4096 | 64K | 50, 100 |
| Qwen3.5-27B | Instruct | 64 | 5120 | 80K (81,920) | 50, 100 |
| Qwen3-30B-A3B (MoE) | Base | 48 | 2048 | 32K (k=50); 128K (k=100) | 50 / 100 |
| Qwen3.5-35B-A3B (MoE) | Base | 40 | 2048 | 32K (k=50); 128K (k=100) | 50 / 100 |

- The HF collection lists 16 items: 14 model repos, the paper, and the `Qwen/QwenScope` Space. Repos: SAE-Res-Qwen3-1.7B-Base-W32K-L0_{50,100}; SAE-Res-Qwen3-8B-Base-W64K-L0_{50,100}; SAE-Res-Qwen3.5-2B-Base-W32K-L0_{50,100}; SAE-Res-Qwen3.5-9B-Base-W64K-L0_{50,100}; SAE-Res-Qwen3.5-27B-W80K-L0_{50,100}; SAE-Res-Qwen3-30B-A3B-Base-W32K-L0_50; SAE-Res-Qwen3-30B-A3B-Base-W128K-L0_100; SAE-Res-Qwen3.5-35B-A3B-Base-W32K-L0_50; SAE-Res-Qwen3.5-35B-A3B-Base-W128K-L0_100 — [HF collection](https://huggingface.co/collections/Qwen/qwen-scope)
- Layer indexing: the paper table writes layers 1–64. The repos and config use 0–63 (`layer0.sae.pt` … `layer63.sae.pt`) — [config.json](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/config.json)
- Hookpoint is the residual stream only: `"hook_point": "resid_post"`, the output of each decoder layer — [config.json](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/config.json). A third-party paper confirms it: "QwenScope only trains SAEs at the residual stream" — [arXiv 2606.26620](https://arxiv.org/html/2606.26620v1). The same paper's related-work section also says Qwen-Scope released SAEs for "each layer and sublayer", which contradicts its own appendix and the release.
- Training: "We train all SAEs sampled from in-house pretraining data". Top-k rule with k ∈ {50, 100}. Auxiliary loss weight 1/32 to reduce dead features. The training code cites Marks et al. `dictionary_learning`. The authors say almost all SAEs have a "negligible" number of dead features — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- `SAE-Res-Qwen3-30B-A3B-Base-W128K-L0_100`: base Qwen3-30B-A3B-Base, residual stream, layers 0–47, d_sae 131,072, d_model 2,048, 64×, k = 100. `W_enc (131072, 2048)`, `W_dec (2048, 131072)`, `b_enc (131072,)`, `b_dec (2048,)`. Same caution clause. The card reports no metrics or training-data details — [HF card](https://huggingface.co/Qwen/SAE-Res-Qwen3-30B-A3B-Base-W128K-L0_100)

### Inferences
- "Up to 128K" is right: only the two MoE "wide" groups reach 131,072. The 80K figure for 27B is 81,920 (16 × 5,120).
- "Instruct" for Qwen3.5-27B means the released post-trained `Qwen/Qwen3.5-27B`. The HF API lists no `Qwen3.5-27B-Base` repo, only Qwen3.5-27B, -FP8 and -GPTQ-Int4 — [HF API search](https://huggingface.co/api/models?author=Qwen&search=Qwen3.5-27B). That is probably why the 27B SAE was trained on the post-trained model, but the paper gives no reason.

### Gaps
- I found no per-SAE variance explained, FVU, delta-LM-loss or dead fraction in the parts of the paper I could read, or on any card. Mark reconstruction quality as unreported or unverified.
- Unverified: whether "thinking" vs non-thinking chat-formatted data was part of the 27B SAE's training distribution. The paper says only "in-house pretraining data".

## Qwen3.5-27B specifics: repos, files, checkpoint, licence

### Takeaway
There are two repos (k = 50 and k = 100). Each holds 64 fp32 `.pt` files of about 3.36 GB, roughly 215 GB per repo. The SAEs were trained on the post-trained `Qwen/Qwen3.5-27B`. The card copy wrongly calls it a "base model". The LICENSE file is Apache 2.0, the card metadata says "other / qwen", and the card adds a restrictive "Caution" use clause.

### Cited Findings
- `config.json` (L0_50): `model_type "topk_sae"`, `base_model "Qwen/Qwen3.5-27B"`, `d_model 5120`, `d_sae 81920`, `k 50`, `num_layers 64`, `layers 0..63`, `hook_point "resid_post"`, `dtype "float32"`. L0_100 is identical except `k 100` — [L0_50 config](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/config.json), [L0_100 config](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_100/blob/main/config.json)
- Files: `layer{n}.sae.pt` (n = 0–63), each a dict with `W_enc (81920, 5120)`, `W_dec (5120, 81920)`, `b_enc (81920,)`, `b_dec (5120,)`. `layer0.sae.pt` is 3,355,793,777 bytes. The repo also holds `README.md`, `LICENSE`, `config.json` and `app.py` (85 KB Gradio demo) — [HF tree API](https://huggingface.co/api/models/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/tree/main); [HF card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)
- Reference encoder in the card: `pre_acts = residual @ W_enc.T + b_enc`, keep the top-k values, zero the rest (no ReLU, no `b_dec` subtraction before encoding in the snippet). The residual is captured by a forward hook on `model.model.layers[LAYER]`, and the model is loaded in float32 — [HF card README](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/README.md)
- Checkpoint: the paper says the 27B SAEs are trained on the instruct variant — [arXiv HTML](https://arxiv.org/html/2605.11887v1). The card table says "Base model | Qwen3.5-27B" and links to the post-trained repo. It also says "For most of the situations, using SAEs trained on base models to explore the internal process of post-training checkpoints is also reasonable." This is boilerplate shared with the Base-trained cards — [HF card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50). `Qwen/Qwen3.5-27B` itself is tagged apache-2.0 and image-text-to-text, created 24 Feb 2026 — [HF API](https://huggingface.co/api/models/Qwen/Qwen3.5-27B)
- Licence: the card metadata gives `license: other`, `license_name: qwen`, `license_link: .../blob/main/LICENSE` — [HF API](https://huggingface.co/api/models/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50). The linked LICENSE file is the plain Apache License 2.0, "Copyright 2026 Alibaba Cloud" — [LICENSE](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/LICENSE)
- Caution clause, verbatim from the README: "It is strictly prohibited to use interpretability tools for non-scientific research purposes to interfere with model capabilities, or to fabricate, generate, and disseminate harmful information that violates public order, good morals, and socialist core values, including pornographic, violent, discriminatory, or incendiary content. Violators will have their authorization automatically terminated and shall bear all legal liabilities arising therefrom. The right of final interpretation of this statement belongs to the project owner." — [HF card README](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50/blob/main/README.md)
- Usage: 546 downloads for L0_50 and 427 for L0_100 at time of check. One Space uses the L0_50 SAE: `devon7y/rat-qwen` — [HF API](https://huggingface.co/api/models/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50); [HF card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)

### Inferences
- The earlier note said the instruct claim was "unconfirmed". The paper confirms it, and the lack of any Qwen3.5-27B-Base repo supports it. The card's "base model" wording is the HF `base_model` field and template text, not a statement about the training checkpoint.
- The clause reads as "using interpretability tools for non-scientific research purposes to interfere with model capabilities" is prohibited. Its grammar can also be read as banning all non-scientific use. Its legal relation to the Apache 2.0 LICENSE is unclear. A primer should quote it, not paraphrase it.
- Memory: one fp32 layer file is about 3.4 GB. W_enc and W_dec are each 81,920 × 5,120 × 4 bytes ≈ 1.68 GB. Hooking a few layers is practical. All 64 layers is about 215 GB on disk.

### Gaps
- The README does not say whether the `resid_post` activations used in training came from chat-templated or thinking-mode text.
- I found no stated activation normalisation or scaling for the 27B SAE.

## Tooling: Neuronpedia, SAELens, demos, explanations

### Takeaway
SAELens has registered all 14 groups since 30 Apr 2026 (`conversion_func: qwen_scope`), which corrects the earlier "no SAELens loader" note. Neuronpedia hosts one Qwen3.5-27B source (`31-qwenscope-res-80k`) with inference not enabled. Qwen ships a Gradio feature explorer and steering demo, but I found no released feature-explanation dataset.

### Cited Findings
- SAELens `pretrained_saes.yaml` has 14 releases: `qwen-scope-3-1.7b-base-w32k-l50/l100`, `qwen-scope-3-8b-base-w64k-l50/l100`, `qwen-scope-3-30b-a3b-base-w32k-l50`, `qwen-scope-3-30b-a3b-base-w128k-l100`, `qwen-scope-3.5-2b-base-w32k-l50/l100`, `qwen-scope-3.5-9b-base-w64k-l50/l100`, `qwen-scope-3.5-27b-w80k-l50`, `qwen-scope-3.5-27b-w80k-l100`, `qwen-scope-3.5-35b-a3b-base-w32k-l50`, `qwen-scope-3.5-35b-a3b-base-w128k-l100`. The 27B entry has `model: Qwen/Qwen3.5-27B`, `repo_id: Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50`, `saes: id layer{n}, l0 50, path layer{n}.sae.pt`. No `neuronpedia` ids are set in these entries — [SAELens pretrained_saes.yaml](https://github.com/decoderesearch/SAELens/blob/main/sae_lens/pretrained_saes.yaml); added in commit #677 on 2026-04-30 — [SAELens commits](https://github.com/decoderesearch/SAELens/commits/main/sae_lens/pretrained_saes.yaml)
- Neuronpedia's Qwen3.5-27B page lists one source, `31-qwenscope-res-80k`, and states "Inference is not currently not enabled for this model" — [Neuronpedia](https://www.neuronpedia.org/qwen3.5-27b). The source page is [31-qwenscope-res-80k](https://www.neuronpedia.org/qwen3.5-27b/31-qwenscope-res-80k), but its content did not render in my fetch.
- `Qwen/QwenScope` Space (Gradio 5.49.1, Apache-2.0 tag, created 29 Apr 2026). It runs `app.py`, described as "SAE Feature Explorer for Qwen3 models, whether pretrain (base) or posttrain (thinking/instruct) models". It defaults to `Qwen/Qwen3.5-2B` with `SAE-Res-Qwen3.5-2B-Base-W32K-L0_100`. Its UI compares two examples across a layer range and has top-K, exclude-first-token and remove-common-tokens options. It takes separate arguments for the model the SAE was trained on and the model being analysed — [Space app.py](https://huggingface.co/spaces/Qwen/QwenScope/blob/main/app.py); [Space README](https://huggingface.co/spaces/Qwen/QwenScope/blob/main/README.md)
- Each SAE repo ships a copy of `app.py`. The 27B card's run command is `--model Qwen/Qwen3.5-27B --model-name-sae-trained-from qwen3.5-27b --sae-path Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50 --top-k 50 --num-layers 64 --sae-width 81920 --d-model 5120` — [HF card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)
- Feature descriptions in the paper come from top-activating contexts or an automatic interpretation pipeline (Paulo et al., 2025b). A judge model scores semantic relevance for the safety features — [arXiv HTML](https://arxiv.org/html/2605.11887v1)
- Community fork: `ZhangShuui/qwen-scope` describes itself as a fork of the Qwen/QwenScope Space (Qwen3.5-2B, width 32,768, Top-K 100) — [GitHub](https://github.com/ZhangShuui/qwen-scope/blob/main/README.md)
- ModelScope mirror collection: [modelscope.cn/collections/Qwen/Qwen-Scope](https://modelscope.cn/collections/Qwen/Qwen-Scope) (linked from the paper, not fetched)

### Inferences
- `sae_lens` `SAE.from_pretrained("qwen-scope-3.5-27b-w80k-l50", "layer31")` should work through the `qwen_scope` converter. I did not run it. The converter's handling of TopK (no ReLU) is unverified.

### Gaps
- Not determined: whether Neuronpedia's layer-31 27B source has auto-interp explanations, and which explainer model produced them. The page content did not render.
- No released feature-label or explanation file found on HF or in the paper.
- No official Qwen GitHub repo found (the QwenLM/Qwen-Scope link 404s).

## Third-party use, evaluation and critiques

### Takeaway
Third-party use so far is small and qualitative. One methods paper steers with a Qwen-Scope 1.7B SAE and raises the base-to-instruct transfer caveat. A concurrent Alibaba paper compares design choices (residual only, proprietary data, base targets) but runs no experiments on Qwen-Scope weights. I found no independent benchmark of Qwen-Scope reconstruction quality.

### Cited Findings
- Riegler & Torpmann-Hagen (SimulaMet/Simula), "Pairwise matrices for sparse autoencoders: single-feature inspection mislabels causal axes", arXiv 2605.03160, 4 May 2026. It uses `qwen-scope-3-1.7b-base-w32k-l50` at layer 20 on post-trained activations. Feature #26221 ("AI self-disclaimer") is non-monotonic under steering: disclaimer rate 87.5% at baseline, 0% at c=+1000, and a "contemplative-philosopher voice" at c=+500. Jointly suppressing #29108, #26221 and #4405 at c=−500 produces placeholder text (7/72 vs 6/2400 for random directions). Caveats quoted: "Two of three SAEs are base-trained and applied to post-trained activations"; "we do not have a matched instruct-trained Qwen SAE to test base-to-instruct ranking transfer head-on" — [arXiv 2605.03160](https://arxiv.org/html/2605.03160v1)
- He et al. (Alibaba AI DATA, with Beijing Institute of Technology), "Discovering Millions of Interpretable Features with Sparse Autoencoders", arXiv 2606.26620, 25 Jun 2026. It calls Qwen-Scope "concurrent work". Its points of contrast: "QwenScope targets the base variants of Qwen3 models"; "Qwen-Scope relies on Qwen3 proprietary pretraining data" (they use FineWeb-Edu instead, for reproducibility); "QwenScope only trains SAEs at the residual stream" (they also cover attention and MLP outputs). The comparison is qualitative only, a design-properties table with no experiments on Qwen-Scope weights — [arXiv 2606.26620](https://arxiv.org/html/2606.26620v1)
- Secondary coverage (not primary; use only for dating): [MarkTechPost, 1 May 2026](https://www.marktechpost.com/2026/05/01/qwen-ai-releases-qwen-scope-an-open-source-sparse-autoencoders-sae-suite-that-turns-llm-internal-features-into-practical-development-tools/), [QevosAgent blog](https://qevos.ai/blog/en/2026-05-01-qwen-scope-analysis.html) (promotional, links a 404 GitHub repo), [riftlab.ai](https://riftlab.ai/pulse/qwen-releases-qwen-scope-sparse-autoencoder-suite-for-qwen-models), [aihola](https://aihola.com/article/alibaba-qwen-scope-release), [Moonlight review](https://www.themoonlight.io/en/review/qwen-scope-turning-sparse-features-into-development-tools-for-large-language-models)

### Inferences
- The main critique points: (1) the paper reports no reconstruction or faithfulness metrics; (2) the training data is proprietary, so the SAEs cannot be retrained; (3) the coverage is residual only; (4) most SAEs are base-trained but are meant for post-trained models. Point 4 does not apply to Qwen3.5-27B, whose SAEs were trained on the post-trained checkpoint.
- The 2606.26620 claim that Qwen-Scope "targets the base variants of Qwen3 models" ignores the Qwen3.5-27B exception.
- Corrections to the earlier notes in `Broken promise probes related work/method_tooling.md` §5:
  - "No SAELens loader" is wrong. SAELens has registered them since 30 Apr 2026.
  - The "trained on instruct" claim is now confirmed by the paper.
  - The "Top-K 100 variant" is confirmed: `SAE-Res-Qwen3.5-27B-W80K-L0_100`.
  - The "30 Apr 2026 release" is roughly right. The repos were created 27 Apr, the Space 29 Apr, SAELens added them 30 Apr, and the paper came out 12 May.
  - The "collection updated 14 May" is confirmed.

### Gaps
- I did not search LessWrong / Alignment Forum specifically. No critique there surfaced in general searches.
- No independent reconstruction or interpretability evaluation of the Qwen3.5-27B SAEs found.
- Not checked: Neuronpedia sources for models other than Qwen3.5-27B.
