# Presentation bibliography

## Why monitor a model’s internal activity?

- **Sharkey et al. (2025).** Use §3.2.1a to frame early warning as an open problem and §2.2.2 to explain why the outcome we can label, a broken promise, differs from the intent we would like to detect. [Open Problems in Mechanistic Interpretability](https://arxiv.org/abs/2501.16496v1)
- **Goldowsky-Dill et al. (ICML 2025).** Earlier work tested whether probes trained on simple examples can detect deception in more complex scenarios. Cite this as prior work on transfer, alongside our comparison on negotiations from separate games. [Detecting Strategic Deception with Linear Probes](https://proceedings.mlr.press/v267/goldowsky-dill25a.html)
- **Cooney, Africa, and Irving (June 2026).** Activation and token-probability detectors performed worse on models trained to misreport what they believed than on prompts that asked models to lie. Give the caveat that their method for checking beliefs partly favored cases where written reasoning revealed them. [Did You Lie?](https://arxiv.org/abs/2606.12618v2)
- **von Klinski et al. (September 2026).** Stress tests found that some lie detectors tracked instruction following or answer likelihood. Use this when explaining why predicting an instructed answer and detecting a concealed plan need separate evidence. [Stress-Testing LLM Lie Detectors](https://arxiv.org/abs/2609.39807)
- **Hollinsworth et al. (October 2026, v4).** A probe combining many layers and tokens slightly outperformed text monitors that saw actions alone on two agent benchmarks. Specify what those monitors saw. Our main comparison gave the monitor access to written reasoning. [Telling FIBS](https://arxiv.org/abs/2610.12445v4)

## What the model could see on the board

- **Duffy et al. (AAAI 2026, preprint 2025).** Figure 2 shows control and unit presence separately. Figure 8 compares prompt variants on replays of a game phase. A short list that repeated possible moves improved order success in their test. The paper also tracks negotiated promises and game orders. [Democratizing Diplomacy, full paper](https://arxiv.org/html/2508.07485v1)
- **Sclar et al. (ICLR 2024).** Changes to prompt formatting can affect accuracy while preserving meaning. Cite this for comparing different layouts with the same facts. [Quantifying Language Models’ Sensitivity to Spurious Features in Prompt Design](https://arxiv.org/abs/2310.11324)
- **Sui et al. (WSDM 2024).** Table format and ordering affected how models answered questions about table content. Cite this as evidence that layout can matter in general. Our six-position comparison found the same accuracy for sentences and the table. [Table Meets LLM](https://arxiv.org/abs/2305.13062)

## Related evidence and project results

- **Cheap Talk, Empty Promise (April 2026).** Measures whether models follow through on public commitments in one-shot games. Cite when explaining earlier work on observed breaches. [Cheap Talk, Empty Promise](https://arxiv.org/abs/2604.04782)
- **Warring States results.** Cite our report for the eight-game comparison and measurement audit. Cite the plan for the six-position prompt replay and the viewer experiments. [Eight-game report](https://github.com/augchan42/broken-promise-probes/blob/main/analysis/results/eight-game-reasoning-end/README.md) · [Detailed project plan](2026-11-15-findings-to-date.md) · [Follow-up results](../../analysis/results/board-prompt-and-neuron-followups/README.md)
