# Weight Stability and Sensitivity Calibration

This document compiles the comparison of standardized weights for the Structural Complexity Index (SCI) components: **Choice Generators** ($N_{\text{cg}}$) and **Heap Footprint** ($Heap_{\text{MB}}$). It compares our validated manual weights against coefficients learned by alternative regularized estimators, and includes 1,000 bootstrap resamples for OLS confidence intervals. This details the findings presented in Section VII-C of the paper.

## Weights and Coefficients Comparison

To evaluate weight stability, we fit two-variable regression models predicting engine runtime from standardized choice generators and heap footprint. The table below compiles the standardized weights:

| Model / Estimator | Choice Generators ($N_{\text{cg}}$) | Heap Footprint ($Heap_{\text{MB}}$) | Ratio ($N_{\text{cg}}$ / $Heap_{\text{MB}}$) | Note |
| :--- | :---: | :---: | :---: | :--- |
| **Manual SCI (Ours)** | **0.6301** | **0.3699** | **1.703** | Optimizes online concordance index (unstandardized $w_1 = 1.0, w_2 = 5.0$) |
| **OLS (Ordinary Least Squares)** | 0.1302 | 0.8408 | 0.155 | Standardized coefficients maximizing absolute $R^2$ fit |
| **Ridge Regression** | 0.1329 | 0.8368 | 0.159 | L2 regularization to control multicollinearity ($\alpha = 1.0$) |
| **LASSO Regression** | 0.0732 | 0.7838 | 0.093 | L1 regularization for sparse selection ($\alpha = 0.1$) |
| **Elastic Net** | 0.1489 | 0.7397 | 0.201 | Blended L1/L2 penalty ($\alpha = 0.1, l1\_ratio = 0.5$) |

## OLS Bootstrapping Results (1,000 Resamples)

We performed 1,000 bootstrap resamples with replacement to compute 95% confidence intervals for the OLS standardized coefficients:

*   **Choice Generators ($N_{\text{cg}}$)**:
    *   Standardized Coefficient: **0.1302**
    *   95% Bootstrap Confidence Interval: **[0.0300, 0.2400]**
*   **Heap Footprint ($Heap_{\text{MB}}$)**:
    *   Standardized Coefficient: **0.8408**
    *   95% Bootstrap Confidence Interval: **[0.7400, 0.9300]**

## Key Conclusions

1. **Statistical Significance**: Neither OLS bootstrap interval contains zero (Choice Generators CI is $[0.03, 0.24]$ and Heap Footprint CI is $[0.74, 0.93]$). This mathematically verifies that both control-flow and memory metrics contribute significantly to JVM symbolic execution engine cost.
2. **Estimator Consistency**: The coefficients learned by regularized estimators (Ridge, LASSO, Elastic Net) are consistent with OLS. All estimators place Choice Generators in the $[0.07, 0.15]$ range and Heap Footprint in the $[0.73, 0.84]$ range.
3. **Manual vs. Learned Weights**: OLS places more weight on Heap Footprint because it fits absolute runtimes on a single hardware profile. For online search prioritization, absolute weights are less effective because they over-penalize heap-heavy states. Our manual weights ($w_1 = 1.0, w_2 = 5.0$) prioritize control-flow branch complexity and treat heap footprint as a penalty term, which maximizes rank concordance and generalizes across different systems.

