# Predicting the Direction of Five Year Bank Tier 2 Bond Yields

**ECO6109 Group Project Proposal — working draft**

**Members and student IDs:** [to be completed]

**Submission deadline:** 20 November 2026, 23:59

**Research question.** Can information available after the daily close improve forecasts of the next observed change in five year Chinese bank Tier 2 bond yields, relative to majority-class and direction-persistence benchmarks? We will examine whether a parsimonious logistic model and an AutoGluon benchmark provide a stable improvement, rather than selecting a model solely because it has a high F1 score.

**Data.** We will use a fixed income dataset retained from a group member's internship, with a primary sample from January 2019 to August 2025. The main workbook contains 153 candidate fields covering government and policy bank yields, money market rates, capital instrument spreads, derivatives, and other market indicators. A separate Tier 2 AutoGluon dataset and prior research notebooks will provide supporting material. The target is a yield time series, not a panel of individual bonds. We will verify the curve definition, units, date coverage, and data usage conditions before submission.

**Method.** We define the positive class as a decline or no change in the next observed yield. We will begin with majority-class and persistence benchmarks, then compare logistic regression and AutoGluon on the same observations and features. The primary test window starts on 14 May 2024; a preceding chronological validation window will be used for model selection. Preprocessing will be fitted using training data only, and observations whose labels cross partition boundaries will be removed. We will audit calendars, missing values, duplicate features, and publication timing before expanding the feature set. Historical notebooks have already inspected this period, so we will disclose this limitation and use rolling evaluation where feasible.

**Evaluation and work plan.** We will report sample sizes, class proportions, accuracy, precision, recall, F1 and, for probabilistic forecasts, AUC. Results will be compared across subperiods and economically interpretable feature groups. The group will independently recount at least one key numerical result from exported predictions. Data verification and baseline work will be completed first, followed by model comparison, interpretation, and preparation of the 15 minute presentation and final report. Existing internship scores will be treated as historical evidence requiring verification, not as new findings. The report will discuss information timing, model selection bias, limited sample size, and the difference between yield-direction forecasts and executable bond returns.

*Before submission: fill in names and IDs, confirm data scope, and format this draft as a single page. No new model outperformance is claimed at the proposal stage.*
