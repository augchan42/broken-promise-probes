# Reading more of the order reasoning helped predict a breach

> **Public copy.** This folder is copied from the private working repository, which holds the game data. The Python scripts are not included because they import modules that are only there. The JSON files hold aggregate scores only.

On four saved positions where Qwen sometimes kept and sometimes broke the same promise, the text reader's ranking score rose from **56.3% after 270 reasoning tokens to 87.5% after 2,238**. Adding block 31 at the early reading lowered the score to **33.3%**. The primary comparison failed its replication rule. The original eight-game test also retains its frozen fail verdict.

The exploratory sweep identified block 51 as a candidate at 270 tokens. Its fixed probe raised the text reader's score from **40.0% to 46.7%** on fresh replays. The gain came from one position, and removing it made the gain negative. [Fresh replay results](block51-fresh-results.md)

## Which blocks were tested

The earlier eight-game study swept all 64 blocks on the evaluation games at the end of Qwen's reasoning **before it sent the promise**. Block 36 gave the largest observed gain over the baseline that included a reasoning monitor, +0.031 AUROC versus +0.025 for block 31. Both added two catches at the same review budget. No block reached the original +0.050 margin. [Eight-game sweep and plot](../../results/eight-game-block-sweep/README.md)

This replay study looks **after the promise, while Qwen chooses its orders**. We saved all 64 blocks and ranked all of them at 270 tokens using only the four development games. Block 31 was fixed as the original comparison. Block 2 was the highest-ranked alternative, selected before joining the replay scores to outcomes. Those were the two blocks in the original replay comparison. The follow-up below evaluates every block at both cutoffs. [Development scores for all 64 blocks](score.json)

## What the percentages mean

Take two replays of the same position, one ending in a breach and one in a keep. Give the monitor one point if it assigns higher risk to the breach and half for a tie. Compute a percentage within each position, then average the four percentages equally. Chance gives 50%. These percentages measure how well a monitor ranks pairs. They do not estimate the chance that any one promise will be broken.

| What the monitor could read | 270 tokens | 2,238 tokens | 270, excluding capped runs | 2,238, excluding capped runs |
|---|---:|---:|---:|---:|
| Text | 56.3% | 87.5% | 66.7% | 91.7% |
| Block 31 | 66.7% | 33.3% | 75.0% | 33.3% |
| Text and block 31 | 33.3% | 83.3% | 25.0% | 87.5% |
| Block 2 | 60.4% | 77.1% | 68.8% | 85.4% |
| Text and block 2 | 56.3% | 91.7% | 68.8% | 91.7% |

## Comparison with the recorded expectations

We expected the longer text to help more than adding early block 31. Reading more text gained 31.25 percentage points on average. The text ranking improved in three positions and fell in one. Adding early block 31 lost 22.92 points and lowered the score in all four. The combined monitor had learned to treat a higher early block 31 score as evidence *against* a breach. On the development games the activation alone had ranked breach above keep only 9.3% of the time under leave-one-game-out scoring. That direction failed to transfer to the replay comparisons. The fitted weights explain how the combination could do worse than either input.

Block 2 was the highest-scoring eligible alternative in the development sweep (55.2%). Adding it tied text early. At the later reading, the combined monitor reversed one wrong ranking involving a capped replay. It also broke two text-reader ties, one in each direction. The tie changes canceled in the mean across positions. Excluding capped runs erased the net gain. There were zero broken–kept pairs at either cutoff where the blinded stance reader marked both replays as considering both options and endorsing neither. We cannot answer that part of our prediction.

A private review of the reversed pair found both replays discussing a territory covered by the promise within 50 tokens of the reading point. The replay that later broke the promise landed on a word expressing what the player ought to do. The two local excerpts were classified as considering an option. Block 2 alone ranked the kept replay higher, as did the text reader. The combined monitor gave the block 2 score a negative weight and reversed the ranking. The difference in phrasing is a plausible cue. This comparison cannot identify what drove the block score.

| Position | Breaches / keeps | Early text | Early text + 31 | Late text | Late text + 31 | Late text + 2 |
|---|---:|---:|---:|---:|---:|---:|
| A | 3 / 2 | 41.7% | 33.3% | 83.3% | 83.3% | 100% |
| B | 2 / 3 | 83.3% | 50.0% | 66.7% | 50.0% | 66.7% |
| C | 4 / 1 | 25.0% | 0% | 100% | 100% | 100% |
| D | 3 / 2 | 75.0% | 50.0% | 100% | 100% | 100% |

