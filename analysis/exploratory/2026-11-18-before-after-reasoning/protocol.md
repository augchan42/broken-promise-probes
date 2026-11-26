# Protocol: block 31 before and after the reasoning

Written on 18 November 2026, before scoring. Exploratory. The eight games were scored on 12 November and have been inspected since. The verdict on the first test stays **fail**.

## Question

Does the model's reasoning change its block 31 activation in a way that predicts a breach, beyond what was there before it reasoned?

## Design

One thing varies: the token where the activation is read.

| Readout | Token | What the model has processed |
| --- | --- | --- |
| A | Last token of the prompt, before the model writes anything | Board, inbox and instructions |
| B | Last token of the reasoning, before the promise | The same, plus its own reasoning |

Everything else is fixed:

- The same 90 development promises from four games for fitting, and the same 185 promises with 23 breaches from eight games for scoring.
- The same labels as the first test.
- Block 31, zero-based, after the transformer block, from the saved captures. No new model runs.
- One probe per readout on the activation alone: each coordinate centred and scaled on the development promises, then logistic regression with the regularisation of the first test (C=1). This is the first test's fitting code with no other inputs.
- No board features, no text features, no Claude estimate, no combined model.

## Checks before reading the result

- The saved inputs match the hashes recorded by the first test.
- Readout B reproduces the "activations alone" score from the Qwen-Scope comparison: mean per-game AUROC 0.6738 and 11 catches in 49 slots. If it does not, stop and report the mismatch.

## What is reported

- For A and for B: mean per-game AUROC, AUROC weighted by within-game kept-broken pairs, and breaches caught in the 49 review slots.
- B minus A in mean per-game AUROC, by game, with a 95% interval from resampling whole games 10,000 times.
- A chance line for each readout: shuffle the development labels within each development game 1,000 times, refit, and report the mean and the 2.5% to 97.5% range of mean per-game AUROC.

There is no pass or fail rule.

## How to read it

- B about equal to A: the predictive signal is present before the model reasons. It reflects the situation, not a plan formed during the reasoning.
- B above A: the reasoning added something predictive. That is a candidate for a plan. It is not proof of one.
- Both inside the chance range: the activation alone carries little here, and the earlier gain depended on the baseline it was added to.

## Limits

- With 23 breaches the interval will be wide. A difference can be missed.
- Readout A can hold a disposition to betray as well as the situation. A is an upper bound on what the situation explains.
- Readout B can encode the situation more readably than A without any plan. A gain is not proof of intent.
- A broken promise is an outcome. The model writes its orders in a later call.
- One block and two tokens. Other blocks and tokens are not tested here.

## Output

`score.json` with aggregate numbers only. No case IDs, text, case-level scores or activations.

## Correction after scoring (18 November 2026)

The text above is as committed before scoring. An independent review after scoring found that the third reading under "How to read it" claims too much. A score inside the shuffled-label range means the probe cannot be told apart from one fitted on shuffled labels. It does not show that the activation carries little, and this run measures no baseline, so it says nothing about what the earlier gain depended on. The result note uses the corrected reading.
