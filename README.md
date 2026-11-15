# Broken promise probes

This project tests whether reading a language model's internal activations helps predict that it will break a promise it is about to make.

The model is Qwen3.5-27B. It plays Warring States, a seven-player negotiation game in the style of Diplomacy. Players send each other messages, then submit orders. A promise is broken when the player's orders contradict what it told another player in the same round.

A deployer who had a reliable warning could pause and check a proposed action before it runs. The question is whether activations give a better warning than reading the model's text.

## Result so far

The probe did not pass its test.

A baseline that reads the messages, the board and the model's written reasoning scored a mean AUROC of 0.840 across eight games (185 promises, 23 broken). Adding a linear probe on block 31 raised that to 0.864. The gain of +0.025 was half the +0.050 that the rule, fixed before scoring, required. The 95% interval was -0.021 to +0.088.

The [project plan](docs/feedback/2026-11-15-detailed-project-plan.md) says what comes next. [What we learned](docs/learnings.md) lists the mistakes and what each one taught us.

## Why this project

These are the four questions TARA asks of every final project.

### Which catastrophic risk is this about?

Losing oversight of a capable AI agent that deceives the people running it. An agent that acts for a company or a person can commit to one thing and plan another. If it also keeps that plan out of what it writes, the people responsible for it find out only after the action has run. The more that agents negotiate, trade and act without a human checking each step, the more this costs. This is the setting AI control studies: a model that may not be trustworthy, monitored by the party that runs it ([Greenblatt et al.](https://arxiv.org/abs/2312.06942)).

### How does the project aim to reduce it?

It tests one monitoring tool against another, on deception the model chose for itself.

- **A second monitor that fails differently.** Reading the model's written reasoning works while the model writes its plans down. Models can learn to keep intent out of their reasoning ([Baker et al.](https://arxiv.org/abs/2503.11926)). [Korbak et al.](https://arxiv.org/abs/2507.11473) call for checking reasoning monitors against methods that read the model's activations. This project is one such check.
- **A cheap first screen.** A linear probe is one dot product on activations the model has already computed. If it worked, it could run on every message and send only flagged cases to a slower monitor.
- **Who can use it.** Whoever runs the model has the activations. For an open-weight model that is the deployer. The probe does nothing for someone negotiating against a closed model they cannot inspect.

### What was done?

Seven copies of Qwen3.5-27B played full games against each other. The scored test used four development games and eight test games. Reviewers labelled promises without seeing the orders, and the orders showed which promises were broken. A rule fixed before scoring said how much the probe had to add. It added half of that, so it failed. The sections below give the numbers, how to read them, and three pieces you can run.

### What gap does it fill?

I found no earlier study that combines three things: promises the model makes without being told to deceive, labels that come from the model's own later actions, and probes on that model's activations. Most deception-probe results use instructed deception, where the prompt tells the model to lie. Earlier work on broken promises in games measured behaviour and did not read activations. The [bibliography](docs/feedback/2026-11-15-presentation-bibliography.md) lists the closest work and how far each source was checked.

The result is also a caution. In this setting a monitor that reads the board, the messages and the reasoning already ranks broken promises well, and the probe added little to it.

## How to read the result

- **It measures monitor quality.** The test asks whether a second signal ranks broken promises better than the first. It is not a control evaluation. Nothing here tests a model that is trying to get past the monitor.
- **The baseline is strong.** The text monitor reads the model's written reasoning and the sent promise. The probe reads the model one token before the promise is sent. A monitor that could not see the reasoning would be easier to beat. That comparison is the first item in the [exploration plan](docs/adr/006-exploration-after-the-failed-probe.md).
- **The label is a broken promise, which is not the same as a lie.** A promise counts as broken when later orders contradict it. The model writes its messages and its orders in separate calls, so it may have changed its plan after the promise. The data cannot separate that from deception at the time of the promise.
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
- `docs/adr/` has the decision records, including [what to explore after the probe failed](docs/adr/006-exploration-after-the-failed-probe.md).
- `docs/superpowers/` has the test protocols, written before each test was scored.
- `analysis/results/` has the result write-ups with aggregate numbers and figures.
- `research_notes/` has working notes on the literature. Claims marked unverified were not checked against the source.
- `analysis/` has the scoring scripts, for reading. They need the private data to run.

## What is withheld

The game transcripts, the model's reasoning, the case-level labels with their text, and the full activation captures stay in private storage. The game engine is also not included.

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
