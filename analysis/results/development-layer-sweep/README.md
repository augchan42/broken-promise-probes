# Four-game exploratory probe

The A100 sweep is now complete. Reasoning-end layer 2 raised mean AUROC from 0.615 to 0.700 across four development folds. With the same text baseline, the strongest prompt-end layer reached 0.682. The four development games supplied the exploratory selection. Run report and scores

The later CPU re-score adds blinded reasoning annotations to the baseline. Layer 2 caught nine breaches in 24 reviews, compared with seven for either the enhanced baseline or its prompt-end activation control. The gain did not clear the prespecified shuffle reference.

The difference-of-means sweep repeats the four-game comparison with a single activation direction per layer. It matches the full logistic probe's layer 2 shortlist count with the same context.

The original attempt reached the CPU text baseline while A100 capacity was unavailable. The five reserved natural games stayed sealed.

## Development folds

The blinded message audit yielded 75 kept and 15 broken commitments from four 20-round games. These 90 cases span 28 ordered sender–recipient pairings. The test fold is one whole game. The other three games train the model and fit the vocabulary and feature scales. All outcomes refer to the audited same-round commitments. The text baseline includes the system and user prompts with board and inbox information, sender identity, token lengths, and any reasoning available at the cutoff. The outbound message, eventual recipient, and subsequent orders are excluded from the features.

| Information available | Mean AUROC | Mean average precision | AUROC with matched-width noise | Average precision with matched-width noise |
| --- | ---: | ---: | ---: | ---: |
| End of prompt | 0.525 | 0.322 | 0.506 | 0.281 |
| Halfway through reasoning | 0.613 | 0.386 | 0.603 | 0.379 |
| End of reasoning before the message | 0.605 | 0.384 | 0.613 | 0.387 |

Per-game scores and hashes record the four folds and all three cutoffs. The game folds have 5/30, 4/24, 2/17 and 4/19 broken commitments. Each game gets equal weight. With four games, shared state pairings and 15 breaches, these are descriptive scores. The largest gain over the baseline across layers at reasoning halfway or reasoning end will be a candidate for a later independent test. Prompt-end activations will help check whether any gain already appears before the model writes its reasoning. A gain would show an improvement over this specific text baseline.

PR #8 controls for the four-game sweep records the chronology correction, the blinded intent review inputs, and which controls can use the final recipient. The activation comparison is pending.

The updated baseline reads the power balance and legal move list from the exact pre-message prompt. It adds absolute ownership and center counts, then adds ownership from the sender's perspective, the sender's unit locations, and reachable targets grouped by terrain and ownership. The structured inputs use the public board fields visible to the model. The board vocabulary is fitted on the three training games in each fold. Each of the two board feature groups is scaled to unit length per example. The activation comparison will use this combined baseline at the same three cutoffs.

| Information available | Text only AUROC / AP | Text and absolute board AUROC / AP | Text and both board views AUROC / AP |
| --- | ---: | ---: | ---: |
| End of prompt | 0.525 / 0.322 | 0.507 / 0.314 | 0.509 / 0.315 |
| Halfway through reasoning | 0.613 / 0.386 | 0.616 / 0.387 | 0.622 / 0.388 |
| End of reasoning | 0.605 / 0.384 | 0.610 / 0.385 | 0.615 / 0.386 |

These are means over four game folds. The sender-relative features added a small gain over the absolute board features at both reasoning cutoffs. The full board baseline scored below the original text baseline at prompt end. Board baseline scores

## Blinded reasoning review

Three reviewers split 90 excerpts per cutoff. They completed the halfway review before opening the end excerpts. The review was frozen and hashed before joining the commitment scope and validated orders. The join counted only current-round intent about legal moves covered by the promise.

| Scope-matched finding | Reasoning halfway | Reasoning end |
| --- | ---: | ---: |
| Planned attack followed by a kept promise | 0 of 75 | 0 of 75 |
| Stated avoidance followed by a prohibited move, first pass | 3 of 15 | 6 of 15 |
| Stated avoidance followed by a prohibited move, stricter second review | 1 of 15 | 4 of 15 |

