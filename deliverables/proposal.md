# Forecasting Five Year Bank Tier 2 Bond Yield Directions

ECO6109 Group Project Proposal | 20 November 2026

## Research Question

Can market information improve forecasts of the next change in five-year Chinese bank Tier 2 bond yields beyond simple benchmarks? We will examine whether logistic regression and tree models implemented through AutoGluon deliver consistent improvements over majority-class and direction-persistence forecasts. This question connects financial market prediction with the practical challenge of identifying bond price direction, since falling yields generally correspond to rising bond prices.

## Data

We will use a fixed income dataset retained from a group member's research internship. The primary workbook covers January 2019 to August 2025 and contains 153 candidate fields, including the target yield, government and policy bank yields, money market rates, capital instrument spreads, derivatives and other market indicators. The target is a yield time series rather than a panel of individual bonds. WindPy extraction scripts and a separate Tier 2 AutoGluon dataset provide supporting material. We will verify the curve definition, units, calendar and missing observations before estimation.

## Methodology

We define the positive class as a decline or no change in the next valid yield observation. Predictors will be restricted to information available at the forecast time. Training will use data before January 2024, followed by validation through 13 May 2024 and evaluation from 14 May 2024 to 27 August 2025. Preprocessing and feature selection will use training data only; model settings will be selected on validation data, and labels crossing partition boundaries will be excluded. Models will be compared using the same dates, features and label definition. Because earlier internship experiments examined this evaluation period, we will disclose its retrospective nature and add rolling evaluation to assess stability. Predictive gains will be interpreted separately from executable investment returns.

## Evaluation and Work Plan

We will report class proportions, accuracy, precision, recall, F1 and AUC for probabilistic forecasts, with comparisons across subperiods and feature groups. Data checks and benchmark verification will be completed by 27 November, followed by model comparison and interpretation by 2 December. We will then prepare the 15-minute presentation for the assigned class date and the final report due on 19 December. A group member will independently recompute a key numerical result from exported predictions. The report will document tools and code sources and discuss information timing, class imbalance and model selection bias.
