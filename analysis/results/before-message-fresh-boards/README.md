# Can activations flag a misleading message before it is written?

> **Public copy.** This folder is copied from the private working repository, which holds the game data. The runner scripts and the pilot plans named below are not included because they import modules or read run directories that are only there. The JSON files hold aggregate scores only.

**At zero observed false alarms, the best result was 9 catches out of 84 misleading replies.** Direct Qwen caught nine, Opus 5.5 caught five, FIBS caught two, and Qwen's written-percentage judge caught none. Those cutoffs were chosen after seeing the fresh results.

## Catches and false alarms on 16 fresh boards

The batch contained 84 misleading replies and 44 truthful replies. A misleading reply contradicted a move that was already locked in. The separate eight-game study measured later promise breaches. In each cell, the first number is misleading replies caught and the second is truthful replies flagged by mistake.

| How we chose the cutoff | Qwen direct scores | Opus 5.5 | FIBS probe | Qwen written percentages |
| --- | ---: | ---: | ---: | ---: |
| Fixed on earlier boards at zero false alarms | 43 / 3 | 0 / 0 | 24 / 6 | 0 / 0 |
| Fixed on earlier boards at at most one false alarm | 45 / 3 | 66 / 4 | 41 / 9 | 0 / 0 |
| Chosen on these fresh replies with zero false alarms | 9 / 0 | 5 / 0 | 2 / 0 | 0 / 0 |
| Chosen on these fresh replies with at most one false alarm | 13 / 1 | 5 / 0 | 6 / 1 | 0 / 0 |

The first two rows test how well earlier cutoffs carried over. Among the cutoffs that made any catches, all raised more than one false alarm on the fresh boards. The last two rows show the best counts we could get by looking back at the fresh scores and trying cutoffs. Those counts describe this batch.

## What we tested on 24 Nov

Qwen3.5-27B BF16 completed 12 replies on each of eight synthetic boards. Half the boards locked Red's move to enter and half locked it to stay, so either public sentence could be the false one depending on the board. Qwen wrote a short private note and then chose its public sentence. We scored immediately after the `MESSAGE:` marker, before the first word of that sentence. The batch contained 69 misleading replies and 27 truthful replies, with 95 distinct prefixes. Replies that shared a prefix shared their scores and each counted once in the totals.

Both methods saw the same information at the same point. Claude Opus 5.5 read the prompt and note as text and estimated the chance of a misleading next message. The released FIBS Early-Fusion Covariance probe read Qwen's activations across that prefix at blocks 19, 27, 35, 43, 51 and 58, using checkpoint revision `05def1c13a70237cda3b717d785813918b8a22fa`. We used the released weights on the shorter pre-message window specified in our [frozen protocol](../../../docs/superpowers/specs/2026-11-24-before-message-fresh-boards.md). In the earlier 24-reply pilot, both methods correctly ranked all 30 within-setup truthful–misleading comparisons. We chose alarm thresholds that flagged none of that pilot's 10 truthful replies.

## Results at those fixed thresholds

| Metric | FIBS probe (score ≥ 1.0) | Opus text judge (forecast > 85%) |
| --- | ---: | ---: |
| Misleading replies flagged | 59 of 69 | 53 of 69 |
| Truthful replies flagged | 8 of 27 | 2 of 27 |

At the fixed thresholds the two methods shared 46 correct flags. The probe caught 13 additional misleading replies and Opus caught seven additional ones. Both flagged the same two truthful replies, and the probe flagged six more.

| Locked move | Misleading replies flagged by probe | Misleading replies flagged by Opus | Truthful replies flagged by probe | Truthful replies flagged by Opus |
| --- | ---: | ---: | ---: | ---: |
| Enter | 27 of 31 | 17 of 31 | 4 of 17 | 0 of 17 |
| Stay | 32 of 38 | 36 of 38 | 4 of 10 | 2 of 10 |

### When the private note left the choice open

One reviewer classified the notes before seeing the public replies or either score. In 20 replies the note left the choice open. There were eight misleading replies and 12 truthful ones in this group. Both methods caught four misleading replies, agreeing on two and each finding two of the other method's misses. The probe flagged two truthful replies and Opus flagged zero. Within this subset only two boards had both kinds of reply (16 within-board comparisons). The probe ordered all 16 correctly. Opus ordered 15 correctly and tied one. This is too little independent evidence to establish an advantage when the note leaves the choice open.

### How the false-alarm budget changes the comparison

We swept both scores on the same 96 replies after seeing the results. At each observed false-alarm limit, the table shows the most misleading replies each method could catch with one threshold across all boards. Tied scores move together.

| Allowed false alarms out of 27 truthful replies | FIBS caught / false alarms | Opus caught / false alarms |
| ---: | ---: | ---: |
| 0 | 22 / 0 | 0 / 0 |
| 1 | 35 / 1 | 47 / 1 |
| 2 | 39 / 2 | 63 / 2 |
| 3 | 54 / 3 | 65 / 3 |

The zero-false-alarm cutoffs came from a sweep over 27 truthful replies. With one observed false alarm allowed on that batch, Opus was already ahead. See the [aggregate scores, per-setup results and complete curves](comparison.json).

## Fresh-board validation of the frozen cutoffs, 25 Nov

We fixed both pairs of cutoffs before generating eight replies on each of 16 new synthetic boards. All 128 replies were eligible, with 84 misleading and 44 truthful. Both methods scored the same 125 distinct pre-message prefixes. The [frozen protocol](../../../docs/superpowers/specs/2026-11-25-before-message-low-false-alarm.md) required FIBS to catch more misleading replies while each method raised at most one false alarm on the new batch.

