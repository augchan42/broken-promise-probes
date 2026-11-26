# FIBS and Warring States promise-probe implementation plan

> Use the executing-plans or subagent-driven-development skill to implement these tasks.

**Status.** Draft for [issue #71](https://github.com/augchan42/warring-states-promise-probes/issues/71), 24 November 2026.

**Goal.** Check the released FIBS probes on the authors' data before the separate Warring States transfer experiment.

**Architecture.** One CPU module stages token and judge inputs, verifies receipts, and scores private checkpoints. A CUDA runner uses the existing model loader and public FIBS scoring package. Keep the compatibility report usable even if capture stops before the full comparison.

**Stack.** The repo's Python environment for staging and analysis. A separate pinned CUDA PyTorch/Transformers environment for the official BF16 model. The released `probe_inference` loader and the existing checkpointed text judge.

**Spec.** [Experimental design and data contract](../specs/2026-11-24-fibs-promise-probe-design.md)

## 0. Check the released probes on the authors' data

- [x] Run the authors' Qwen3.5-9B linear and EFC parity tests on their 32 reference rows. Both passed on macOS arm64 with Python 3.12.13 and PyTorch 2.14.0. Maximum absolute differences were **7.19e-8** for the final linear score (tolerance **1e-6**) and **4.20e-5** for the EFC logit (tolerance **5e-5**).
- [x] Load the released 27B linear and EFC weights on CPU. Both loaded and named the official base revision `fc05daec18b0a78c049392ed2e771dde82bdf654`, blocks 19, 27, 35, 43, 51 and 58, and their respective one-token and full-turn read windows.
- [x] Download the exact 5,000-row validation set, holdout manifest and source-row digests from FAR.AI's separate evaluation release. Keep the downloaded inputs in the local access-controlled cache. [Validation rows and provenance](https://huggingface.co/datasets/AlignmentResearch/telling-fibs-eval-transcripts#fibs-validation-rows)
- [x] Implement the replay runner in `gpu/reproduce_fibs.py`. It validates the pinned split, checks model and probe files, scores the two published read windows, saves each result as it finishes, and reports coverage and AUROC.
- [x] Inventory the gated split using the pinned tokenizer. All 5,000 validation row IDs and source digests match the authors' manifests. All rows render locally, totaling 7,586,974 tokens. The largest input is 133,164 tokens. Decode JSON tool arguments for Qwen's template and use the first rendered token of the final user turn, including grouped tool responses where Qwen renders them as a user turn. The release supplies source transcripts. If the authors provide their tokenized inputs, check parity with those IDs.
- [x] After approval of the exact player view, replay the first four rows per class as a local check. The cached BF16 MLX conversion at `5ad6b65ac842d2d023621f1e892c49df478f2dce` ran all eight rows and produced finite scores from both released probes. The run covered 3,741 tokens in 31.0 seconds of scoring and 51.0 seconds including setup. This checks the complete data-to-score path on the Mac. It leaves the official CUDA benchmark pending.
- [x] Run a 64-row MLX check with the same frozen weights and read windows. Select 32 evenly spaced token-length midquantiles per label and break length ties by source row ID. Replay transcripts above 1,024 tokens in contiguous 1,024-token chunks with model caches. All 64 rows scored. Linear AUROC was **0.96875** and EFC AUROC was **0.99609375**. The run covered 71,099 tokens, with a median of 570 and a maximum of 7,503. It took about **14.5 minutes** end to end, including one restart after row 46 with a 2 GiB Metal allocation cache limit. Completed row scoring took 12.9 minutes. The manifest SHA-256 was `5ff60e60b463e45fb541ea245dcb23dee183ce3aea077789825450063940f96c`. A straight extrapolation gives about 23 hours of scoring for all 5,000 rows. It does not account for the longest transcript, at 133,164 tokens, or for changes in throughput.

**Stopping point.** The 64-row MLX check completes this stage. Its high AUROCs give us confidence that the released probes separate labeled honest and deceptive answers on the sampled FIBS transcripts. An exact comparison with the authors' full validation AUROCs would use all 5,000 rows and match their CUDA activation capture. That comparison is optional and outside the current plan.

### Public run receipt

| Artifact | Revision or hash |
| --- | --- |
| Authors' scoring code | `6cae61deed78157021bf141c69f626881bbd638d` |
| 9B activation and score fixture | `14382a5fe404dc1ce7a13edbacaecd3964024353` |
| Fixture `reference.json` SHA-256 | `c6cb35958543166785813c26cf9e63e46646f188927e90e55e6236850577e57d` |
| 9B weights used by the fixture | `22a7a341078ba1722cfad73ef7e40bdc25aa74c2` |
| 27B weights loaded locally | `05def1c13a70237cda3b717d785813918b8a22fa` |
| 27B linear and EFC file inventory SHA-256 | `fef42830eb86c01eade00649e164523ec056cf4144c1320a44a7fcdecb7f78fa` |
| FIBSv1 validation source release | `65dccf12934620bfe01db665ea3d7d0e3c9f1355` |
| Published validation parquet and holdout manifest repository | `AlignmentResearch/telling-fibs-eval-transcripts` @ `97d20337785f68062befa9324d97d7c81063b0c2` |
| Validation parquet SHA-256 | `251151bff25e0046f14254a310d4cbe0a900d4c23f09596a6d7780fead0d915c` |
| Holdout manifest SHA-256 | `10dd0a41e2ca28890c43699b2eb6de8f45eed34c6ef09e9e79ce4f9e24a0153a` |
| Validation row-digests manifest SHA-256 | `0665c20ffa02dd3702cf7f0a79acd5915484e7dfea640f36a18b22340b3973cc` |
| Rendered token IDs, labels and bounds inventory SHA-256 | `e7470c093b1a257e2de5de505604d7cc2c858c791fd06e614ff8b5ec912d3e6e` |

The 27B inventory hashes a UTF-8 list of the 16 probe files. Sort by repository-relative POSIX path and emit each line as the file's hex SHA-256, two spaces, the path, and a newline.

From a checkout of the pinned authors' repository:

```sh
OMP_NUM_THREADS=2 uv run --python 3.12 --locked --extra hub \
  pytest -q -s tests/test_parity.py -k 'qwen3.5-9b and (linear or efc)'
```

The parity run uses the authors' saved 9B activations. The 27B result above uses the 64-row MLX sample.

### CUDA commands for an optional full reproduction

Use an environment with NumPy, Hugging Face Hub, Transformers, PyArrow, CUDA PyTorch and `probe_inference` from the scoring code revision above. The inventory only needs the pinned Qwen metadata and tokenizer directory. Replay also checks every official model shard. Use authorized Hugging Face access or the verified local cache. The runner reads the validation parquet and its two provenance files at the recorded revision and writes outputs to the specified directory. The replay requires the owner's approval of the exact player view.

```sh
python -m gpu.reproduce_fibs --model "$metadata_dir" --out "$run_dir/inventory" --inventory
PLAYER_VIEW=fibs-27b-validation python -m gpu.reproduce_fibs --model "$model_dir" --out "$run_dir/pilot" --pilot-per-class 4
PLAYER_VIEW=fibs-27b-validation python -m gpu.reproduce_fibs --model "$model_dir" --out "$run_dir/full" --max-seconds "$wall_seconds"
```

Repeat the full command with the same environment, inputs and output directory to resume. The time limit is checked between rows. Save the run manifest and aggregate outside Git with the gated material. Publish only aggregate numbers and artifact revisions.

## Later Warring States transfer

The tasks below are for a separate experiment. Start with the frozen published probes and fit the Warring States probe only after those scores exist.

## Files and entry points

| Path | Responsibility |
| --- | --- |
| `analysis/fibs_promise_pilot.py` | CPU subcommands `stage`, `judge` and `score`. Reuse archived call links, case manifests and judge checkpoint mechanics. |
| `gpu/capture_fibs_promise.py` | CUDA subcommands `preflight` and `capture`. Pin the model, validate the shapes and masks, run frozen probes, save only retained vectors and scores. |
| `analysis/test_fibs_promise_pilot.py` | Synthetic tests for token boundaries, input visibility, incomplete checkpoints, game splits, metrics and privacy of reports. |
| `~/tara-runs/fibs-promise-pilot-2026-11-24/` | Private staged case records, protocol copy, checkpoints, readouts, scores, and manifests. |
| `analysis/results/fibs-promise-pilot/{README.md,aggregate.json}` | Compatibility decision, resource cost, and score summaries if the pilot proceeds. |

Use `python -m analysis.fibs_promise_pilot` or `python -m gpu.capture_fibs_promise` from the repository root. CPU staging takes `stage --runs-root "$runs_root" --out "$run_dir"`. GPU commands use `--out "$run_dir" --model "$model_dir" --probe-dir "$probe_dir"`. Judging uses `judge --out "$run_dir" --view recipient` or `--view matched`. Scoring uses `score --out "$run_dir"`. Run CPU fixtures with `python -m unittest analysis.test_fibs_promise_pilot`. A worker lock and private output directory are shared requirements.

## 1. Freeze cases and exact inputs on CPU

- [ ] Implement `stage(runs_root: Path, out: Path) -> dict`. Check the two eight-game archive hashes, the legacy development archive and audit receipts, the development records hash, and the two distinct frozen score hashes from `qwen-scope-score.json`. Check test case, game and label counts against the private one-time artifact and its linked records. Keep the held-out and AISI aggregate checksums in the manifest as well. Reuse `activations.extract.linked_ids` to join the thinking, optional closure, and answer segments exactly once. Verify the routed message against the archived successful response and the strict label against its linked valid orders. Record a private case ID, game grouping and provenance for every row.
- [ ] Implement `build_masks(ids, user_start, answer_start, eot) -> dict`. Locate the final user boundary from the archived message structure and verified tokenizer framing. Verify that the recorded first user-turn token and the final end marker match the pinned tokenizer and that no guessed boundary from untrusted message text enters the mask. Use the documented inclusive span for EFC and the penultimate token for linear. Store original IDs, boundaries, mask hashes and receipt references in `staged/cases.jsonl`. Reject a missing end marker, response mismatch, empty answer or duplicate case, with a private cause. Test the one known forced-close shape, answer continuations, embedded delimiter-like text, and wrong/off-by-one token positions.
- [ ] Implement `judge_view(case, view) -> dict`. Build the recipient packet from verified shared facts and the first-pass messages visible to that recipient plus the new promise. Build the matched packet from the exact sender transcript through the end of the reply. Keep the same question, roles and output format. Save a field-level visibility record, exact serialized request and request hash per packet privately. Use synthetic cases with third-party private messages and later orders to prove neither packet leaks future data and only the matched packet contains sender instructions and reasoning.

## 2. Run compatibility and price the replay

- [ ] Reuse the public loader, 27B weight pins and parity receipt above. Verify the full base snapshot from `portable/models.json` and record the 27B file hashes and exact CUDA environment in the transfer compatibility receipt.
- [ ] Implement `preflight(out: Path, model: Path, probe_dir: Path) -> dict`. Use the CUDA BF16 text-backbone loading path in `gpu.capture_promise_probe.load_text_model`. Choose three development inputs by archived length, before reading scores. On a short public or synthetic prefix compare the six hook outputs against independent `output_hidden_states[k + 1]` in the same BF16 model. Freeze whether the backend uses Transformers directly or a validated vLLM equivalent. Check that both masks produce their expected finite output and that a missing, extra or shifted block fails the adapter test. Verify repeated forward and stored-vector scores on the fixed inputs. Report the backend actually checked. Keep the environment and mask contracts fixed for the full capture.
- [ ] Measure startup, min/median/max throughput, peak memory, disk and wall time. Project cost using the actual resource rate and **1,002,538** diplomacy input tokens. Limit preflight to **two GPU-hours** and the main run to **six additional GPU-hours**. Estimate the cost of up to **550** primary judge calls from both packet lengths. Freeze the judge budget and applicable model/privacy approvals before issuing real requests. The additional **384,394** order-prompt tokens and up to 275 judge calls belong in the optional estimate only. Report the stop reason if the primary run cannot fit or the compatibility check fails.
- [ ] Freeze the protocol and stage receipt before main scoring. Pin the cohort, windows, model, architecture, classifier settings, judge templates, bridge between scores, threshold and metrics. Confirm which judge scores are reusable by exact hashes, and prepare the exact local player views for model runs covered by the project's approval gate. Run only phases with the required input authorization. Keep the authored protocol and approvals separate from private request content.

## 3. Score the released probes, then train the Warring States probe

- [ ] Implement `capture(out: Path, model: Path, probe_dir: Path) -> dict`. Replay the exact IDs through the frozen backend with no answer generation. Capture the six post-block streams for one transcript, apply the frozen linear and EFC scores on their separate masks, then discard the sequence activations. Save the six BF16 penultimate-token vectors, scores and a private receipt atomically per case. Stop at the measured budget. Validate each completed checkpoint when resuming. Preserve failed attempt metadata and retry only transient failures with the same inputs. Freeze the completed released-score receipt before fitting the domain probe, without inspecting evaluation performance.
- [ ] Run the two primary judge views on the same cases, with no tool access or conversation carryover. Save parsed estimates, model ID, prompt and response receipts, times, token usage and cost. Reuse raw saved estimates only if the request hash and model match. Preserve failed results and invalid output reasons. Keep both judge views and the published probe scores available on a common case set. If one arm cannot be completed, document the blocker and report the finished arms with coverage.
- [ ] Implement `fit_domain(dev_rows) -> scorer`. Normalize each of six vectors by its own L2 norm, reject nonfinite or zero vectors, concatenate in the fixed layer order and scale by `sqrt(6)`. Fit the fixed logistic regression on development only, then score the evaluation rows. Compute development calibration scores by four whole-game holdouts using the same training settings. Freeze input hashes, held-in game IDs, model settings and output coefficients privately. Test that changing evaluation labels has no effect on fitted coefficients or calibration. Use the same design independently at order start only if that addition is in budget.

## 4. Score metrics and write the report

- [ ] Implement `score(out: Path) -> dict`. Join scores by case and game. Use existing AUROC and average precision functions. Publish direct judge scores, released probe scores, domain scores, and fixed judge-plus-probe percentile averages. Midrank each value against development scores as `(count_less + 0.5 * count_equal) / n_development`. Select a strict `score > threshold` alert rule using the kept development scores. In descending order choose the score at zero-based index `floor(0.10 * number_kept)`. Report realized false alarms and recall, all tied-score curve points, equal-game and pair-weighted AUROC, game-level gains, and average precision. Leave undefined per-game rank metrics blank with the reason.
- [ ] Run 10,000 paired bootstrap draws of evaluation games using seed `20261124` and leave one evaluation game out at a time for sensitivity. Reuse the same resampled games for all methods. Predeclare development-median splits for reasoning length and number of legal breach destinations. Include class counts and missing cases for every method. Test that tied scores cannot raise the development false-alarm rate above its stated target, and that a game without both outcomes is counted in coverage without a fabricated AUROC.
- [ ] Recompute aggregate totals from the private checkpoints and verify the frozen files against the stage receipts. Publish the compatibility and cost finding, coverage, tables and curves, and the outcome-versus-intent interpretation. Use numbers and anonymous game slots in the shareable report. Verify that no private prompt, activation, case-level score or outcome escaped into the report. Record any stage that stopped and why, then close out the pilot.
