# Test the released FIBS probes on Warring States promises

**Draft, 24 November 2026.** [Issue #71](https://github.com/augchan42/warring-states-promise-probes/issues/71)

## First experiment. Check FIBS on the authors' data

The public Qwen3.5-9B linear and EFC tests matched the authors' saved reference scores within their published numerical tolerances. The 27B BF16 MLX check then replayed 64 of the authors' held-out transcripts with the released weights frozen. Linear reached **0.969 AUROC** and EFC reached **0.996**. This completes the local check. The authors' published full-set results of **0.972** and **0.998** are reference figures from a separate, larger run. [Authors' parity tests](https://github.com/AlignmentResearch/fibs-probes/blob/6cae61deed78157021bf141c69f626881bbd638d/tests/test_parity.py) · [Published 27B validation results](https://huggingface.co/AlignmentResearch/probe-inference-weights#training)

The public reference fixture covers 9B and Nemotron. FAR.AI separately released the exact 5,000 validation transcripts under `fibs_validation`, with the original row IDs, labels, selection manifest and source row digests. The dataset requires Hugging Face access approval and is evaluation-only. The [execution plan](../plans/2026-11-24-fibs-promise-probe-pilot.md#0-check-the-released-probes-on-the-authors-data) records how the 64 rows were selected and rendered through the pinned Qwen template. [FAR.AI validation release](https://huggingface.co/datasets/AlignmentResearch/telling-fibs-eval-transcripts#fibs-validation-rows)

## Question and scope

The remaining design is for a later Warring States transfer experiment.

When Qwen finishes writing a promise, how well do the released FIBS probes rank the risk that it will break that promise in its later orders? On the same cases, does a probe trained on Warring States improve the ranking from a text judge that sees the same transcript?

FIBS was trained to recognize statements the model takes to be false. Our label comes from the later orders. A sincere promise followed by a change of plan can produce a breach. This pilot measures transfer to breach prediction. Evidence about the timing of a stated plan comes from the separate pre-message order design. The earlier AISI trial used different weights and a different readout. [FIBS paper](https://arxiv.org/abs/2610.12445v4) · [AISI result](../../../analysis/results/aisi-probe-zero-shot/README.md)

Use the original board, order menu, messages and token IDs in the saved traces. No new games or agent responses are needed. A compact order menu would change the input and belongs in the same-facts test in [issue #70](https://github.com/augchan42/warring-states-promise-probes/issues/70).

## Data and timing

| Quantity | Frozen choice |
| --- | --- |
| Development | 90 eligible promises from four games. Use these alone to train the Warring States probe and set score scales and alert thresholds. |
| Evaluation | 185 promises, 23 breaches, eight separate games. These games have already been examined, so the comparison is exploratory. |
| Label | Reuse the strict promise scope, legal opportunity and linked valid orders from the earlier comparison. Count an attempted covered move as a breach under that rule. Retain any existing circumstance annotations separately, with unknowns explicit. |
| Primary time | The moment the diplomacy reply is complete, before the later orders. Start from the exact original token chain through the assistant's end-of-turn token. |
| Optional secondary time | The end of the saved order prompt, before Qwen reasons or generates an order. Train and test a separate Warring States readout and compare it with a judge that reads that exact prompt. Any missing own sent messages remain missing on both sides. |

Keep every case, variant and later order with its original game. The five former holdout games are outside this pilot. Freeze the protocol before inspecting any new evaluation scores. Leave the frozen held-out, eight-game and AISI verdicts as recorded. A later confirmation requires independent games and a protocol frozen before scoring them. [Eight-game result](../../../analysis/results/eight-game-reasoning-end/README.md)

## Verify that the released probes can read the game archives

Use official `Qwen/Qwen3.5-27B` at `fc05daec18b0a78c049392ed2e771dde82bdf654` on CUDA in BF16. Verify the files against the model manifest. Pin the loader and its camera-ready weight revision (documented as `05def1c1`) by full commit and artifact hash. Capture the outputs of zero-based decoder blocks **19, 27, 35, 43, 51 and 58**, corresponding to Hugging Face `hidden_states[k+1]` for these blocks. Match the published residual stream before the next block. Apply the released loader and its shipped normalization in float32. Use reference hooks and public fixtures to validate indexing, masks and scores. The earlier MLX captures and sparse cutoff snapshots cannot supply the required full-window BF16 data. [Released loader and activation contract](https://github.com/AlignmentResearch/fibs-probes#activation-contract) · [Weights card](https://huggingface.co/AlignmentResearch/probe-inference-weights)

| Published detector | Exact tokens at promise time |
| --- | --- |
| Linear | One position. The token immediately preceding the recorded assistant end-of-turn token. Use the loader's mean of the six layer scores after each sigmoid. |
| EFC | The released cross-layer probe. Read every token from the final user turn's opening marker through the assistant end-of-turn token, inclusive. Score with the loader's pooled logit. |

Use the original reply with its actual reasoning and answer delimiters. The released probes can score it directly. This is a transfer test on game transcripts, distinct from the paper's sabotage test that adds a question and prefills the answer. At order-prompt end there is no completed order reply for the native FIBS masks. Leave the FIBS cells empty at that optional cutoff. [FAR.AI evaluation setup](https://www.far.ai/fibs) · [Read masks](https://github.com/AlignmentResearch/fibs-probes#building-the-read-mask)

The CPU inventory linked **all 90 development and 185 evaluation replies** to exact prompt and output IDs. All 275 saved answers end in the pinned tokenizer's `<|im_end|>` (248046). One development case used a forced reasoning closure, which its saved answer prefix already includes. The full diplomacy replays total **1,002,538 tokens** with a maximum of **9,440** in one case. Storing six BF16 streams of width 5,120 for every token would take up to **61.6 GB** before metadata. Stream one case at a time, keep only the six final-answer vectors and the frozen scores, and discard the long tensors after scoring. The optional order prompts add **384,394** input tokens. These counts describe saved inputs. Stage 0 still needs to measure GPU throughput, startup, peak memory and end-to-end cost.

**Proposed compute limit.** Allow up to two GPU-hours for verification and timing, then budget at most six additional GPU-hours for the primary recapture. Benchmark a short, median and long development prefix and report the expected cost including startup and storage at the rate actually available. Scope the optional order replay after that estimate. Stop and document the blocker if the artifact contract or the primary budget cannot be met. Reproducing FIBS training would be a separate study with its own budget.

## Comparisons on the same promises

| Method | Inputs |
| --- | --- |
| Released linear and EFC | Frozen weights on the exact windows above. No weight fitting or search over layers, prompts or tokens. |
| Warring States linear | Six vectors at the linear FIBS token. L2-normalize each case's vector within each layer, concatenate in published layer order and divide by the square root of six. Fit L2 logistic regression with fixed `C=1`, an intercept and no class weighting. Fit once on all development games for evaluation. |
| Recipient-view judge | Verified board facts visible to the recipient, first-pass correspondence visible to that recipient, and the promise the recipient receives. Exclude other private exchanges and infer no same-pass message ordering. |
| Matched-transcript judge | The sender's exact instructions, prompt and full reasoning and reply through the primary cutoff. Include the recorded answer as written. Keep the prediction question and judge model fixed across the two views. |
| Judge plus probe | Show each judge's raw score first. For each probe, map its score and the judge's score to their own development percentiles and average the two. Use midranks for ties. Estimate the domain probe's development percentiles from predictions that hold out one whole development game at a time. Use no fitted classifier on top of the judge. |

Use the verified model recorded by the earlier judge receipt, subject to availability and permission for any new transfer of private text. A saved score can stand in for a judge call only if the model and exact input hash match. Otherwise use the same approved judge for both views, with a pinned model ID. Ask the judge for the probability that the sender's submitted orders break the commitment during this round. Let it infer scope from the visible text. Record its estimate directly. A prior approval limited to inputs with reasoning removed does not cover this matched transcript. A local judge can supply both views if its identity and budget are frozen before scoring.

## Reporting and interpretation

- Lead with equal-game averages and the paired AUROC change from adding the domain probe to the matched-transcript judge. Report the kept–broken-pair-weighted AUROC alongside it. Give average precision, cases, breaches, base rates and changes by game. Use a paired whole-game bootstrap over the precomputed game metrics for descriptive 95% intervals and report leave-one-game-out sensitivity. Give the contributing game counts for every metric.
- Report full recall versus false-positive-rate and catches versus review-effort curves. Include an illustrative development operating point targeting at most **10%** false alarms among kept promises, alongside the realized rate on the eight games. Use a strict threshold comparison and handle boundary ties conservatively. The point is descriptive and supports comparison with the full curves. Kept is an outcome label. Low false-alarm targets such as 1% are poorly resolved by this development set.
- Use one aligned set of cases for comparisons. Reconcile missing or invalid outputs and report counts and causes. A partial comparison uses a labeled common subset and states which games and outcome classes are affected. Report whether gains depend on one game, reasoning length, or easy attack opportunities. Fix any slice definitions using development data.
- Weak FIBS transfer still permits the domain comparison. A gain over the recipient-view judge can reflect its reduced access to information. A gain over the matched-transcript judge measures added prediction in this setup. Either result can occur without a reliable indicator of deliberate deception. Stop after the exploratory report.

## Run records

Keep exact prompts, traces, labels, activations, and individual scores local or in the existing private R2 storage. Use an immutable manifest with the protocol and code revisions, source archive hashes, both original score artifact hashes, cohorts, model and tokenizer artifacts, weight revision and file hashes, loader and backend versions, dtype, hardware, mask construction, normalization, judge model and request hashes, metric definitions, thresholds, bootstrap seed and resource budget. The private one-time score and public aggregate have separate published checksums. Verify each against its own receipt. Earlier follow-up receipts

For each case keep the private source and game IDs, linked calls, label provenance, exact input and token hashes, window indices and mask hash, selected vector and score checksums, judge view provenance, status and exclusion reason. Record UTC start/end, runtime, memory, retries and failure cause per attempt. Write case checkpoints atomically and resume only with matching inputs and settings. Publish the frozen protocol, compatibility finding, aggregate outcomes and resource use. Keep case records out of Git and the issue.
