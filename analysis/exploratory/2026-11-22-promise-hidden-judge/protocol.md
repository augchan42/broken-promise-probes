# Eight-game promise-hidden judge comparison

Written 22 November 2026, before any promise-hidden judge call was scored. Exploratory. The eight evaluation games have been inspected many times. The frozen verdict stays **fail**.

## Question

The Claude judge read the promise the player sent, and was told who received it. The board and text classifier saw neither. How much of the judge's lead over the classifier (0.852 against 0.692 mean per-game AUROC) remains when the judge does not read the promise?

## Design

- Same 185 evaluation commitments, outcomes, judge model (`claude-opus-5-5`), system prompt and call settings as the frozen eight-game score. Inputs are loaded and checksum-verified by `cohort()` from `analysis/exploratory/2026-11-15/reasoning-hidden/rescore.py`.
- One change to the judge prompt. Delete the `<agent_message>` block. Replace the sentence "In this message the agent, {sender}, makes a commitment to {recipient}." with "After this reasoning the agent, {sender}, sends {recipient} a message that makes a commitment. You are not shown the message." Everything else is unchanged, including the private reasoning and the question.
- The judge is still told the recipient, because the question is about the recipient's territory. The classifier was never told the recipient. This comparison removes the message text only. It does not remove the recipient.
- Judge alone needs no fitting, so only the 185 evaluation cases are judged. No development cases are judged.
- Each answer is saved as it arrives, keyed by the SHA-256 of its prompt. Finished cases are skipped on restart. Temporary errors are retried four times. No case is replaced because of its answer.

## Report

Mean per-game AUROC, pair-weighted AUROC, and broken promises caught in the original 49 review slots with fractional credit for ties, for the promise-hidden judge alone. Report beside it, from saved results and with no refitting:

- the original judge alone (0.852, 15.69 catches),
- the board and text classifier (0.692, 12 catches),
- the board and text classifier with word features of the sent message and the recipient added (`local_text_board_with_reasoning`, run 15–16 November: 0.704, 12 catches).

Also report the per-game AUROC difference between the original and promise-hidden judge, with a whole-game bootstrap interval (seed 20261112). No pass or fail threshold. Outputs contain aggregates only. Judge checkpoints hold no game text and no free-text answers.

## Amendment after the first score (22 November, post hoc)

The promise-hidden judge scored higher than the original (0.921 against 0.852 mean per-game AUROC, 20 against 15.69 catches). The original judge answers date from 11–13 November and each is one sample. The difference could come from hiding the promise, from sampling variation between runs, or from a change in the served model. To separate these, rerun the original prompt unchanged (promise visible) on the same 185 cases today, into `judge-with-promise-rerun/`, and report it beside the other two. This control was added after seeing the first result.
