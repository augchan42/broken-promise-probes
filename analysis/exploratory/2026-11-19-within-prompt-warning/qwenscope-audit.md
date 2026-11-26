# What QwenScope captures from early order reasoning

The audit uses the saved 270-token snapshots at blocks 51 and 52. Those layers were selected by an earlier comparison on the same four mixed replay positions. We use this audit to generate explanations for that comparison.

## The ranking gain survives reconstruction

| Input to the original fitted predictor | Block 51 | Block 52 | Block 51, uncapped | Block 52, uncapped |
| --- | ---: | ---: | ---: | ---: |
| Text alone | 56.3% | 56.3% | 66.7% | 66.7% |
| Text plus raw activation | 87.5% | 87.5% | 95.8% | 95.8% |
| Text plus QwenScope reconstruction | 87.5% | 83.3% | 100% | 95.8% |
| Text plus what QwenScope left out | 54.2% | 45.8% | 54.2% | 45.8% |
| Text plus five development-selected features | 62.5% | 62.5% | 75.0% | 75.0% |
| Text plus reconstruction after subtracting those five features | 87.5% | 83.3% | 100% | 95.8% |

The dictionaries left roughly 48% of the overall activation variance unreconstructed, yet kept most of the differences along the predictor's direction. On the uncapped pairs, subtracting the reconstruction left 26% of the original squared score difference for each block, using equal position weights. The expectation that the error might help predict the order did not hold here. The five development-selected features reproduced little of the gain, and removing them left the original reconstruction rankings intact. Even the five strongest contributors selected using the uncapped replay pairs reached only 81.3% for block 51 and 77.1% for block 52 when added to text.

## What the features and confound checks show

- Block 51 feature 21004 fired in all four occurrences of one exact whitespace token and nowhere else in the 60 replays. The strongest uncapped candidate in each block appeared in one replay. Block 51 feature 67401 was active on 20 different cutoff tokens, but its contribution favored the breach in one mixed position and the kept order in two. These examples give us plausible formatting and case-specific cues alongside contributions that vary across positions.
- Across the six uncapped pairs ending on the same broad token type, the text and raw-activation rankings both scored 66.7%. Adding the QwenScope reconstruction scored 100% for block 51 and 91.7% for block 52. A simple distinction such as word versus punctuation therefore does not account for all the sparse result. **Zero pairs shared the exact cutoff token**, so a finer wording or position cue remains possible.
- In 17 uncapped pairs across all four mixed positions, neither prefix named a covered territory in the last 32 tokens. Text scored 64.6%. Text plus the reconstruction scored 100% and 95.8%. This weakens a recent exact territory-name explanation. Mentions elsewhere in the reasoning, phrasing and context remain possible explanations.
- The blinded reader marked an explicit choice to enter covered territory in just two of 60 prefixes. None of the five development-selected features in either block fired on either of those two. That reader is imperfect and the positive count is too small to establish how any feature responds to a written choice.

The strongest result is that the dictionaries retain the ranking information this predictor used. The tests of what that information means are still limited to four positions. A controlled follow-up could hold the cutoff token and phrasing fixed while varying whether the model's visible reasoning endorses or rejects the same legal move.

## How the score is decomposed

The QwenScope encoder returns up to 50 active feature IDs and strengths per snapshot. Each feature has a decoder vector that describes its contribution to the reconstructed activation. We multiply each feature's strength by how much that vector points along the existing breach predictor. This gives signed contributions in the predictor's own score units. The sum of those contributions, the decoder's constant offset and the projected reconstruction error reproduces the original activation score.

We keep the text weight and activation weights fixed. We score text with just the reconstructed activation, with just the reconstruction error, and with five features chosen on the development examples. The rankings use equal weight per position and half credit for ties. Five additional features ranked using the replay pairs are descriptive. Candidate firing counts inspect all 60 replay prefixes. Ranking comparisons use 22 pairs across four mixed positions, or 19 when capped runs are excluded. Some pairs share a replay.

The procedure verifies the public checkpoint hashes, reproduces the fixed predictor's input-output relation, cross-checks the encoder with an independent NumPy calculation, and checks that the raw predictor matches the recorded sweep. Sources and captured activations stay local. The score decomposition measures the fitted detector. No Qwen generations or game outcomes are changed. [QwenScope model card](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50) · [Expectations recorded before examining the features](qwenscope-expectations.md)

[Block 51 aggregate results](qwenscope-block51-score.json) · [Block 52 aggregate results](qwenscope-block52-score.json) · Reproducible analysis
