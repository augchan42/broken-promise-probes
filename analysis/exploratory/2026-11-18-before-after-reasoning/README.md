# Block 31 before and after the reasoning

> **Public copy.** This folder is copied from the private working repository, which holds the game data. The script `score.py` is not included because it imports modules that are only there. `score.json` holds aggregate scores only.

Exploratory, scored once on 18 November 2026. The [protocol](protocol.md) was committed before scoring. The verdict on the first test stays **fail**.

## Question

Does the model's reasoning change its block 31 activation in a way that predicts a breach, beyond what was there before it reasoned?

## Result

A probe on the activation alone, fitted on 90 development promises and scored on 185 promises with 23 breaches from eight games.

| Readout | Mean per-game AUROC | Pair-weighted AUROC | Breaches caught in 49 slots | Shuffled-label range of mean AUROC |
| --- | ---: | ---: | ---: | --- |
| A. End of prompt, before any reasoning | 0.614 | 0.570 | 9 | 0.278 to 0.733 |
| B. End of reasoning, before the promise | 0.674 | 0.665 | 11 | 0.311 to 0.699 |
| B minus A | +0.060 | +0.095 | +2 | |

The 95% interval for B minus A, resampling whole games, is -0.076 to +0.191. B ranked better than A in five games and worse in three.

Readout B reproduced the earlier activations-alone score (0.6738, 11 catches), as the protocol required.

## Reading

Neither readout scored above the 97.5th percentile of its shuffled-label runs. This run cannot tell either probe apart from one fitted on shuffled labels. That does not show the activation holds no breach information.

B scored higher than A, but the interval includes zero and a drop. This run does not show that the reasoning added breach information to block 31, and it does not rule it out.

The shuffled-label range is wide, about 0.3 to 0.7. With 90 development promises and 23 test breaches, this design can detect only a large difference.

The protocol's third reading said that a result inside the chance range would mean the activation carries little and that the earlier gain depended on the baseline. That reading claimed too much. This run measured no baseline, and a score inside the shuffled-label range is not evidence of no signal. The protocol now carries a correction note. Its original text is unchanged.

## Limits

- 23 breaches in eight games. Four games have a single breach. In those games the AUROC moves in steps of about 0.04 to 0.09, and each counts as much as any other game in the mean.
- The shuffled-label range assumes the labels can be exchanged within a development game.
- Readout A can hold a disposition to betray as well as the situation.
- A broken promise is an outcome. The model writes its orders in a later call.
- One block and two tokens.

[Aggregate scores](score.json) · Script · [Independent review](codex-review.md)
