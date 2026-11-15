# What we learned

Recorded 15 Nov 2026 for the talk. Each entry says what we did, what happened, and what we would do differently. Numbers come from the result write-ups under `analysis/results/`.

## 1. Choosing the best of 192 options found block 2, and block 2 was wrong

We swept all 64 blocks at three points in the prompt and reasoning, and kept the option that scored best on the four development games. That was block 2 at the end of reasoning. It raised AUROC from 0.615 to 0.700 on the same games used to choose it.

It did not hold up. On matched positions it changed no pair ordering. On five reserved games it caught 5 of 10 breaches, the same as the baseline. On the eight-game test it lowered AUROC from 0.840 to 0.801. Block 2 is also too early in the model to plausibly hold a plan.

**Lesson.** Choosing the best of many options on 90 cases mostly selects chance. Fix the block before looking at the outcomes. We fixed block 31 for the eight-game test for this reason.

## 2. A probe can read the situation instead of the plan

Prompt-end block 54 looked strong on the development games. Its raw scores were higher later in every game. Adjusting for the round cut its ten catches to six, and once the baseline included the board and the relationship between the players it added nothing. A later check found that the block 31 breach reading carried little beyond whether the player planned an attack at all.

**Lesson.** Before crediting a probe, give the baseline everything visible: the round, the board and who is allied with whom.

## 3. The stronger the baseline, the less the probe added

The first text baseline scored 0.605 on the development games. The final baseline, with the board and a monitor that reads the reasoning, scored 0.840 on the eight games. Against that baseline block 31 added +0.025.

**Lesson.** The model writes its reasoning in plain text, and a monitor that reads it captures most of the signal. The open question is what a probe adds when the monitor cannot read the reasoning.

## 4. Broken promises are rare and hard to produce on demand

We tried to generate breaches cheaply by replaying archived positions with new incentives. In one pilot, 24 incentive branches produced no breach. In the confirmation run, 48 replays produced two. Natural full games gave 15 breaches in 90 promises, then 23 in 185.

**Lesson.** Full games were the only reliable source, and the number of breaches limits every conclusion. With 23 breaches, one game can move the average.

## 5. The model often misread the board

In one audit, 12 of 13 invalid order sets contained a support error. The player confused origin with destination, or used a territory name where a state name belonged. On six saved positions the original prompt got 15 of 18 board questions right. Adding a territory table raised that to 18 of 18.

**Lesson.** Check what the model can read from its prompt before reading intent into its actions. A broken promise can be a mistake.

## 6. A rule fixed in advance made the failure informative

The rule required a gain of +0.050 AUROC, two extra catches, and more catches than a shuffle test. Block 31 gave +0.025 and two extra catches against a shuffle threshold of three. It failed.

The audit then showed how fragile the gain was. Most of it came from one game with a single breach, where AUROC went from 0.722 to 0.944. Weighting every kept and broken pair equally, both methods scored 0.839.

**Lesson.** Without the rule, +0.025 and two extra catches would have read as a modest success.

## 7. A neuron that tracks a contrast need not cause the answer

We screened 1,114,112 MLP neurons on short prompts that told the model to lie. Three neurons shifted in the same direction on every discovery pair and on the reserved pairs. Swapping their values between the truthful and lying runs moved the answer score by about 0.0001, against baselines of 1.3 to 5.1. On game promises, neuron 8497 moved in the predicted direction in three of eight pairs. Adding it to a predictor on new boards gave 43 of 48 correct against 44 without it.

**Lesson.** A consistent reading is not a mechanism. Test the effect on the output before building on a neuron.

## 8. A published probe did not transfer

We ran the UK AI Security Institute's deception probe on our cases with no refitting. The result was inconclusive on both the development games and the reserved games.

**Lesson.** A probe trained on instructed deception does not automatically detect promises that are later broken in play.

## 9. A breach is not evidence of intent

The label records that the player's orders contradicted its promise. A blinded review of 12 cases questioned the wording or scope of the promise in four. The player may have planned the breach, read the promise differently, or changed its mind after a later message.

**Lesson.** Claims about deception need evidence about intent at the time of the promise. Our labels support claims about behaviour only.

## What we would do first next time

1. Test whether the model reads the board correctly from the player's prompt.
2. Count how many breaches natural play produces before designing the test.
3. Build the strongest text baseline first, then ask what activations add.
4. Fix the readout and the pass rule before looking at outcomes.
