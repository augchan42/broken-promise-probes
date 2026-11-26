# Block 51 did not show a consistent gain on fresh replays

At 270 reasoning tokens, adding the fixed block 51 probe raised the average ranking score from **40.0% to 46.7%**. It helped on one position, hurt on another and left three scores equal. Removing the one position where it helped changed the average gain from **+6.7 to −16.7 percentage points**. The result missed the consistency rule set before the run. [Protocol](block51-fresh-protocol.md)

Qwen generated 32 fresh answers across eight positions. All reached the cutoff and produced valid orders. Qwen broke the promise 17 times and kept it 15 times. Five positions produced both outcomes, yielding 15 pairs. Each pair compares one breach with one keep on the same position. A correct ordering receives one point and a tie receives half a point. Each position counts equally in the average.

| Replays included | Mixed positions | Pairs | Text alone | Text + block 51 | Gain | Gain after removing one position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 5 | 15 | 40.0% | 46.7% | +6.7 pp | −16.7 to +25.0 pp |
| Excluding five forced closures | 3 | 9 | 33.3% | 44.4% | +11.1 pp | −33.3 to +50.0 pp |

The five position-level changes were 0, −66.7, 0, 0 and +100 percentage points. In the position that drove the gain, text ranked zero of three pairs correctly and text plus block 51 ranked all three correctly. In the position where the probe hurt, the count fell from two of three to zero. Excluding forced closures left those same two positions plus one with equal scores. Both methods scored below the 50% chance benchmark in both comparisons.

The rule required at least four mixed positions in the primary cohort, a positive mean gain after omitting each mixed position in turn, and a positive mean gain without forced closures. The run met the first and third conditions. It failed the second because omitting the one improved position gave a loss. The earlier sweep's 31.25-point gain did not replicate at a similar size or across positions.

The scoring check reproduced the aggregate result and independently recalculated each rank score. It also verified the locked coefficients, the original score checksum, all 32 order labels and the token sequences used for the readouts. The 32 replays came from eight prompts absent from the development, earlier replay and scripted-choice inputs. [Aggregate scores](block51-fresh-score.json)
