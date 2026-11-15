# Herrmann board pilot

This pilot asks whether simple readouts of a board fact from Qwen3.5-27B agree with one another on new games. It uses only the existing prompt-end capture at zero-based block 31. The four development games are for choosing the territory and fitting. The five games used in the earlier prompt-end evaluation are for scoring this new board question. Labels come from the board in the prompt.

For each territory and pair of named states, group the captured development views by game and round. Keep rounds with one view from each of the two states and consistent ownership in both views. The three labels are ownership by the first state, ownership by the second, and neither. Require each label to occur in at least two development games. Choose the territory and pair that maximize the smallest of the three round counts, breaking ties alphabetically. Apply the same view and ownership rules on the evaluation games. A territory absent from a view's parsed board has unknown ownership in that view.

Fit independent L2 logistic readouts for the three categories and the union of the first two, using training-only standardization and fixed C=1. Compare two encodings of the same three categories on the same views. The absolute encoding uses state names. The relative encoding uses mine, the other named state, and neither. Convert relative predictions back to named states using the known sender when comparing accuracy and probability scores. This restriction makes the encodings equally informative. Compare both with ownership frequencies from the development rounds. Measure how far the three independent probabilities sum from one, and how far the direct union probability is from the sum of its two parts. Read these gaps alongside accuracy and probability error, since constant probabilities can be perfectly coherent. Count paired views and distinct rounds separately. This pilot is descriptive.

Issue #30 and [Herrmann's talk](https://augchan42.github.io/hku-ai-humanities-workshop-2026/#talk/herrmann) give the motivation.

## Result on 13 Nov 2026

The development rule selected **Luoyang**, with paired views from Chu and Qin. The development set contributed 86 views of 43 rounds across four games. Chu held Luoyang in 16 rounds, Qin in 13, and neither in 14. The evaluation set contributed 132 views of 66 rounds across five games. The corresponding counts were **39, 1, and 26**.

| Readout | Ownership accuracy | Ownership probability error | Union probability error | Mean gap between the two union estimates |
| --- | ---: | ---: | ---: | ---: |
| Development frequencies | 59.1% | 0.210 | 0.243 | 0.0 percentage points |
| Named owners | 49.2% | 0.208 | 0.221 | 1.1 percentage points |
| Sender-relative | 53.0% | 0.194 | 0.221 | 1.5 percentage points |

Both readouts trailed the always-Chu accuracy baseline. The sender-relative readout had lower mean squared probability error for ownership, but there was only one Qin-owned round in the evaluation games. The evidence is too thin to prefer a vocabulary. Both readouts estimated “Chu or Qin owns Luoyang” somewhat better than the development-frequency baseline by mean squared probability error.

The union gaps were small. The constant baseline has a zero gap, so small gaps by themselves give little evidence of structure. Also, in this three-category design the direct union is the complement of “neither.” Logistic fits to complementary labels yield complementary probabilities under the same settings. This makes the two planned coherence checks redundant here. The union is invariant to switching Chu and Qin perspectives, so its direct score is shared by both encodings.

The test gives a narrow result about reading a board supplied in the prompt. A stronger follow-up would need a territory with enough changes of owner in separate evaluation games and a union whose complement contains more than one category.

Run from the repository root with the existing captures:

```sh
.venv/bin/python -m analysis.herrmann_board_pilot \
  --run-root "$HOME/tara-runs" --out /path/to/new-score.json
```

score.json records the aggregate results and input hashes.
