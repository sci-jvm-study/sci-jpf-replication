# Standardized OLS Regression Coefficients

This document provides the full standardized OLS regression coefficients and their relative explanatory contributions to JPF interpreter engine runtime ($T_{\text{engine}}$) across the 420 completed, non-timeout campaign runs. This details the findings presented in Section VII of the paper.

## Regression Model Specification

The regression model is fit on standardized variables (zero mean, unit variance) to evaluate the relative effect size of each dynamic JVM metrics:

$$\text{Engine Latency } (T_{\text{engine}}) \sim N_{\text{cg}} + N_{\text{gc}} + N_{\text{states}} + Heap_{\text{MB}} + QueueSize$$

## Standardized Effect Sizes

The table below summarizes the standardized coefficients, their sign (direction of effect), and their relative contribution (percentage of the absolute sum of coefficients):

| JVM Metric / Feature | Symbol | Standardized Coefficient ($\beta$) | Direction | Relative Effect Size (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Heap Footprint (MB)** | $Heap_{\text{MB}}$ | 0.6400 | Positive (+) | 36.37% |
| **Choice Generators** | $N_{\text{cg}}$ | 0.5943 | Positive (+) | 33.77% |
| **Garbage Collection (GC) Cycles** | $N_{\text{gc}}$ | 0.4021 | Positive (+) | 22.85% |
| **Priority Queue Size** | $QueueSize$ | 0.1100 | Positive (+) | 6.25% |
| **Explored State Count** | $N_{\text{states}}$ | 0.0133 | Positive (+) | 0.76% |
| **Total** | | **1.7598** | | **100.00%** |

## Key Insights

1. **Dominance of Structural Metrics**: Choice Generators ($N_{\text{cg}}$) and GC Cycles ($N_{\text{gc}}$) account for **56.62%** of the total standardized effect size (with Heap Footprint adding another **36.37%** to reach **92.99%**). This confirms that virtual machine interpreter overhead (dynamic type resolution and memory-management sweeps) is the primary driver of performance, rather than path exploration topology alone.
2. **State Count Limitations**: Traditional state count contributes only **0.76%** of the standardized effect size when JVM-level memory and control-flow variables are present. This explains the physical cause of the **State-Count Complexity Gap** described in Section IV-C of the paper.