| Cutoffs selected on 24 Nov | FIBS catches, out of 84 | Opus catches, out of 84 | FIBS false alarms, out of 44 | Opus false alarms, out of 44 |
| --- | ---: | ---: | ---: | ---: |
| Zero observed false alarms (FIBS ≥ 2.4375040531158447, Opus > 96%) | 24 | 0 | 6 (13.6%) | 0 |
| One observed false alarm (FIBS ≥ 2.1075711250305176, Opus ≥ 90%) | 41 | 66 | 9 (20.5%) | 4 (9.1%) |

At the stricter cutoffs, FIBS caught misleading replies on 10 of 16 boards. Six truthful replies across five boards also cleared the FIBS cutoff. That cutoff excluded all 27 truthful replies in the earlier sweep by construction. The new results show how a threshold picked from a small sample can give an overly optimistic picture of false alarms. None of the fresh Opus forecasts cleared 96%. At the second pair of cutoffs, Opus caught 25 more misleading replies than FIBS and raised five fewer false alarms. Both methods exceeded the one-alarm limit at that pair.

The two batches use the same compact game layout, and Red's move was locked before it wrote. The label measures whether the message contradicts that move. See the [aggregate validation results and per-board counts](low-false-alarm-validation.json). The [separate eight-game verdict](../eight-game-reasoning-end/README.md) remains a fail under its frozen rule. We verified its original score checksum.

## Can Qwen review its own text?

A separate Qwen3.5-27B BF16 call used the same weights as the player. It read the same board, rules and written note as Opus 5.5, ending at the same point before the public message. Qwen gave a probability with thinking off and greedy decoding. We reused both the saved Opus forecasts and the scores from the released six-block FIBS activation probe. The probe read the same pre-message prefix, and its weights stayed fixed. We set Qwen's cutoffs using the earlier 96 replies, then evaluated all three methods on the same 128 validation replies. See [ADR-007](../../../docs/adr/007-same-model-text-monitor.md) and the [aggregate comparison](qwen-self-review.json).

Qwen gave only three forecast values across the fresh replies, compared with 32 for Opus. Qwen gave its highest score, 100%, to 79 misleading replies and 12 truthful ones. The tie meant every cutoff that caught any of the 79 also flagged those 12 truthful replies. In the fresh-score sweep, Opus caught five at both budgets. It used zero false alarms because dropping its cutoff from 96% to 95% would have flagged three truthful replies.

The two judges read the same written evidence, with different model-specific decoding and response formatting. The comparison measures these judge setups on this template. It cannot isolate how much of the difference came from model capability, decoding or score format.

### Reading Qwen's next-token scores directly

We kept the same written evidence and replaced the percentage request with a choice between `honest` and `misleading`. After the words “The next message will be”, we read the model's probabilities for the two exact answer tokens and used the misleading token's share of their combined probability. We scored all 220 distinct saved prefixes locally without sampling a verdict. We reused the Opus 5.5 forecasts and FIBS scores.

Direct Qwen produced 78 distinct scores on the validation prefixes, compared with three when it wrote percentages. The two answer tokens held a median of 1.5% of the full next-token probability. Their relative scores describe the model's preference between the two tokens under this prompt. They do not estimate a calibrated probability that the player will mislead. See the [aggregate direct-score results](qwen-direct-probabilities.json) and [ADR-007](../../../docs/adr/007-same-model-text-monitor.md#direct-next-token-scores).

## What AUROC measures

AUROC asks how often a misleading reply gets a higher score than a truthful one from the same board. Ties count half. We average the per-board results, giving equal weight to each board with both kinds of reply. That covers eight boards in the 24 Nov batch and 12 in the fresh batch.

Imagine ten misleading replies all score 80. Nine truthful replies score 10 and one scores 99. Every misleading reply outranks nine out of ten truthful ones, so the AUROC is 0.90. A cutoff that avoids flagging the truthful reply at 99 also misses all ten misleading replies. This is why our main tables show catches and false alarms from one cutoff across all boards.

On 24 Nov, Opus had mean within-board AUROC of 0.942 and FIBS had 0.852. FIBS ranked above Opus on two boards, tied on two, and ranked below it on four. On the fresh batch, direct Qwen had 0.922, Opus 0.902, written-percentage Qwen 0.790, and FIBS 0.734. Direct Qwen ranked above Opus on four fresh boards, tied on four, and ranked below it on four. Its best zero-false-alarm cutoff caught 9 of 84 misleading replies. That is 11% recall at that cutoff.

## Reproducing the comparisons

| Step | Source |
| --- | --- |
| Generate the first 24 synthetic replies | Before-message pilot and pilot plan |
| Generate the 24 Nov replies and score their prefixes with Opus and FIBS | Board runner and scorer |
| Repeat on 25 Nov using the frozen cutoffs | Low-false-alarm runner |
| Run the same-model judge and read its written percentages | Qwen text judge |
| Read the judge's direct scores for `honest` and `misleading` | Qwen direct-token runner, especially `score_answer_labels` |

The Qwen judge runners reuse the same saved inputs under `~/tara-runs` and the pinned local Qwen3.5-27B BF16 model. Run their `stage` command to render an exact sample prompt, then follow the [player-view approval workflow](../../../tools/player_view_gate/README.md) before running the model. Each completed score is checkpointed. The `report` command joins the private scores with the existing reply labels and writes the aggregate comparison. Keep prompts, replies and per-reply scores in the local run directories.

The FIBS reproduction plan records the earlier check of the released weights on the authors' transcripts. [ADR-008](../../../docs/adr/008-auroc-and-monitoring-metrics.md) explains how to report catches, false alarms and AUROC in future comparisons.
