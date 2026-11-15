# Follow-ups on board prompts and neuron 8497

## What this adds to the eight-game study

The eight-game study tested whether one internal reading helped a monitor predict a broken promise. On 185 promises with 23 breaches, the average ranking score rose from 0.840 to 0.864 when each game counted equally. When each kept-versus-broken comparison within a game had equal weight, both methods scored 0.839. At the original review budget, the monitor found 15 breaches and the monitor with the internal reading found 17. The result fell short of the preset rule. [Eight-game report](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md)

The follow-ups ask what the model can read in the board prompt, whether the way we present those facts matters, and what happens when we measure or change one reading in simpler examples. The saved-game sections report aggregates. The raw prompts, replies, and game records are in private local storage.

The earlier [Luoyang ownership pilot](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/herrmann-board-pilot/README.md) and [evaluation of the published AISI probe](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/aisi-probe-zero-shot/README.md) are recorded separately.

## Reading the board in six saved positions

We picked six positions from six different games and scored one occupancy, one legal move, and one legal support question per position. The engine supplied the answers. Within each pair, Qwen received the same saved board, messages, and questions. The added summary listed who controlled each relevant territory, which army was present, and which territories were one move away.

| Question | Original prompt | Added table, first run | Same facts in sentences | Same facts in table |
| --- | ---: | ---: | ---: | ---: |
| Which army is physically there? | 5/6 | 6/6 | 6/6 | 6/6 |
| Is the move legal? | 6/6 | 6/6 | 6/6 | 6/6 |
| Is supporting the other army’s hold legal? | 4/6 | 6/6 | 5/6 | 5/6 |
| Total | 15/18 | 18/18 | 17/18 | 17/18 |

The first replay corrected one occupancy error on a controlled but empty territory and two missed legal supports. The original prompt did not explicitly list every opposing army, so the summary added facts as well as changing how they were presented. In the rerun, each territory and fact appeared in the same order in both formats. The table saved 68–119 tokens per prompt. Both formats missed the same support question in the batch and answered it correctly when that position was run one prompt at a time. The table had the same prompt tokens in the first and second runs.

The design lesson is to check what the model can actually recover from the player’s prompt before collecting games. These direct questions measure what Qwen can answer about a saved position when asked. What it understood at the time of the original negotiation remains uncertain. [Democratizing Diplomacy, Figures 2 and 8](https://arxiv.org/html/2508.07485v1) · [Prompt formatting](https://arxiv.org/abs/2310.11324) · [Table Meets LLM](https://arxiv.org/abs/2305.13062)

## Changing one reading at Mill Gate

On four synthetic prompts, we exchanged one neuron’s reading from the run with the other instruction on the same board. The edit was at the last prompt token. Both occupied and empty boards were tested in both directions. For each exchange, we edited a randomly chosen neuron in the same block by an amount that made an equally large change at the block output. The 32 conditions included 12 swaps, 12 random edits, four untouched runs, and four checks that copied back the original values.

| Block and neuron | Swaps that moved the score toward the other run’s answer | Swaps in that direction that moved the score more than the random edit did in either direction | Top answers changed |
| --- | ---: | ---: | ---: |
| 25 / 11286 | 2/4 | 1/4 | 0 |
| 38 / 8497 | 4/4 | 4/4 | 0 |
| 47 / 12215 | 2/4 | 1/4 | 0 |

For neuron 8497, the shifts ranged from 0.000029 to 0.000168 on Qwen’s raw answer score. All four checks that copied back the original values matched the untouched scores exactly. The comparison used one random neuron per block and two versions of one fictional board. [Detailed plan and per-prompt scores](../../../docs/feedback/2026-11-15-findings-to-date.md#b-project-scope)

## Reading neuron 8497 on four fresh boards

We ran 48 synthetic prompts across four boards and three shared wording patterns. For each board and wording, we crossed the fort’s occupancy with the instruction to give a correct or false answer. We read neuron 8497 at the last prompt token and scored the actual Yes or No reply. Qwen gave the factually correct answer on 13 of the 24 prompts that requested a false one.

| Predictor | Qwen replies predicted correctly |
| --- | ---: |
| Answer implied by the board and instruction | 35/48 |
| Board plus the fixed neuron rule from Mill Gate | 35/48 |
| Predictor fitted to prompt information from the other boards | 44/48 |
| Same fitted predictor with the neuron reading added | 43/48 |

For each held-out board, we fitted a small logistic regression model on the other 36 replies and predicted the 12 remaining replies. The model saw the shared wording pattern, occupancy, and requested answer type. The version with the neuron also saw its activation before the reply. Qwen’s own weights stayed fixed. The average squared error of the predicted probabilities went from 0.0843 to 0.0787 with the neuron, while the number of correct predictions fell by one. This pilot tested transfer to other boards using the same wording patterns. [Detailed plan](../../../docs/feedback/2026-11-15-findings-to-date.md#b-project-scope)

## Scout-report forecasts on saved boards

The earlier forecast checks held the game and question fixed while changing invented scout wording. These were Qwen’s stated probabilities that the other player would attempt a named move.

| Anonymous position | Direction unclear | Toward the target | Away from the target |
| --- | ---: | ---: | ---: |
| 1 | 15% | 85% | 15% |
| 2 | 15% | 85% | 10% |
| 3 | 15% | 85% | 15% |

We then crossed two pairs of saved boards with two wordings for each direction. Each pair used the same opponent, starting unit, and target. The boards in a pair differed in occupancy and other board facts.

| Pair | Target status | Original toward | Reworded toward | Original away | Reworded away |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Vacant | 85% | 85% | 15% | 15% |
| 1 | Occupied | 85% | 85% | 15% | 15% |
| 2 | Vacant | 10% | 85% | 15% | 15% |
| 2 | Occupied | 15% | 15% | 15% | 15% |

In pair 2, we clarified the scout reports by naming the player, the unit’s current location, and the target together. Across both boards and both phrasings, the forecasts were 95% toward and 10% away. The edits show sensitivity to the wording and board as supplied. The original games provide no observed outcomes under the invented reports. The numbers measure Qwen’s stated expectations.

The separate [synthetic Lake Keep pilot](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/lake-keep-behavior-pilot/README.md) changed the rule for sending a scout. Reports shifted with that rule, including in conditions where the point did not depend on the reply. The run found no observed difference attributable to the point.
