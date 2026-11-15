# 睽 (38) board forecast experiment

**Question.** Does Qwen revise its forecast of a specific move when a scout provides new information, and does that revision hold across clear descriptions of the same observation? The earlier pilot exposed a wording problem. It did not establish forecast accuracy or what the model represented internally. [Pilot results](../../../analysis/results/kui-forecast-pilot/README.md)

**Starting point.** Qwen is a neutral observer. It sees the current public board, the rules needed to read it, and the move it is being asked to forecast. The question is “What is the chance that Blue submits a move order this round for its army at East Camp to enter River Fort?” Score the order submission. A move that bounces still counts as an attempt. The forecasts are numbers Qwen gives us.

## Inputs and comparisons

Render each board from one verified archived pre-order state. Include the current units, ownership, supply centers, and legal moves for the players. Take unit positions and move menus from the archived observations and verify them against the pinned game rules. Strip diplomatic messages, role instructions, saved reasoning, submitted orders, and resolution. Ask the same question in every condition for a given board. Use one common observer instruction across all boards.

| Condition | What Qwen sees | What it tells us |
| --- | --- | --- |
| Board only | Board and forecast question | What Qwen expects from the public position alone |
| Direction unknown, two phrasings | Same board plus a scout who saw the wagons and could not determine their direction | Whether adding a report without direction changes the forecast |
| Toward the target, two phrasings | Same board plus the scout observing the wagons heading toward the target | Whether evidence in favor of the move raises the forecast |
| Away from the target, two phrasings | Same board plus the scout observing the wagons heading away from the target | Whether evidence against the move lowers the forecast |

Use a record with fields for the scout, player, army location, destination, observed object, and direction. Generate both phrasings from that record. For example, using invented names:

> The scout saw the supply wagons of Blue’s army at East Camp heading toward River Fort.
>
> The supply wagons of Blue’s army at East Camp were seen by the scout heading toward River Fort.

Both must name the player, army location, and destination inside the report. Both refer to the wagons, carry the same level of certainty, and make the same claim about direction. The scout reports an observation made before the forecast and has no access to orders. A reviewer who has not seen the forecasts reads each sentence independently and records the fields. Use a pair only if both readings match the intended record. Keep the same names, evidence source, task wording, and placement of the report across conditions. Omit the report line for the board-only control. Verify from the rendered prompts that every within-board comparison differs only in that line. Start each condition in a fresh context.

For a separate board check, use a small set of **matched pairs** with the same player, army location, and target move. Compare the board-only forecasts first, then compare forecasts under an identical scout sentence. Prefer verified pairs where one board feature changes, such as whether a defending unit occupies the destination. When using archived snapshots that differ in several ways, call the result board sensitivity and report those differences. Occupancy changes the obstacles to a move and does not establish how likely the player is to attempt it. Include a simple board-reading check that asks which player has a unit at a named location, scored directly against the board.

## Cases, scoring, and stopping

1. **Select before reading outcomes.** Use four pilot boards from two games and eight confirmation boards from at least four other games. Exclude every board used in the earlier wording experiments from confirmation. Use one legal target per board and choose targets from the pre-order state by a fixed rule. Include a mix of contested and vacant destinations where the archive supports it. Freeze the rule and the split by game. If the archive cannot fill those cells, report the shortfall before running confirmation.
2. **Pilot only to check the instrument.** Use the four boards to verify that a neutral spectator gets a valid numeric answer, that the board is intelligible, and that the report pairs pass the independent reading check. Allow one prompt revision and repeat all seven conditions on one pilot board if needed. Then freeze the prompts, checkpoint, decoding settings, parser, and scoring rules before running the confirmation boards once. Start with the pinned Qwen3.5-27B BF16 checkpoint, thinking disabled, and greedy decoding, as in the pilot. The call budget is 28 pilot forecasts, 56 confirmation forecasts, up to seven pilot repeats, and up to nine calls for board checks. Reserve four of those nine for direct questions about the positions. The full follow-up stops at 100 model calls or two local GPU hours, whichever comes first. A run stopped before completing confirmation is incomplete.
3. **Report the paired differences in percentage points.** For each board and evidence direction, take the absolute gap between the two phrasings. For each phrasing, report the change from unknown direction to toward and from unknown direction to away. Also report the unknown-direction report minus board only. This shows whether mentioning a scout changes the forecast by itself. Show all board-level differences and counts of invalid answers. Report how much room the starting forecast leaves to move in each direction so a floor or ceiling cannot be mistaken for lack of updating.
4. **Use an explicit confirmation gate.** Require at least seven of eight boards to have valid answers in all conditions and no wording gap over 10 points in any of the three report conditions. Require toward to exceed away under both phrasings on at least six of eight boards across at least three games, with a median gap of at least 20 points for each phrasing. Compute each median on the same set of boards with all seven answers valid, and also report the gaps by game. Count boards with missing answers as failures for the two counts. These proposed thresholds make an operational distinction between a tolerable wording shift and a useful evidence shift. They are not statistical significance thresholds. Report the full differences regardless of the gate, and stop after one confirmation run.
5. **Check accuracy on real inputs.** After recording the board-only forecasts, join them to the archived legal order submissions. Report how often the target order occurred and the mean squared difference between forecast probability and outcome, also called the Brier score. Compare with the constant event rate estimated on the pilot boards and report the denominator. Eight forecasts provide a descriptive check. Accuracy under an invented scout report has no matching archived outcome. [Brier’s probability score](https://journals.ametsoc.org/view/journals/mwre/78/1/1520-0493_1950_078_0001_vofeit_2_0_co_2.xml)

## What this would change for the deception study

Passing the forecast check would establish that this setup can separate sensitivity to evidence from sensitivity to wording for a simpler task. It would justify using the same controls in a future behavior study. The existing feasibility gate for concealed intent is separate. A deception label still requires affirmative evidence of a conflicting plan at the time the promise was made, with comparable open attacks and genuine peace cases in independent games. Keep the previous 23-breach screen and its stop decision as reported. [Concealed-intent stop rule](2026-11-13-neuron-search-stop-rule.md)

## Execution and review

- [ ] Stage a private board manifest and validate the renderer against the archived move menus. Check that no prompt contains the original inbox, actual order, or later resolution. Check that a bounced move would be counted as an attempt and an invalid order would be excluded from accuracy scoring.
- [ ] Review the report pairs and run the pilot. Freeze the manifest and rendered-prompt hashes, including the fixed board-only control.
- [ ] Run confirmation locally using the existing forecast runner and strict probability parser. Checkpoint each board. Report anonymous case results, excluded cases and reasons, actual outcomes available for the board-only score, and the stopping decision. Keep game text, board identifiers, and raw model outputs in private storage.