The second review mixed the nine first-pass candidates across cutoffs with seven other excerpts. A different reviewer saw the reasoning only and required a settled tactical choice, with exact supporting text. The strata in the JSON reflect the original review across all 180 excerpts. The stricter check covers the first-pass candidates and comparison excerpts. The four end-of-reasoning cases give examples of stated plans diverging from orders. Whether new information changed those plans remains a separate question. Review counts and hashes

## Checkpoint and context

The separate player perspective test stages multiple exact views of each saved board to compare named ownership with the acting player's perspective.

The archived config and weight index match the SHA-256 hashes recorded during full-game generation. The config specifies 64 text blocks, with 48 linear-attention blocks, 16 full-attention blocks and 5,120 hidden coordinates. The weight index independently contains text blocks 0 through 63 and a separate draft head. The earlier synthetic A100 replay `qwen35-synthetic-1794191065` used the same four pinned metadata files and recorded post-block activations of shape `[30, 3, 64, 5120]` with passing replay parity. Its capture receipt SHA-256 is `b2f46da5672f6bbc34788254a03c5e49c62a72463629b7d5800b27dbbb8445ea`. The development capture now also checks that each block's hook fires exactly once per forward. [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-27B)

The game launcher set vLLM's request limit to 32,768 tokens. This kept the serving configuration consistent with the preceding batches on a single GPU. The longest recorded request in the four games was 10,884 tokens including output. The longest staged replay prefix is 9,290 tokens. The native model limit is 262,144 tokens and the documented extension uses YaRN. Longer live sequences require more memory for attention history. The replay uses the original saved tokens and does not depend on the vLLM server limit. [Qwen context extension](https://huggingface.co/Qwen/Qwen3.5-27B#processing-ultra-long-texts) · [vLLM memory configuration](https://docs.vllm.ai/en/stable/configuration/conserving_memory/)

## Reproduction

Run from the repo root using the tokenizer that matches the generation archive. Each output path must be new.

```sh
python -m analysis.development_layer_sweep stage \
  --run gpu/results/runpod/qwen35-four-cap21-j7gxa77o2r7cvw \
  --tokenizer /path/to/pinned/tokenizer.json --out /path/to/staged
python -m analysis.development_layer_sweep baseline \
  --staged /path/to/staged --out /path/to/board-baseline.json
```

The case-level annotations and stricter review are in the ignored local development directory. To reproduce the review summary from those files, run the following with a fresh output path.

```sh
python -m analysis.development_intent_review summarize \
  --run gpu/results/runpod/qwen35-four-cap21-j7gxa77o2r7cvw \
  --staged /path/to/staged --review /path/to/blinded-intent-review \
  --checks /path/to/blinded-intent-review/strict-checks.json --out /path/to/intent-review.json
```

On the A100 with the existing volume mounted at `/workspace`, put the staged `prefixes.jsonl` alongside the repo paths `gpu/capture_promise_probe.py`, `gpu/run_development_layer_sweep.sh` and `activations/extract.py` under the input directory. Build `model.sha256` there from `stage-manifest.json`'s `model_metadata_sha256` mapping, with one line per file in `digest  filename` format. Keep the labels and prompts in `records.json` local. Create a unique persistent run directory on the volume. Run the launcher with the deadline set to 55 minutes after pod launch. It writes a ZIP and checksum beside the run directory, then stops the pod after five minutes or as soon as it finds `download-verified` in that directory. Create that receipt after downloading and checking the ZIP hash.

```sh
bash gpu/run_development_layer_sweep.sh "$input_dir" "$persistent_run_dir" "$deadline_unix"
python -m analysis.development_layer_sweep score \
  --staged /path/to/staged --capture /path/to/unpacked/capture --out /path/to/layer-sweep.json
```
