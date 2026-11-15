# 睽 (38) pilot: forecasts after a scout report

Qwen3.5-27B raised its forecast of a specific opponent move from 15% to 85% in each of three saved game situations when a scout reported movement toward the target. A report of movement away left the forecast at 15% twice and lowered it to 10% once.

| Anonymous case | Direction unclear | Toward target | Away from target |
| --- | ---: | ---: | ---: |
| 1 | 15% | 85% | 15% |
| 2 | 15% | 85% | 10% |
| 3 | 15% | 85% | 15% |

We selected the first eligible archived diplomacy situation from each of the first three games in the split manifest. Within a game, eligibility required a legal move from an opponent unit into the sender's territory, verified against the archived move menu and ownership. We chose the first such move in sorted order. Each forecast used the same archived board, inbox and target move. The forecast task was identical across arms, and the only difference was the text of an invented scout report. The report described movement of supply wagons without disclosing orders. We used the pinned 27B BF16 model on the Mac, greedy decoding and one forecast per arm with thinking disabled. All nine replies supplied a valid probability.

The result shows that the model's stated forecast responded to this wording. The neutral forecast was already low, so the two directions had unequal room to move. The repeated values could reflect a response template, and the small sample and single report wording per arm cannot distinguish that from using the board context. The reports are counterfactual, so the original game outcomes cannot establish forecast accuracy under those reports. The pilot measured stated expectations. It did not collect activations, ask the model to submit orders, or test deceptive intent.

Runner: `python -m analysis.kui_forecast_pilot --run <private replay directory> --games <private game archive> --model <pinned checkpoint> --out <private output directory>`.

## Follow-up with matched boards and paraphrases

We ran 16 forecasts across two game pairs. Each pair used the same opponent, starting unit, and legal move into the same supply center. We selected the closest archived rounds in each game where the target was vacant on one board and occupied on the other. We used the earlier inbox and the other prompt text from the vacant-target case for both boards. Only the board section changed in a board comparison. Only the scout report changed in a wording comparison. Each report described movement toward or away from the target, using the original wording or a paraphrase. No submitted orders entered the prompts. All 16 answers were valid. The checkpoint and decoding settings matched the first pilot.

| Game pair | Target | Original toward | Paraphrase toward | Original away | Paraphrase away |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Vacant | 85% | 85% | 15% | 15% |
| 1 | Occupied | 85% | 85% | 15% | 15% |
| 2 | Vacant | 10% | 85% | 15% | 15% |
| 2 | Occupied | 15% | 15% | 15% | 15% |

The away report gave 15% in all eight conditions. In game pair 1, the report's direction changed the forecast and the board and paraphrase did not. In game pair 2, the board section affected forecasts for the toward report, and the wording mattered most on the vacant board. The paraphrase gave 85% on the vacant board and 15% on the occupied one. The original gave 10% and 15%, respectively. The boards differ in more than target occupancy, so the result supports sensitivity to the board section without identifying which fact drove it. Vacant and occupied describe the board, not known probabilities of an attempted move.

Runner: `python -m analysis.kui_forecast_followup` with the same four arguments as above and a fresh private output directory.

## Rerun with explicit references

In game pair 2, we repeated both scout phrasings on both boards. We replaced the generic references in the report with the other player's name, the unit's current location, and the target territory. The report still described supply wagons. We verified that every other part of each prompt was identical to its earlier version.

| Target | Original toward | Paraphrase toward | Original away | Paraphrase away |
| --- | ---: | ---: | ---: | ---: |
| Vacant | 95% | 95% | 10% | 10% |
| Occupied | 95% | 95% | 10% | 10% |

All eight forecasts were valid. The earlier differences between phrasings and between boards disappeared in this pair. Naming the entities together changed the way the report was written, so this rerun does not identify which reference mattered or establish that the model misidentified the unit earlier. The percentages are Qwen's estimates of whether the other player would submit the named move order. We did not measure forecast accuracy.

Reproduce with `--explicit-pair 2` and a fresh private output directory.
