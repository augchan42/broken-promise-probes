# Does the Claude judge need to read the promise?

> **Public copy.** This folder is copied from the private working repository, which holds the game data. The script `promise_hidden.py` and the `2026-11-15` comparison folder are not included because they depend on modules and files that are only there. The score files hold counts and AUROC values only.

Exploratory, run 22 November 2026 on the eight scored games. The verdict on the first test stays **fail**.

`protocol.md` was written before any promise-hidden answer was scored. Its last section records a control that was added after the first score. The protocol and script were written in private storage and were not committed before the run. They are committed here unchanged, as run.

## Why

In the first test the Claude judge read the promise the player sent. The board and text classifier did not. The judge alone scored 0.852 and the classifier 0.692. This run asks how much of that lead comes from reading the promise.

## What was done

- **Promise hidden.** The original judge request with the `<agent_message>` block deleted and one sentence reworded to say that a commitment is sent and not shown. Same 185 promises, same model (`claude-opus-5-5`), same system prompt and call settings. One answer per promise.
- **Promise visible, rerun (post hoc control).** The original request, unchanged, asked again on the same day. Added after the promise-hidden score came out higher than the original, to separate the effect of hiding the promise from a difference between runs.
- **Original.** The saved answers of 12 November that the first test used. Read, not rerun.

Both new runs finished with no failed or missing case. Every saved answer records `claude-opus-5-5` as the model requested and the model reported. The Claude Code CLI was version 2.1.330. The 12 November answers did not record a CLI version.

## Result

| Judge run | Mean per-game AUROC | Pair-weighted AUROC | Breaches found in 49 slots (of 23) |
| --- | --- | --- | --- |
| Promise visible, 12 Nov (first test) | 0.852 | 0.813 | 15.69 |
| Promise visible, 22 Nov rerun | 0.914 | 0.919 | 20.40 |
| Promise hidden, 22 Nov | 0.921 | 0.911 | 20.00 |

For comparison, from saved results with no refitting: the board and text classifier scored 0.692 and found 12. With word features of the sent message and the recipient added (run 15–16 November, `../2026-11-15/reasoning-hidden/score.json`, `local_text_board_with_reasoning`) it scored 0.704 and found 12.

| Comparison | Mean AUROC change | 95% whole-game bootstrap | Games up / down | Correlation of the 185 probabilities |
| --- | --- | --- | --- | --- |
| Hidden minus visible, both 22 Nov | +0.007 | −0.043 to +0.061 | 3 / 5 | 0.93 |
| Visible 22 Nov minus visible 12 Nov | +0.061 | −0.019 to +0.139 | 5 / 3 | 0.79 |

Per game:

| Game | Promises | Breaches | AUROC 12 Nov | AUROC 22 Nov visible | AUROC 22 Nov hidden | Found 12 Nov | Found 22 Nov visible | Found 22 Nov hidden |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 19 | 1 | 0.833 | 0.778 | 0.889 | 1.00 | 1.00 | 1.00 |
| 2 | 22 | 1 | 1.000 | 0.929 | 0.881 | 1.00 | 1.00 | 1.00 |
| 3 | 33 | 5 | 0.739 | 0.879 | 0.821 | 2.40 | 3.40 | 3.00 |
| 4 | 25 | 5 | 0.735 | 0.950 | 0.935 | 3.00 | 5.00 | 5.00 |
| 5 | 28 | 3 | 0.820 | 0.967 | 0.960 | 2.00 | 3.00 | 3.00 |
| 6 | 22 | 6 | 0.917 | 0.938 | 0.969 | 4.29 | 5.00 | 5.00 |
| 7 | 24 | 1 | 0.957 | 0.870 | 1.000 | 1.00 | 1.00 | 1.00 |
| 8 | 12 | 1 | 0.818 | 1.000 | 0.909 | 1.00 | 1.00 | 1.00 |

## What it shows

- **Reading the promise made little difference to the judge.** On the same day, hiding the promise changed the score by +0.007, and the interval spans zero. With neither reading the promise, the judge scored 0.921 against the classifier's 0.692. With both reading it, 0.914 against 0.704.
- **The identical request gave different answers ten days apart.** The 22 November rerun scored 0.061 higher than the 12 November answers. The interval over eight games includes zero. The probabilities agree less across the two dates with the same request (0.79) than across the two requests on the same date (0.93).
- **The cause of the difference between dates is not known.** Each run is one sample per promise. It could be sampling variation, a change in the served model, or a change in the CLI. This run cannot separate them. Tracked in issue #64.

## Limits

- The eight games have been inspected many times. Nothing here is a confirmation.
- The rerun with the promise visible was designed after seeing the first result.
- One sample per promise in every run. There is no estimate of same-day variation for a fixed request.
- The promise-hidden judge is still told who the recipient is. The classifier was never told. This run removes the message text only.
- The promise-hidden request has one reworded sentence, so it differs from the original by more than the deleted block.
- The first test's primary baseline and its probe comparison used the 12 November judge answers. They have not been rescored with the 22 November answers.

## Files

- `protocol.md`: the protocol, with the post hoc amendment.
- `promise_hidden.py`: the script, as run. It imports `rescore.py` from `../2026-11-15/reasoning-hidden/` for the checked cohort loader and the judge loop.
- `score.json`: promise hidden against the 12 November answers.
- `score-with-control.json`: all three runs and the two comparisons.

## What is not here

The 370 judge checkpoints and the two run logs stay in private storage under `~/tara-runs/promise-hidden-2026-11-22/`. The checkpoints hold a prompt hash, the model and a probability, and no game text.

## Running it again

Work in the private copy so that checkpoints do not land in the repository. From the repository root:

```
d=~/tara-runs/promise-hidden-2026-11-22
PYTHONPATH=.:analysis/exploratory/2026-11-15/reasoning-hidden .venv/bin/python $d/promise_hidden.py judge
PYTHONPATH=.:analysis/exploratory/2026-11-15/reasoning-hidden .venv/bin/python $d/promise_hidden.py rejudge
```

`score` and `rescore` write `score.json` and `score-with-control.json` once and refuse to overwrite them.
