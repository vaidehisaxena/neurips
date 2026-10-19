# Revision response

This revision addresses the AgenticLS reviews in the expanded manuscript. Page and line numbers should be regenerated after venue conversion.

| Reviewer concern | Revision made | Location |
|---|---|---|
| Prior work makes the novelty statement inaccurate | Replaced the “unknown” claim with a scoped research question and added direct comparisons with Controlled Benchmarking, ActiveFusion, and Tab-AICL. | Introduction; Related Work |
| “RDKit2D improves every setting” is too broad | Restricted the claim to all 12 model–policy macro averages and foregrounded the random-forest/P-glycoprotein decrease of 0.011. | Abstract; Results 4.1–4.2; Conclusion |
| Runtime, AUPRC, Brier, NLL, and diversity are asserted but insufficiently shown | Added a secondary-outcome figure, aggregate table, complete 24-condition appendix table, and diversity figure with intervals. | Results 4.4–4.5; Table 2; Appendix B |
| Boxplots do not show uncertainty in the mean | Replaced the central boxplot with paired mean effects and 95% bootstrap confidence intervals. Added an appendix explanation of the estimand. | Figure 2; Appendix D |
| “TabPFN is best” rests on thousandths | Reframed TabPFN and random forest as statistically tied under the best RDKit2D policy; retained the interaction result. | Abstract; Results 4.1; Discussion 5.1 |
| Conclusions repeat results | Rewrote the conclusion around the methodological implication and bounded claim. | Conclusion |
| Only one split | Explicitly distinguished acquisition-seed uncertainty from split uncertainty and added multiple splits as the first confirmation experiment. | Methods 3.5; Limitations; Appendix E |
| Missing reproducibility details | Added per-dataset N/prevalence, split sizes, initial-set generation, preprocessing fit scope, AULC equation, definition of “best,” exact model settings, and tie-breaking. | Tables 1 and 4; Methods; Reproducibility Statement |
| Validation set unused and hyperparameters fixed | Explained the fixed-configuration rationale and its potential representation-specific bias; proposed validation-only tuning as confirmation. | Methods 3.1/3.3; Discussion 5.2; Limitations |
| 0.07 lacks matching precision | Changed to 0.070 throughout. | Abstract; Results 4.1 |
| Many unadjusted contrasts | Labeled all pairwise intervals exploratory and unadjusted; removed strong interpretation of marginal contrasts. | Methods 3.5; Discussion 5.1; Limitations |
| TabPFN3 not tested | Added as an explicit limitation and planned confirmation experiment. | Limitations; Appendix E |
| Tree-baseline scope/rationale unclear | Justified the selected baselines and stated the missing model families. | Related Work; Methods 3.3; Limitations |
| Query-selection consistency lacks detail | Added a representation × learner × policy plot with bootstrap intervals in a common ECFP4 similarity space. | Figure 5; Results 4.5 |
| Copyediting and terminology | Removed duplicate abstract text; corrected grammar/typos; standardized American spelling, “entropy–diversity,” “trajectory,” and “labeled.” | Throughout |

## Items not claimed as resolved by new experiments

- No additional scaffold splits were run.
- No validation-based hyperparameter tuning was run.
- TabPFN3 and non-tree baseline families were not run.
- The revisions therefore treat these as limitations and preregistered directions, not completed evidence.

