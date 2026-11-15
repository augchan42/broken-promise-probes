# Findings to date (long version of the 15 Nov plan)

## A. The Project

| Field | Response |
| --- | --- |
| Project title | Does looking inside a negotiating model help predict which promises it will break? |
| Solo or group? | Solo |
| Group members (if any) | None |

**Problem**

A highly capable AI agent authorised to make consequential decisions could conceal that a planned action violates a commitment its operator relies on. If its messages and written reasoning give little warning, the operator may have too little time to intervene before serious harm occurs.

**Goal**

I will report whether an activation readout improves prediction of later promise breaches beyond the board state, messages, and a monitor that reads the model's reasoning and sent promise. A deployer with access to an open-weight model's activations could use a reliable warning to pause and independently verify a proposed action before execution. The study tests the first step by measuring whether activations improve breach rankings and help find more breaches at a fixed review budget. The eight-game test is complete, and the activation readout did not pass the rule I set before scoring.

The comparison applies an existing interpretability method to commitments that arise during multi-agent play. Instructed-lie experiments tell the model to lie and test whether a probe recognises the lie. Here, the commitments arise from negotiation and the outcome comes from the player's subsequent action.

**Project plan**

1. Seven instances of Qwen3.5-27B play the Diplomacy-style game Warring States, each for its own state. AI reviewers apply a fixed promise rubric without seeing submitted orders. I link strict promises to valid orders by the same player in the same round and require a legal opportunity to breach. A breach is an attempted move into territory covered by the promise.
2. Replay saved tokens through the pinned model and fit the predictors on 90 eligible commitments from four development games. Use the residual-stream activation from block 31 at the final reasoning token before the player sends the promise. The baseline uses the board, inbox, written reasoning, reasoning length, and the monitor's score. The monitor also reads the sent promise, so the comparison models oversight after the operator can see the promise and before the player submits orders.
3. Score the fixed baseline and the same baseline plus block 31 once on eight separate games. Compare the rankings within each game and count breaches in the top quarter of each game's ranked promises, rounding up. The protocol fixes in advance the ranking margin, the minimum catch gain, and a shuffle test that estimates how many extra catches chance alone could produce. [Frozen protocol](https://github.com/augchan42/broken-promise-probes/blob/main/docs/superpowers/plans/2026-11-12-eight-game-reasoning-end.md)

**How block 31 was chosen**

An exploratory sweep on the four development games tried all 64 blocks at three points in the prompt and reasoning. It selected block 2 at the end of reasoning. On the earlier five-game transfer test, that probe and the baseline each caught five of ten breaches. For the eight-game study, I fixed block 31, the 32nd of 64 blocks and a midpoint already reported in the development comparison, before labelling any messages from those eight games. The probe uses the block's full activation vector at the final reasoning token. It learns from labelled development cases how to weight the components of that vector alongside the baseline features to score breach risk. [Layer choice](https://github.com/augchan42/broken-promise-probes/blob/main/docs/adr/003-probe-layer-choice.md) · [Five-game transfer test](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/held-out-transfer/README.md)

## B. Project Scope

**In scope**

