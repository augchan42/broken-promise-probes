# ADR-008: Lead with catches and false alarms in monitor evaluations

- **Status:** Proposed
- **Date:** 2026-11-25
- **Depends on:** ADR-001 on text judges, [ADR-007 on same-model review](007-same-model-text-monitor.md), and the [eight-game measurement audit](../../analysis/results/eight-game-reasoning-end/README.md#measurement-audit).

## Context

ROC came from radar signal detection. Engineers specified the observation the receiver could use and tested how well it distinguished a target already present in that observation from noise. The receiver's evidence could still be weak or ambiguous. An alarm cutoff trades off real signals caught against noise flagged by mistake. AUROC is the area under that curve across all cutoffs. It is also a ranking measure. Given a randomly selected positive and negative case, it counts how often the positive scores higher, with half credit for ties. [Peterson and Birdsall, 1953](https://www.eecs.umich.edu/techreports/systems/cspl/cspl-13.pdf) · [Hanley and McNeil, 1982](https://doi.org/10.1148/radiology.143.1.7063747).

For a monitor with a strict false-alarm limit, most of the ROC curve describes cutoffs the operator would reject. A few highly scored truthful replies can force the cutoff above many misleading ones. Prior deception-probe studies show why the truthful cases matter too. Ordinary chat and truthful replies from situations where the model had an opportunity to mislead can produce different false-alarm rates at the same cutoff. [McClish, 1989, on restricted ROC ranges](https://doi.org/10.1177/0272989X8900900307) · [Goldowsky-Dill et al., §4.1](https://arxiv.org/html/2502.03407#S4.SS1) · [Parrack et al., Appendix E](https://arxiv.org/html/2507.12691#A5).

## Decision

1. **State what the monitor predicts and when.** Record exactly what the monitor sees, where the input ends and how we assign the label. A finished X-ray gives the reader an observation of a condition that already exists. Our before-message monitor receives only the prefix and forecasts a later sampled reply. The same model with the same prefix and settings can produce different replies on different random draws. In the synthetic game we forecast a message that contradicts a locked move. In the eight-game test we forecast a later broken promise. Each label supports a claim about that outcome. Claims about intent need separate evidence.
2. **Choose the operating rule to match the task.** For an automatic alarm, specify the allowed false-alarm rate and what action the alarm triggers. For a reviewer with limited time, specify the number of cases they can inspect, then show how catches vary with capacity. Set the primary budget before evaluating the methods and explain why it is appropriate. If there is no justified budget, show the trade-off across the relevant range.
3. **Set alarm cutoffs on development cases and evaluate them on fresh cases.** Use the same evaluation replies for all methods and keep their information cutoff aligned. If the intended use applies one cutoff across games, test one cutoff across games. Include truthful replies from contexts where deception is possible. Treat a cutoff sweep on the evaluation set as exploratory. Keep tied scores together unless the test specifies an independent tie-break rule.
4. **Lead with counts and denominators.** Report misleading replies caught out of all misleading replies (recall) and truthful replies flagged out of all truthful replies (false-alarm rate). When review workload matters, show how many of the flags were correct (precision) and the total number of flags. Precision depends on how common deception is in the population, so identify the population behind the numbers. [Davis and Goadrich, 2006](https://doi.org/10.1145/1143844.1143874).
5. **Use AUROC as a secondary ranking measure.** Say which pairs are compared and how the average is weighted. An equal-board average gives every board with both outcomes the same weight. An average weighted by within-board pairs gives every eligible pair the same weight. Both describe within-board ranking. Cross-board pooling answers a separate question about the shared score scale. Report the number of boards that contribute and, when relevant, show the results by board.
6. **Show the uncertainty at the strict cutoff.** Zero observed false alarms on 44 truthful replies is a count from this batch. One false alarm among 44 already represents 2.3 percentage points. State the number of independent boards or games and account for shared boards or repeated prefixes when estimating uncertainty. A low-rate claim needs enough representative truthful cases to measure that rate.

## Examples from this project

| Comparison | Catches | False alarms | How the cutoff was chosen |
| --- | ---: | ---: | --- |
| Direct Qwen, strict sweep | 9 of 84 | 0 of 44 | Selected on these fresh scores and outcomes |
| Direct Qwen, earlier zero-alarm rule | 43 of 84 | 3 of 44 | Fixed on the earlier batch, then applied to the fresh boards |

Direct Qwen's mean within-board AUROC was 0.922 across the 12 fresh boards that contained both outcomes. Its best zero-false-alarm cutoff on that batch caught 11% of misleading replies. Both results belong in the report. For claims about how a fixed alarm performs on fresh boards, lead with the second row. [Fresh-board report](../../analysis/results/before-message-fresh-boards/README.md) · [Aggregate scores](../../analysis/results/before-message-fresh-boards/qwen-direct-probabilities.json).

The direct Qwen score comes from a separate judging call that reads the text and compares two verdict tokens. A separate baseline for this two-choice game would score the two full public replies under the original player's output distribution, using the same pre-message cutoff and sampling settings. That would test how much the released probe adds beyond the player's own output probabilities.

The eight-game experiment keeps the pass rule fixed before scoring, with its original verdict of **fail**. Its [full review-budget curve](../../analysis/results/eight-game-reasoning-end/review-budget-curve.csv) and alternative AUROC weighting give exploratory views of that result. This ADR applies to how we design and report future comparisons.
