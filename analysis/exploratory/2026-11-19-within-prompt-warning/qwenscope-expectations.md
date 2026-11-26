# What could explain the block 51 and 52 scores?

Written 20 November 2026 before examining the sparse features. The four mixed replay positions already selected blocks 51 and 52 in the all-block sweep. Use them to generate explanations for a new test.

At 270 order-reasoning tokens, project the two QwenScope reconstructions onto the existing combined breach predictor. Keep the fitted text and activation weights fixed. Check how much of the within-position difference comes from named sparse features and how much remains in the reconstruction error. Also score text with either component by itself, with the same weights. Keep the corrected and uncapped cohorts available.

I expect some of the early gain to survive reconstruction, but I expect the reconstruction error or many small feature contributions to matter. I also expect the strongest individual features to track wording, names, or the structure of reasoning more consistently than an explicit choice to enter covered territory. If a few features carry the gain, recur across positions and track an endorsed covered move across wording while staying quiet on considered and rejected moves, I would revise that expectation. This evidence would concern the order call.

Select five features per block on the development games by mean absolute variation in their signed contribution within a game. Examine these on the replays and compare with five descriptive candidates ranked by contribution differences on the replay pairs. Treat patterns from the latter as hypotheses. Check whether the same final token, token type, and a recent mention of a covered territory account for apparent recurrence. Use only the 270 visible tokens for these checks. The saved blinded text reader's stance labels provide a separate but imperfect reading. Lack of matched cases leaves a confound unresolved.

The readout decomposition changes the inputs to a fitted predictor. The underlying Qwen decisions and original score are frozen. The report will use anonymous aggregate counts and no excerpts.

[Research process and recording expectations](https://www.lesswrong.com/posts/Ldrss6o3tiKT6NdMm/my-research-process-understanding-and-cultivating-research) · [Existing replay result](README.md)
