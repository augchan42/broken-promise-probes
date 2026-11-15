# Detailed Project Plan

## A. The Project

| Field | Response |
| --- | --- |
| Project title | Does looking inside a negotiating model help predict which promises it will break? |
| Solo or group? | Solo |
| Group members (if any) | None |

**Problem**

A capable AI agent could conceal that a planned action breaks a commitment its operator relies on. If its messages and written reasoning give little warning, the operator has too little time to intervene. This is a deception and oversight risk. A monitor that reads only what the model writes can be told one thing while the model does another.

**Goal**

A measured answer to one question. Do a model's activations predict its promise breaches better than a monitor that reads its messages and reasoning? A deployer of an open-weight model could use a reliable warning to pause and check an action before it runs.

**Project plan**

1. Seven copies of Qwen3.5-27B play Warring States, a Diplomacy-style game. Reviewers label promises without seeing the orders, and the orders show which promises the player broke.
2. Compare a baseline that reads the board, messages, reasoning and a text monitor's score against the same baseline plus an activation readout. This first test is finished, and the readout did not pass.
3. Spend weeks 12 and 13 finding out why, by trying other ways of reading the same activations, then report what held up.

## B. Project Scope

**In scope**

- **Finished first test.** I fitted a linear probe on block 31 activations from four development games and scored it once on eight separate games, with 185 promises and 23 breaches. The ranking score, AUROC, rose from 0.840 to 0.864. The rule I fixed in advance required +0.050, so the probe failed. An audit showed the gain came mainly from one game. [Results and audit](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md)
- **Exploration, weeks 12 and 13.** I will try the candidates below on the saved games and activations, starting with the cheapest. I may drop, reorder or replace a candidate after Teacher feedback or further reading, and I will record each change and the reason.
  1. *A monitor that cannot see the reasoning.* Two papers report that probes detect deception that monitors reading only the outputs or actions miss. My monitor also read the reasoning, so it had more to work with. I will rescore with that access removed. [Probes and action-only monitors](https://arxiv.org/abs/2610.12445) · [Probes and output-based monitors](https://arxiv.org/abs/2509.18058) · [Sources and how far each was checked](https://github.com/augchan42/broken-promise-probes/blob/main/docs/adr/006-exploration-after-the-failed-probe.md)
  2. *A stronger probe.* My probe read one block at one token. Recent work pools scores across tokens and combines several blocks. [Multi-layer probes](https://arxiv.org/abs/2604.13386)
  3. *Sparse autoencoder features.* Qwen-Scope publishes sparse autoencoders for every block of this model. I will use them to describe what the saved activations encode, and compare a probe on those features with the probe on raw activations. Earlier comparisons favour raw activations for detection, so I expect description to be the main use. [Qwen-Scope](https://arxiv.org/abs/2605.11887) · [Probes and sparse autoencoders compared](https://arxiv.org/abs/2502.16681)
  4. *Single neurons on synthetic boards.* I have already screened individual MLP neurons on short prompts that tell the model to lie. The three shortlisted neurons had a negligible effect on the answer and did not carry over to the games. [Findings to date](https://github.com/augchan42/broken-promise-probes/blob/main/docs/feedback/2026-11-15-findings-to-date.md)
- **Rule for the exploration.** The eight games have now been scored, so every new result on them is exploratory and the report will label it that way. The verdict on the first test stays as recorded. This measures monitor quality. It is not a control evaluation.

**Out of scope**

A new pass or fail claim on the eight scored games, training my own sparse autoencoders, changing the model, and claims about agents that act for users. New self-play games happen only if a candidate needs them and the Week 12 results justify the cost.

## C. Success Criteria & Milestones

| Target date | Milestone |
| --- | --- |
| Week 12 · Sat 28 Nov EoD | Verify the records of the first test against the saved hashes and counts. Produce a first result for candidates 1 and 3. Choose which candidates to continue. |
| Week 13 · Sat 5 Dec EoD | Stop exploring. Finish the results table and charts. Revise the one-page report and draft the 10-minute talk. |
| Week 14 · Fri 11 Dec EoD | Submit the one-page PDF by Thu 10 Dec. Rehearse the talk for the Sat 12 Dec presentation. |

**Success criteria**

1. The report gives the first test's counts, both AUROC figures, the interval and the verdict against the rule fixed in advance.
2. At least two candidates have a reported result on the saved games, positive or negative, each labelled exploratory.
3. The report states which explanation for the failed test the evidence supports: the readout method, the monitor's access to the reasoning, or the labels and sample size.
4. A reader can check the first test from the scoring code, the protocol and the input hashes.

## D. Help & Open Questions

**What feedback would help most?**

1. Which candidate is most worth two weeks? My guess is that the reasoning-hidden comparison is the most informative and that single neurons are the least.
2. With 23 breaches, is the limit more likely the readout method or the labels and sample size? What result would tell them apart?
3. Is a negative first test followed by labelled exploration a sound project for the talk, or should I narrow it to one question now?

**What resources do I need?**

The first two weeks use the saved activations, the public Qwen-Scope weights and my own Mac. Compute so far is $64.02 on RunPod, all for generating the games. That is over the $50 TARA covers, and I will pay the difference. I plan no further paid compute. If a candidate needs new games, I will ask for approval before the 28 Nov checkpoint. A pointer to the best current reference on probes against text monitors would help.