## Follow-up sweep on all 64 blocks

The original block comparison missed a larger early gain at other depths. At 270 tokens, text plus block 51 or 52 scored **87.5%**, versus **56.3%** for text alone. The gain appeared in three of four positions and remained positive when any one position was removed. Excluding capped runs gave **95.8%** versus **66.7%**.

| Reading and cohort | Text alone | Text plus best block | Mean gain | Blocks beating text |
|---|---:|---:|---:|---:|
| 270 tokens, all scored replays | 56.3% | 87.5% (51, 52) | +31.25 points | 25 of 64 |
| 270 tokens, excluding capped runs | 66.7% | 95.8% (51, 52, 57) | +29.17 points | 16 of 64 |
| 2,238 tokens, all scored replays | 87.5% | 95.8% (1) | +8.33 points | 13 of 64 |
| 2,238 tokens, excluding capped runs | 91.7% | 95.8% (1) | +4.17 points | 1 of 64 |

At 270 tokens, ten blocks (0, 51–53, 57 and 59–63) still added value after leaving out any one position in both cohorts. At 2,238 tokens, block 1's uncapped gain came from one position and disappeared when it was left out. Activation alone reached at most 70.8% early (blocks 28 and 30) and 77.1% late (block 2) in the corrected cohort.

We used the same fitting procedure and text scores for every block. All models were fitted on the 90 development promises, and the sweep reproduced the locked text, block 2 and block 31 scores before joining replay outcomes. We picked the best blocks in this table by looking across all 64 on the same four mixed positions. Their scores are exploratory. We then froze block 51 for the fresh replay test. [All block and position scores](block-sweep.json)

## What QwenScope and the controlled choice tests showed

- On the original replay pairs at 270 tokens, text plus the QwenScope reconstructions scored 87.5% at block 51 and 83.3% at block 52, versus 56.3% for text alone and 87.5% when adding either raw block. The reconstruction errors gave no gain, and five features selected on development data explained little of the improvement. One candidate fired only on a single recurring whitespace token. [QwenScope audit](qwenscope-audit.md)
- In short scripted reasoning, raw block 51 scored the move that broke the promise higher in 15 of 16 comparisons and the QwenScope reconstruction did so in 6 of 16. The test held the ending tokens fixed and varied the ordering of the options and what the promise covered. With archived reasoning added, raw block 51's average reversed on one of the two repeated positions. [Controlled choice results](qwenscope-choice-results.md)

## Checks and limits

All 60 replays from 12 positions reached both cutoffs. Repairing the answer generation on four capped runs changed zero outcome labels. There were 17 breaches, 42 keeps and one invalid order. Seven positions supplied only keeps, one supplied only breaches, and four supplied both. The four mixed positions contributed 20 replays and 22 pairs, or 19 replays and 19 pairs excluding capped runs. Pairs reuse the same orders.

All 150 captures have three readings from 64 blocks with 5,120 coordinates per block. The 90 development promises supplied the layer selection and fitted weights. Replacing later tokens at fixed sequence length left earlier readings identical in all blocks. At zero reasoning tokens, text scores and all block outputs matched across the five replays of each position. The separate prompt-only capture matched the archived block 31 vector exactly. Reading the same prompt position inside a longer pass changed individual coordinates by up to 0.125 in that control. One development case ended before 2,238 tokens. The frozen score's SHA-256 matched the original, and a separate calculation reproduced both cohorts' rankings from the locked scores.

On the original four mixed positions, the text reader could usually anticipate the final move late in the order reasoning. Several blocks helped at the early cutoff on those positions. The fixed block 51 test on fresh positions failed its consistency check. Every replay began after the promise was sent, so these results leave the sender's intent at promise time unresolved.

Run the follow-up from the repository root with the saved private captures and reader scores.

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python analysis/exploratory/2026-11-19-within-prompt-warning/sweep_blocks.py \
  /path/to/new-block-sweep.json
```

[Predictions made before scoring](expectations.md) · [Protocol](protocol.md) · [Aggregate scores, ties and sensitivity checks](score.json)
