# Broken promise probes

This project tests whether reading a language model's internal activations helps predict that it will break a promise it is about to make.

The model is Qwen3.5-27B. It plays Warring States, a seven-player negotiation game in the style of Diplomacy. Players send each other messages, then submit orders. A promise is broken when the player's orders contradict what it told another player in the same round.

A deployer who had a reliable warning could pause and check a proposed action before it runs. The question is whether activations give a better warning than reading the model's text.

## Result so far

The probe did not pass its test.

A baseline that reads the messages, the board and the model's written reasoning scored a mean AUROC of 0.840 across eight games (185 promises, 23 broken). Adding a linear probe on block 31 raised that to 0.864. The gain of +0.025 was half the +0.050 that the rule, fixed before scoring, required. The 95% interval was -0.021 to +0.088.

The [project plan](docs/feedback/2026-11-15-detailed-project-plan.md) says what comes next. [What we learned](docs/learnings.md) lists the mistakes and what each one taught us.

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

This is my final project for TARA, the Technical Alignment Research Accelerator, Round 2 2026, Hong Kong cohort. The project follows TARA's participant project guide, its one-page report template, and its course weeks on linear probes, evaluations and AI control.

Those course materials belong to the TARA team and are not published here. [docs/tara-course-materials.md](docs/tara-course-materials.md) lists the ones this project draws on.

## How AI tools were used

I wrote the code, analysis and documents in this repository with AI coding assistants, Claude Code and Codex. I chose the questions, the tests and the pass rule, ran the experiments, and reviewed the results. The assistants wrote most of the code and drafted most of the text, which I edited.

The messages, reasoning and orders in `examples/` are output from Qwen3.5-27B playing the game. Nobody edited them.

The research notes under `research_notes/` came from AI-assisted literature searches. Each note marks the claims that were not checked against the source.

The TARA participant guide encourages using language models and asks that their output is edited. It sets no disclosure rule, so this section follows common practice: say which tools were used and for what.

## Licence

MIT. See `LICENSE`.