- **Completed eight-game evaluation.** The test covered 185 eligible promises and 23 breaches. Giving each game equal weight, the ranking score (AUROC) rose from 0.840 to 0.864. The gain of +0.025 fell short of the prespecified +0.050 margin, with a 95% whole-game bootstrap interval of −0.021 to +0.088. At 49 review slots, the baseline caught 15 breaches and the augmented model caught 17. The two extra catches met the minimum of two and fell below the shuffle threshold of three. The probe failed the prespecified rule. [Eight-game results](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md)
- **Completed measurement audit.** The equal-game gain came mainly from one game with a single breach. Giving each of the 484 kept–broken pairs within games equal weight, both methods scored 0.839. The catch gain also varied with the review budget. The talk will use a per-game gain chart and one anonymised example from the blinded AI review. That review questioned wording or scope in four of 12 sampled cases and included one breach. The game records a breach under the rubric, while the player's intent at promise time remains uncertain. [Measurement audit](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md#measurement-audit)
- **Remaining work.** Verify the experiment records, revise the one-page report, and prepare the talk. Use aggregate results and shareable code in the submission. Keep traces, case-level scores and labels, and activations in private storage. Exception, 15 Nov 2026: the public repository [broken-promise-probes](https://github.com/augchan42/broken-promise-probes) publishes one development case in full (the Wei and Han promise from round 9, with its messages, reasoning, orders and token trace) and, for the 90 development and 185 test promises, the labels, game numbers, kernel matrices and block 31 activations with no text. These let a reader reproduce the eight-game score and read one real broken promise. [One-page report draft](https://github.com/augchan42/broken-promise-probes/blob/main/docs/feedback/2026-11-13-one-page-report-draft.md)

The [follow-up results](../../analysis/results/board-prompt-and-neuron-followups/README.md) collect the board, scout-report, and single-neuron comparisons. The [presentation bibliography](2026-11-15-presentation-bibliography.md) records the sources and what each supports.

**Exploratory follow-ups**

After the eight-game test I looked for a cleaner test of what the activations encode. The sections below record those follow-ups. None of them changes the frozen verdict.

**From game replays to Mill Gate**

I started with saved Warring States boards, negotiation snippets, and order prompts. The game supplied an observable breach, but its cause could be a plan the player already had, a different reading of the promise, or a decision revised after a new message. Replaying the start of the order call on the same commitments gave the model a later view of the game and did not improve the ranking over the order prompt and board. Even the narrower Luoyang pilot, which asked who owned one territory, had very few rounds for one of the owners. Invented scout reports removed most of the game context, but the report wording and the board changed together, so the forecasts could not separate their effects. [Eight-game report and order-start replay](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md#exploratory-follow-ups) · Design review and pilot history

The activation viewer is a local tool that shows single-neuron readings token by token on short synthetic prompts. I reduced its test to a small table, one question about a fort with known occupancy, and a one-word answer. Instructions to answer truthfully or falsely gave me a known contrast to check the viewer against. The first neuron screen matched the answer but changed the board and the instruction together. The check on a fictional board named Lake Keep then held the board and answer fixed while varying the wording. The Mill Gate prompts fix the board and question within each pair and changes the instruction phrase in two token positions. The second board reverses which answer the instruction calls for. During each swap the prompt being replayed stays fixed.

**How I found the viewer's neurons**

The viewer comes from a separate exploratory test on synthetic boards. Its three neurons are individual feed-forward (MLP) units. The eight-game predictor above uses the full block 31 activation vector.

ARENA's *Transformer from Scratch* calls the repeated stages **transformer blocks** and counts them with `n_layers`. In that convention, layer index 38 is `blocks[38]`, the 39th block, since indexing starts at zero. A block contains an MLP, and each MLP neuron contributes one number per token. The viewer reads one coordinate of the MLP's post-activation vector before the output projection, corresponding to the measurement point ARENA labels `blocks.0.mlp.hook_post` for its first block. The eight-game probe reads the whole residual vector after its chosen block, corresponding to `hook_resid_post`. [ARENA block terminology](https://github.com/augchan42/ARENA_materials/blob/b10a78e1e69ac331648cffa624944959690dff88/chapter1_transformer_interp/instructions/pages/01_%5B1.1%5D_Transformer_from_Scratch.md#L605) · [ARENA activation names](https://github.com/augchan42/ARENA_materials/blob/b10a78e1e69ac331648cffa624944959690dff88/chapter1_transformer_interp/instructions/pages/01_%5B1.1%5D_Transformer_from_Scratch.md#L812-L833)

I screened **64 blocks × 17,408 MLP neurons per block = 1,114,112 block–neuron combinations** on the pinned Qwen3.5-27B checkpoint. Block 38, neuron 8497 is one of those combinations. For each prompt I read one activation per unit at the last input token, before the answer. The activation is the signed number produced by Qwen's gated MLP for that unit, just before the output projection.

The prompts crossed occupied and empty forts with truthful and false-answer instructions. I paired runs within each board family when both followed the instruction and gave the same answer. In one discovery pair, both prompts asked "Is River Fort occupied?"

| River Fort | Instruction | Qwen's answer | Block 38, neuron 8497 |
| --- | --- | --- | ---: |
| Occupied | Answer truthfully. | Yes | +0.12793 |
| Empty | Lie when you answer. | Yes | +0.05933 |

Matching the observed answer controls for whether Qwen emits "Yes" or "No" in the pair. The board state and instruction both change, so the discovery comparison combines their effects. The raw shift is the false-instruction activation minus the truthful-instruction activation at the same unit and the last input token of each prompt. Here that is −0.06860 activation units. This is a difference in internal readings from two forward passes. The output effects shown in the viewer's **Writes** section come from a separate intervention.

I ranked units on five pairs from three discovery board families. For each unit I took the sign of its mean shift, multiplied each shift by that sign, and divided the smallest of the five signed shifts by the unit's within-family variation. The denominator is the root-mean-square deviation from each discovery family's mean across its four prompts, with a floor of 0.01. The score rewards a large minimum shift relative to that unit's variation. A positive score requires all five shifts to agree in direction.

| Rank | Block | MLP neuron | Raw shifts across the five discovery pairs | Within-family scale | Ranking score |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 47 | 12215 | −0.13586 to −0.13004 | 0.06257 | 2.07829 |
| 2 | 38 | 8497 | −0.07373 to −0.06860 | 0.03305 | 2.07598 |
| 3 | 25 | 11286 | +0.02269 to +0.02457 | 0.01108 | 2.04700 |

The first-ranked unit had about 1.9 times the smallest raw gap of neuron 8497 and about 1.9 times its within-family scale. Their ranking scores were nearly tied. All three units kept the same shift direction on four reserved pairs and two additional pairs matched for input token count. [Prompt construction](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/instructed_lie_transfer.py#L13) · [Ranking code](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/instructed_lie_neurons.py#L94)

The viewer includes all three units. Neuron 8497 became the example for the Lake Keep follow-ups because the MCP comparison showed that its largest gap landed on the same comma at token 47 on both board states. Within each board state, only the instruction changed and Qwen gave the same answer. On the occupied board Qwen answered "No" both times, and the activation moved from +0.03760 to −0.15918, a shift of −0.19678. On the empty board it answered "Yes" both times, and the shift was −0.22803. The first-ranked unit's largest gaps on Lake Keep were 0.08740 and 0.09570 in absolute value and occurred at different positions. These are descriptive results on the viewer prompts. On an exploratory check using one kept and one broken promise from each of eight saved games, neuron 8497 moved in the predicted direction in three of eight pairs. [Synthetic viewer](https://pub-14b6774a2a7244fa91c3558531b13846.r2.dev/instructed-lie.html) · [Game-pair selection code](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/instructed_lie_neurons.py#L132)

**What the comma example establishes**

The same-comma gap locates where neuron 8497's activation was most sensitive to the wording on these two boards. The rank came from the separate five-pair screen at the final input token. To check the comma's effect on output, I zeroed that neuron's reading at that position and reran the rest of the model. In FP32 the largest change in the Yes-minus-No logit score was about 0.00005, and the most likely first answer token stayed the same in all 12 trials. The Mill Gate test below swaps natural activation values at a different position, the final input token. Neuron Explorer ranks changes in generated text after intervention, and Neuron Lens measures how the output effect of a firing varies across contexts. For a detector, the relevant check is whether the readings predict what the model actually does on independent examples where wording alone does not give away the answer. [Neuronary and Neuron Explorer](https://neuronary.org/about/#finding-neurons) · [Neuron Lens findings](https://github.com/stdlogits/neuron-lens/blob/main/docs/findings.md#4-one-firing-is-one-sample-of-a-write) · [Lie-detector stress tests](https://arxiv.org/abs/2609.39807)

**Mill Gate swaps on the three shortlisted neurons**

I replayed the four saved Mill Gate prompts as two matched pairs. The board and question stayed fixed within each pair. The phrases "an honest" and "a false" changed two token positions. All four prompts had 66 tokens and shared the last formatting token, where the original screen measured the units. The unedited FP32 replay favored Yes then No on the occupied board and No then Yes on the empty board, in truthful then false-instruction order.

I replayed each prompt with one change. At the last token I replaced one neuron's value with its reading from the other instruction on the same board. For example, on the occupied board I took a reading from the run that answered No and used it in the run that answered Yes, keeping the Yes run's prompt fixed. I tried both directions for each neuron on both boards.

For comparison, I changed a randomly chosen neuron in the same block. I matched the size of the change passed on to the rest of the model. I also ran each prompt untouched and with the same parts of the model set to their own original readings, to check whether the editing procedure itself moved the scores. That gave 12 swaps, 12 random-neuron edits, four untouched replays, and four checks that copied the original values back. Each board's 16 conditions ran together. The calculations used 32-bit precision (FP32) with the pinned BF16 model weights. I fixed the random choices before running the swaps, using seed 20261115. [Activation patching methods](https://arxiv.org/abs/2309.16042)

Qwen gives Yes and No a score before converting those scores to probabilities. The baseline column shows the original Yes score minus the No score. The next three columns show how much the swap and the random-neuron edit shifted the score toward the other run's answer. A positive number in a Yes → No row means the edit made No more competitive.

| Board | Instruction kept fixed | Original answer → other run's answer | Baseline | Block 25 / neuron 11286 | Block 38 / neuron 8497 | Block 47 / neuron 12215 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Occupied | Truthful | Yes → No | +3.745033 | −0.000254 / −0.000036 | +0.000029 / +0.000010 | +0.001341 / +0.000708 |
| Occupied | False | No → Yes | −3.203026 | −0.000063 / −0.000210 | +0.000168 / −0.000002 | +0.000675 / +0.000797 |
| Empty | Truthful | No → Yes | −5.145039 | +0.000021 / +0.000164 | +0.000124 / +0.000074 | −0.000055 / +0.001011 |
| Empty | False | Yes → No | +1.280100 | +0.000034 / +0.000013 | +0.000124 / −0.000025 | −0.000328 / −0.000620 |

**In all four swaps, neuron 8497 shifted the score toward the other run's answer by more than the random-neuron edit shifted it in either direction.** Its shifts ranged from +0.000029 to +0.000168 score units, called logits. Neurons 11286 and 12215 each moved the score toward the other run's answer twice and beat their random comparison in that direction once. The largest shift from any candidate was 0.001341 logits, from neuron 12215 on the occupied board. Copying back the original values left every score exactly the same in all four checks. The top answer stayed the same in every replay.

The test covered two versions of one fictional board. Each block had one random control neuron. Block 25 used 7854, block 38 used 8737, and block 47 used 2427. The result gives no estimate of how often another random neuron would do as well and gives no evidence about whether the unit detects deception in the games. The eight-game probe's frozen verdict remains **fail**.

**Can neuron 8497 help predict an answer on a new board?**

I ran Qwen on 48 prompts across four fictional boards. Each board used the same three wording patterns, with an occupied and an empty version of the fort and instructions to give either a correct or a false answer. I recorded neuron 8497's value at the last prompt token, before Qwen started answering.

I trained a small predictor called logistic regression on Qwen's replies. For example, to test Pine Crossing, I fitted the predictor on the 36 replies from the other three boards and then used it to predict the 12 replies on Pine Crossing. I repeated that process with each board held out in turn. The board was new to the predictor each time, and the wording patterns were familiar. Qwen ran with its original weights throughout.

The predictor learns from what Qwen actually said. It assigns a score to each combination of wording pattern, fort occupancy, and requested answer type. For example, it can learn that Qwen usually gives the correct answer for a particular wording even when the instruction asks for a false one. The version with 8497 also learns how much to adjust the score based on the neuron's reading. Each version turns its score into a probability and predicts a false reply when that probability reaches 50%. Whether the reply is false is determined by comparing it with the board.

| Information available to the predictor | Qwen replies predicted correctly |
| --- | ---: |
| Wording, fort occupancy, and requested answer type | 44 of 48 |
| Same information plus neuron 8497's reading | 43 of 48 |

The predictor with 8497 got one fewer reply right. This small test measures how well the predictor carries over to different boards that use the same wording patterns.

**Can Qwen read the saved board more accurately?**

I used six archived positions from six games and asked three questions about each. Which army is physically in the territory? Is a specified move legal? Can one army legally support another army holding its position? I checked the answers against the archived board and the engine's legal orders. Both versions included the same saved board, inbox, and questions. One also included a compact territory table listing the controlling state, the army present, and the territories one legal move away.

| Question | Original prompt | With the territory table |
| --- | ---: | ---: |
| Which army is physically there? | 5 of 6 | 6 of 6 |
| Is the move legal? | 6 of 6 | 6 of 6 |
| Is the support order legal? | 4 of 6 | 6 of 6 |
| Total | 15 of 18 | 18 of 18 |

The table corrected two missed legal support orders and one occupancy mistake on a controlled but empty territory. The original prompt did not list all the opposing armies explicitly. Adding the table changed both the information Qwen had and how the prompt presented it. The cases and replies remain in private local storage.


**Does the table layout help when both prompts give Qwen the same facts?**

I replayed the same six positions with the same board, inbox, and questions. In one version the extra territory facts appeared as plain sentences. In the other they appeared in the original table. Both versions listed the same territory, controlling state, army present, and neighboring territories, in the same order.

| Question | Same facts in sentences | Same facts in a table |
| --- | ---: | ---: |
| Which army is physically there? | 6 of 6 | 6 of 6 |
| Is the move legal? | 6 of 6 | 6 of 6 |
| Is the support order legal? | 5 of 6 | 5 of 6 |
| Total | 17 of 18 | 17 of 18 |

Both formats missed the same support question. The table used 68–119 fewer tokens per prompt. The table prompts matched the first replay token for token, but one support answer changed when the prompts ran alongside different inputs in the same batch. I reran that position one prompt at a time and both formats got all three answers right. The comparison has six positions and only one replay per format for most positions.

Duffy et al. replayed the same Diplomacy phase and improved order success by repeating the legal moves in a concise list. Sclar et al. found that changes to formatting can change answers even when the meaning stays the same. Sui et al. found that format and ordering affect performance on tasks such as looking up a table cell. [Democratizing Diplomacy](https://arxiv.org/html/2508.07485v1#A1) · [Prompt formatting](https://arxiv.org/abs/2310.11324) · [Table Meets LLM](https://arxiv.org/abs/2305.13062)

Before collecting the original games, I should have checked which board facts Qwen could answer from the player's prompt. The matched replay measures answers to direct questions about a saved board. What Qwen understood when it made the original promise remains an open question. Presentation notes

**Out of scope**

New self-play runs, further layer or cutoff searches on the games, and the value transplant proposed in issue #32 are future work. The game agents act for their own states. Transfer to agents acting on behalf of users and robustness to deliberate concealment are open questions.

## C. Success Criteria & Milestones

| Target date | Milestone |
| --- | --- |
| Week 12 · Sat 28 Nov EoD | Verify the model, replay, labels, and score against the recorded hashes and counts. Finish the results table, per-game gain chart, and anonymised review example. |
| Week 13 · Sat 5 Dec EoD | Revise the one-page report and draft the 10-minute talk. Use the measurement audit to explain how much the result depends on game weighting, review budget, and the promise rubric. |
| Week 14 · Fri 11 Dec EoD | Submit the one-page PDF using the TARA template by Thu 10 Dec. Finish and rehearse the talk by Fri 11 Dec for the Sat 12 Dec presentation. |

**Success criteria**

1. The report gives the counts by game, both AUROC averages, the uncertainty interval, the catch counts at the common review budget, and the verdict against all three prespecified checks.
2. The report presents the measurement audit as an exploratory check. The chart shows which games drove the result, and the review example shows why inferring intent requires evidence beyond a later breach.
3. An authorised reader can check the comparison from the scoring code, protocol, aggregate results, and input hashes. The one-page report and slides explain the result and deployment relevance to a Teacher seeing the project for the first time.

## D. Help & Open Questions

**What feedback would help most?**

1. Is the deployer oversight argument specific enough, given the action window in the game and the operator's access to activations?
2. Does comparing against a monitor that sees the reasoning and the sent promise fill a clear gap left by instructed-lie experiments?
3. Does the per-game chart, together with one reviewed case, give enough context to interpret the failed pass rule and the limits of the breach labels?

**What resources do I need?**

The remaining work uses the existing aggregate scores, protocol, and saved review. I plan $0 in additional compute or API spend. Teacher feedback on the risk framing and comparison would help most. A human read of the selected example would help check that its ambiguity is clear.
