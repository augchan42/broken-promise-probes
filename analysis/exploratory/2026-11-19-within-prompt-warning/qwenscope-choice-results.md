# Testing the early score against a controlled choice

Raw block 51 scored the covered choice higher in 15 of 16 matched comparisons. Its average was positive on all four positions. The QwenScope reconstruction scored the covered choice higher in 6 of 16, with a negative average. This reverses one expectation recorded before the test. We expected neither raw block to be positive across all four positions. [Protocol and predictions](qwenscope-choice-protocol.md)

## Short scripted reasoning

Each saved board and inbox stayed fixed across eight conditions. The script gave one unit two legal moves. We reversed the list, crossed which option Qwen's written reasoning selected, and crossed which destination the written promise covered. The last eight tokens matched across all inputs. The 32 scripts used 80–87 reasoning tokens. Two positions used numbers and two used letters. The before-choice text and both block activations matched exactly between the two otherwise identical choice arms.

| Fixed score | Covered move higher when choice changed | Covered move higher when only scope changed | Positions with positive mean |
| --- | ---: | ---: | ---: |
| Text reader | 14 / 16 with one tie | 15 / 16 | 4 / 4 |
| Block 51 raw activation term | 15 / 16 | 15 / 16 | 4 / 4 |
| Block 51 QwenScope reconstruction | 6 / 16 | 8 / 16 | 2 / 4 |
| Block 51 reconstruction error | 14 / 16 | 12 / 16 | 4 / 4 |
| Block 52 raw activation term | 8 / 16 | 9 / 16 | 2 / 4 |
| Block 52 QwenScope reconstruction | 7 / 16 | 7 / 16 | 2 / 4 |

For block 51 the mean covered-choice effect was +0.0165 in the fitted predictor's units. It stayed positive for both list orders, both promise scopes and when leaving out any one position. The reconstruction contributed −0.0060 and its error contributed +0.0224 to that same effect. Block 52's average raw effect was effectively zero. The scores use the existing fixed weights. Both short combined scores were largely driven by text, so the counts above show the activation term on its own.

The strongest formatting-linked example from the earlier audit, block 51 feature 21004, was inactive at the common endpoint. The fixed five candidate features from each block contributed zero since none was active at the endpoint on these scripts. The raw block 51 contrast therefore survived this literal endpoint and option-marker control. It could be responding to the explicit relationship between the written pledge and choice. The experiment supplies the choice in the input and does not observe whether Qwen would make that choice on its own.

[Aggregate scores](qwenscope-choice-score.json)

## Repeating the test with a saved reasoning lead-in

We repeated the eight conditions on the first position of each wording style. Each condition within a position got the same prefix of real archived reasoning, ending at a sentence or paragraph boundary. This put the reading at 246 or 268 tokens, closer to the original 270. Before-choice readings again matched exactly. The text reader responded in the expected direction in seven of eight choice comparisons with one tie, and all eight comparisons that changed only the scope.

| Fixed score | Covered move higher when choice changed | Covered move higher when only scope changed | Positions with positive mean |
| --- | ---: | ---: | ---: |
| Text reader | 7 / 8 with one tie | 8 / 8 | 2 / 2 |
| Block 51 raw activation term | 6 / 8 | 6 / 8 | 1 / 2 |
| Block 51 QwenScope reconstruction | 4 / 8 | 5 / 8 | 1 / 2 |
| Block 52 raw activation term | 5 / 8 | 4 / 8 | 1 / 2 |
| Block 52 QwenScope reconstruction | 4 / 8 | 3 / 8 | 0 / 2 |

Raw block 51's two average gaps changed from +0.0199 and +0.0097 in the short test to +0.0138 and −0.0034 with the archived lead-in. This missed the follow-up prediction that both would stay positive. The reconstruction averaged negative on the first position and positive on the second. The large positive gap in the second position pulled the overall average above zero. One promise scope still had a negative average. The fixed candidate features remained inactive at the endpoint.

The raw block 51 direction can respond to the relationship between a written choice and a promise with the final token, option marker, and destination accounted for. The response weakened and reversed in one position when we restored earlier reasoning. The follow-up changes both length and context. It cannot tell which mattered. The reconstruction and its error divide the signal differently across inputs, and the earlier five features did not carry this controlled effect. The two positions are repeats of the original four, and every choice in these experiments was supplied as text.

[Aggregate scores with archived lead-in](qwenscope-choice-anchor-score.json)
