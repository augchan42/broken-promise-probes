# Broken promise probes

This project tests whether reading a language model's internal activations helps predict that it will break a promise it is about to make.

The model is Qwen3.5-27B. It plays Warring States, a seven-player negotiation game in the style of Diplomacy. The game is the testbed from my earlier research, described at [warringstates.day](https://warringstates.day). Players send each other messages, then submit orders. A promise is broken when the player's orders contradict what it told another player in the same round.

A deployer who had a reliable warning could pause and check a proposed action before it runs. The question is whether activations give a better warning than reading the model's text.

## Result so far

The probe did not pass its test.

A baseline that reads the messages, the board and the model's written reasoning scored a mean AUROC of 0.840 across eight games (185 promises, 23 broken). Adding a linear probe on block 31 raised that to 0.864. The gain of +0.025 was half the +0.050 that the rule, fixed before scoring, required. The 95% interval was -0.021 to +0.088.

Sweeping all 64 blocks on the same test games found no block that reached the +0.050 margin. Block 36 gave the largest gain, +0.031 ([sweep](analysis/results/eight-game-block-sweep/README.md)).

### What the follow-ups found

The follow-ups were exploratory, and none changes the original **fail** verdict. Three findings stand out.

- **A text monitor was hard to beat in every setting we tried.** In the eight games, in replays of the order call, and on synthetic boards, no activation probe beat a model reading the text by a margin that held up, whether the probe was added to the text monitor or compared with it directly.
- **Gains found by searching did not replicate.** Block 51 looked strong after a sweep over 64 blocks on four replayed positions. On fresh replays the gain came from one position and turned negative without it.
- **Ranking well is not the same as a usable alarm.** On fresh synthetic boards the best monitor ranked misleading replies above truthful ones 92% of the time on average, but a cutoff with no false alarms caught only 9 of 84. Cutoffs fixed on an earlier batch raised more false alarms on the fresh one. [ADR-008](docs/adr/008-auroc-and-monitoring-metrics.md) sets how we now report monitors: catches and false alarms first, AUROC second.

### Completed follow-ups

The first three used the same 90 development promises and 185 test promises.

- **Hide the reasoning from Claude.** Claude saw the board, legal options, inbox and sent promise, but not Qwen's private reasoning. The fitted baseline also excluded reasoning words and length. Adding the same block 31 readout changed mean per-game AUROC from **0.8535 to 0.8538**, a gain of **+0.0003** (95% whole-game bootstrap interval **-0.059 to +0.047**). It caught 17 rather than 15 breaches in 49 review slots, but Claude's estimate alone already caught 17. The within-game pair-weighted AUROC improved from 0.7893 to 0.8264. Hiding the reasoning did not reveal a convincing gain on the primary, equal-game measure.
- **Use Qwen-Scope features instead of raw activations.** Encoding the same block 31 readout with the released sparse autoencoder did not improve mean per-game AUROC. With the original reasoning-visible baseline, the score went from **0.8644 raw to 0.8594 SAE**; with the reasoning-hidden baseline, **0.8538 to 0.8310**. These are comparisons between raw and SAE-augmented predictors, not baseline-only scores. No feature meaning has yet been validated. Reconstruction was only about 5% better than predicting the development mean activation, after correcting the decoder offset, which limits interpretation.

- **Read block 31 before and after the reasoning** ([details](analysis/exploratory/2026-11-18-before-after-reasoning/README.md)). A probe on the activation alone scored **0.614** mean per-game AUROC at the end of the prompt and **0.674** at the end of the reasoning (difference +0.060, 95% interval −0.076 to +0.191). Neither scored above the range of probes fitted on shuffled labels, so this run cannot tell either from chance. It does not show that the reasoning added breach information to block 31, and it does not rule it out.
- **Re-run the same order prompt** ([details](analysis/exploratory/2026-11-18-order-resample/README.md)). 12 saved order prompts, 5 samples each, same weights and settings on different hardware (MLX). For the 6 originally broken promises, the agent broke the promise again in 17 of 30 samples, and 4 of the 6 gave both outcomes. For the 6 originally kept promises, 0 of 29 valid samples broke it.
- **Warn during the order reasoning** ([details](analysis/exploratory/2026-11-19-within-prompt-warning/README.md)). On the four re-run positions that gave both outcomes, reading more of the order reasoning helped the text monitor most: its pair ranking rose from 56.3% after 270 reasoning tokens to 87.5% after 2,238. Adding block 31 early lowered it to 33.3%. A sweep over all 64 blocks picked block 51, which scored 87.5% with the text at 270 tokens. On 32 fresh replays the fixed block 51 probe raised the score only from 40.0% to 46.7%, the gain came from one position, and the test failed its consistency rule ([fresh replay results](analysis/exploratory/2026-11-19-within-prompt-warning/block51-fresh-results.md)). In scripted choices, raw block 51 scored the move that broke the promise higher in 15 of 16 matched comparisons, but the effect weakened and reversed in one position once real reasoning was restored ([controlled choice results](analysis/exploratory/2026-11-19-within-prompt-warning/qwenscope-choice-results.md)).
- **Re-run the Claude judge** ([details](analysis/exploratory/2026-11-22-promise-hidden-judge/README.md)). The identical judge request scored 0.852 mean per-game AUROC on 12 November and 0.914 on 22 November (difference +0.061, 95% interval −0.019 to +0.139). Hiding the promise text on the same day changed the score by +0.007. The cause of the difference between dates is not known.
- **Flag a misleading message before it is written** ([details](analysis/results/before-message-fresh-boards/README.md)). A compact synthetic game locked Red's move, then let Qwen write a private note and choose a public sentence that either matched the move or contradicted it. Each monitor read the prefix up to the start of that sentence. We compared Claude Opus 5.5 reading the text, the released FIBS activation probe from FAR.AI ([paper](https://arxiv.org/abs/2610.12445v4)) on six blocks, and Qwen itself as a text judge in a separate call. On 128 replies across 16 fresh boards (84 misleading, 44 truthful), mean within-board AUROC was **0.922** for Qwen's direct next-token score, **0.902** for Opus, **0.790** for Qwen's written percentage and **0.734** for FIBS. Cutoffs fixed on the earlier 96-reply batch did not carry over. FIBS's zero-false-alarm cutoff caught 24 but flagged 6 truthful replies, and Opus's one-alarm cutoff caught 66 and flagged 4. Looking back at the fresh scores, the best cutoff with no false alarms caught 9 (direct Qwen), 5 (Opus) and 2 (FIBS). [ADR-007](docs/adr/007-same-model-text-monitor.md) adds a same-model text judge as a standard baseline.

These follow-ups are summarized here; `reproduce_headline.py` reproduces the original frozen comparison, not these additional runs. The [project plan](docs/feedback/2026-11-15-detailed-project-plan.md) and [exploration plan](docs/adr/006-exploration-after-the-failed-probe.md) predate these completed comparisons. [What we learned](docs/learnings.md) lists the mistakes and what each one taught us.

## Why this project

These are the four questions TARA asks of every final project.

### Which catastrophic risk is this about?

Losing oversight of a capable AI agent that deceives the people running it. An agent that acts for a company or a person can commit to one thing and plan another. If it also keeps that plan out of what it writes, the people responsible for it find out only after the action has run. The more that agents negotiate, trade and act without a human checking each step, the more this costs. This is the setting AI control studies: a model that may not be trustworthy, monitored by the party that runs it ([Greenblatt et al.](https://arxiv.org/abs/2312.06942)).

There is one documented case of the behaviour. In a 2026 UK AI Security Institute test, an agent that was never told to deceive used fake identities and edited its earlier activity to look harmless. That deception was aimed at third parties, not at the agent's operators, and AISI says it cannot yet say how likely such behaviour is outside testing ([incident report](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing)). The game in this project is a safe place to measure broken promises. It gives no estimate of real-world risk.

### How does the project aim to reduce it?

It tests one monitoring tool against another, on deception the model chose for itself.

- **A second monitor that fails differently.** Reading the model's written reasoning works while the model writes its plans down. Models can learn to keep intent out of their reasoning ([Baker et al.](https://arxiv.org/abs/2503.11926)). [Korbak et al.](https://arxiv.org/abs/2507.11473) call for checking reasoning monitors against methods that read the model's activations. This project is one such check.
- **A cheap first screen.** A linear probe is one dot product on activations the model has already computed. If it worked, it could run on every message and send only flagged cases to a slower monitor.
- **Who can use it.** Whoever runs the model has the activations. For an open-weight model that is the deployer. The probe does nothing for someone negotiating against a closed model they cannot inspect.

This project tests only the first link, whether the probe ranks later breaches better than the text monitor on the same cases. A deployment would also need evidence that the probe carries over to other settings, a false alarm rate that fits the reviewers' time, and a warning that arrives early enough to act on.

### What was done?

Seven copies of Qwen3.5-27B played full games against each other. The scored test used four development games and eight test games. Reviewers labelled promises without seeing the orders, and the orders showed which promises were broken. A rule fixed before scoring said how much the probe had to add. It added half of that, so it failed. The sections below give the numbers, how to read them, and three pieces you can run.

### What gap does it fill?

I found no earlier study that combines three things: promises the model makes without being told to deceive, labels that come from the model's own later actions, and probes on that model's activations. Most deception-probe results use instructed deception, where the prompt tells the model to lie. Earlier work covers the parts separately. [Duffy et al.](https://arxiv.org/abs/2508.07485) track whether Diplomacy orders honour negotiated promises. [Cheap Talk, Empty Promise](https://arxiv.org/abs/2604.04782) measures whether models keep commitments in one-shot games. Both measure behaviour and do not read activations. [Goldowsky-Dill et al.](https://proceedings.mlr.press/v267/goldowsky-dill25a.html) test probes for strategic deception, and the UK AI Security Institute released a probe of that kind for Qwen3.5-27B, and [its test on these promises](analysis/results/aisi-probe-zero-shot/README.md) was inconclusive. The [bibliography](docs/feedback/2026-11-15-presentation-bibliography.md) lists the closest work and how far each source was checked.

The result is also a caution. In this setting a monitor that reads the board, the messages and the reasoning already ranks broken promises well, and the probe added little to it.

## How to read the result

- **It measures monitor quality.** The test asks whether a second signal ranks broken promises better than the first. It is not a control evaluation. Nothing here tests a model that is trying to get past the monitor.
- **The baseline is strong.** The text monitor reads the model's written reasoning and the sent promise. The probe reads the model one token before the promise is sent. The completed reasoning-hidden comparison above found almost no equal-game AUROC gain from adding the probe, despite removing reasoning from the text baseline.
- **The label is a broken promise, which is not the same as a lie.** A promise counts as broken when later orders contradict it. The model writes its messages and its orders in separate calls, so it may have changed its plan after the promise. The data cannot separate that from deception at the time of the promise.
- **The model sometimes misread the board.** The player prompt did not list every opposing army. On six saved positions the original prompt got 15 of 18 board questions right, and adding a territory table raised that to 18 of 18. Some broken promises may be mistakes. See lesson 5 in [What we learned](docs/learnings.md).
- **The probe is a correlation.** It is a linear readout of one block at one token. It makes no claim about how the model decides to break a promise. The one causal test in this repository, swapping the values of three neurons, did not change the answer.
- **The sample is small.** There are 23 broken promises in eight games, and one game supplied most of the gain. The interval of -0.021 to +0.088 includes both no gain and a gain above the required +0.050.

## Three things you can run

Each takes under a minute on a laptop. None needs a GPU or the model.

### 1. Reproduce the headline number

```
pip install numpy
python reproduce_headline.py
```

This fits the baseline and the probe on 90 development promises, scores the 185 test promises, and prints the per-game table and the verdict. The input is `data/eight-game-score-table.npz`. It holds labels, game numbers, kernel matrices, and the block 31 activation for each promise. It holds no game text.

### 2. Read one broken promise

```
python verify_example.py
```

In round 9 of a development game, Wei told Qin it intended to take Zheng from Han. Wei then agreed a non-aggression pact with Han, and ordered an army into Zheng. The script prints the exchange and checks it against the saved messages, orders, board and token trace in `examples/wei-han/`.

`examples/wei-han/round_09/reasoning_before_promise.txt` is the reasoning the model wrote before the promise. The probe reads the model at the last token of that reasoning.

### 3. Explore neurons on a simple lying task

Open `viewer/index.html` in a browser.

The page shows three MLP neurons on short made-up prompts that tell the model to answer honestly or to lie about a small board. These neurons tracked the difference on every prompt pair. Swapping their values between the honest and lying runs did not change the answer. See lesson 7 in [What we learned](docs/learnings.md).

## What is here

- `docs/feedback/` has the project plan, the findings to date and the bibliography.
- `docs/adr/` has the decision records, including [what to explore after the probe failed](docs/adr/006-exploration-after-the-failed-probe.md), [using a same-model text judge as a baseline](docs/adr/007-same-model-text-monitor.md) and [how to report catches, false alarms and AUROC](docs/adr/008-auroc-and-monitoring-metrics.md).
- `docs/superpowers/` has the test protocols, written before each test was scored.
- `analysis/results/` has the result write-ups with aggregate numbers and figures.
- `research_notes/` has working notes on the literature. Claims marked unverified were not checked against the source.
- `analysis/` has the scoring scripts, for reading. They need the private data to run.
- `tools/player_view_gate/` has a hook for Claude Code, Codex and OpenCode. It blocks a model run until I have read what the model receives. It needs no private data. [Why I wrote it and how to install it](tools/player_view_gate/README.md).

## What is withheld

The game transcripts, the model's reasoning, the case-level labels with their text, and the full activation captures stay in private storage. The game engine is also not included. It comes from the earlier research at [warringstates.day](https://warringstates.day).

This repository publishes one development case in full and the numbers needed to reproduce the eight-game score. That is a recorded exception to the rule in the [findings to date](docs/feedback/2026-11-15-findings-to-date.md) that traces, case-level labels and activations stay private. Where a document referred to an unpublished file, the link is now plain text.

## Course context

This is my final project for [TARA](https://www.taraprogram.org/), the Technical Alignment Research Accelerator, Round 2 2026, Hong Kong cohort. The project follows TARA's participant project guide, its one-page report template, and its course weeks on linear probes, evaluations and AI control.

Those course materials belong to the TARA team and are not published here. [docs/tara-course-materials.md](docs/tara-course-materials.md) lists the ones this project draws on.

## How AI tools were used

I wrote the code, analysis and documents in this repository with AI coding assistants, Claude Code and Codex. I chose the questions, the tests and the pass rule, ran the experiments, and reviewed the results. The assistants wrote most of the code and drafted most of the text, which I edited.

The messages, reasoning and orders in `examples/` are output from Qwen3.5-27B playing the game. Nobody edited them.

The research notes under `research_notes/` came from AI-assisted literature searches. Each note marks the claims that were not checked against the source.

The TARA participant guide encourages using language models and asks that their output is edited. It sets no disclosure rule, so this section follows common practice: say which tools were used and for what.

## Licence

MIT. See `LICENSE`.
