# Replication Package & Artifacts

This directory contains the replication package, raw datasets, and analytical guides for the paper "The State-Count Complexity Gap in JVM Symbolic Execution". It provides all the necessary scripts, configuration files, and pre-computed raw execution logs to verify our empirical findings, regenerate the figures, and re-run the symbolic execution campaigns using our Structural Complexity Index (SCI) search strategy (SCISearch).

---

## Directory Structure

* **`code/`**: Contains execution, orchestration, and statistical analysis scripts:
  * **`custom jpf listener/`**: Source files for JPF listeners:
    * `SCISearch.java`: The custom search heuristic prioritizing execution states with lower Structural Complexity Index (SCI).
    * `ResearchDataListener.java`: Listener for collecting solver execution times, path metrics, and branch coverage.
  * **`evaluated benchmarks/`**: Source code of evaluated programs and their `.jpf` configurations:
    * Configuration files: `.jpf` files representing different workloads, scaling depths, and search budgets.
    * Java files: Target benchmark programs executed under Java PathFinder (JPF).
  * `run_sci_robust_campaign.ps1`: PowerShell script orchestrating the JPF robust campaign sweeps across search budgets.
  * `run_sci_evaluation.py`: Runs the comparative search heuristic campaigns (BFS, DFS, vs. SCI-guided) and outputs the online scheduling table (**Table V**).
  * `generate_icse_figures.py`: Generates Figure 1 to Figure 5 in vector SVG formats using the robust campaign datasets.
  * `calculate_correlations.py`: Computes the Pearson and Spearman rank correlation matrix (**Table IV**).
  * `check_sci_weight_sensitivity.py`: Validates weight calibrations and prints concordance indices for the constant-state groups (**Table VI**).
  * `calculate_ols_coefficients.py`: Fits the 5-variable OLS regression, explains sign flipping due to multicollinearity, and outputs absolute standardized effect sizes.
  * `run-oop-study.ps1` & `analyze-oop-study.py`: Runs the dynamic dispatch and exceptions overhead campaigns for **Table I** and **Table II**.
  * `harvest_causal_evidence.ps1`: Runs JPF on the polymorphic dispatch and branch-control configurations to collect direct VM-level causal profiling metrics (**Table II**).
  * `compute_lofo.py`: Executes the Leave-One-Family-Out cross-workload validation and outputs the Spearman correlation and $R^2$ table (**Table VII**).
  * `aggregate_budget_campaign.py`: Aggregates raw budget campaign CSV logs from `results-sci-budget/` into per-strategy summary statistics.
  * `setup_svcomp_benchmarks.py` & `scan_java_feature_candidates.py`: Configures and analyzes JVM SV-COMP benchmarks.
* **`figures/`**: Contains finalized, title-free SVG vector plots included in the paper:
  * `fig1_state_count_failure.svg`: Explored states vs. engine runtime scatter plot.
  * `fig2_constant_state_variance.svg`: Latency variance under constant state counts ($N = 502$).
  * `fig3_residual_recovery.svg`: Residual regression of state baseline model vs. SCI.
  * `fig4_ranking_accuracy.svg`: Pairwise Concordance Index comparison across groups.
  * `fig5_synthetic_to_real_failure.svg`: Synthetic-to-real actual vs. predicted latency transfer failure.
* **`results/`**: Pre-computed raw CSV logs from our campaigns:
  * `results-robust-campaign/`: Data points used for OLS regression, sensitivity sweeps, and correlation matrix (**Table IV**, **Table VI**, and **Table VII**).
  * `results-scaled-eval/`: Scaled JPF complete evaluations on Factories and Guava (**Table V**).
  * `results-budget-eval/`: Scaled budget-constrained JPF evaluations on Factories and Guava (**Table V**).
  * `results-mini-eval/`: Joda-Time budgeted JPF evaluations (**Table V**).
  * `results-sci-budget/`: JPF VM-level metrics and causal profiling dataset (**Table II**).
  * `results-oop-realbatch1-fix/`: Matched pairwise exceptions and dynamic dispatch study logs (**Table I**).
  * `results-opensource/`: Matched pairwise libraries study logs (**Table III**).
  * `results-treemap-budget/`: Additional budget sweep JPF evaluations on TreeMap.
* **`structural_taxonomy.md`**: Companion taxonomy reference mapping control-flow and JVM features across all evaluated workloads.
* **`system_metric_correlations.md`**: Summarizes the Pearson and Spearman rank correlation coefficients computed across all campaign runs (**Table IV** / Section V-B).
* **`ols_coefficients.md`**: Standardized OLS regression coefficients and relative effect sizes for JVM metrics (Section VII).
* **`weight_stability_calibration.md`**: Standardized weights comparison across manual SCI, OLS, Ridge, LASSO, Elastic Net, and OLS bootstrapping confidence intervals (Section VII-C).

---

## Reproduction & Verification Steps

### 1. Prerequisites
Ensure Python 3.x is installed with `numpy` and `matplotlib` packages.

### 2. Generating Plots & Correlation Matrices
To regenerate all figures and metrics from the raw campaign dataset:
* Open a terminal and navigate to the `code/` directory.
* Run `python generate_icse_figures.py` to regenerate `fig1` to `fig5` inside the `figures/` directory.
* Run `python calculate_correlations.py` to compute and display the Pearson/Spearman correlation matrices.
* Run `python check_sci_weight_sensitivity.py` to print the sensitivity check concordance values and constant-state group metrics.
* Run `python calculate_ols_coefficients.py` to compute and display raw vs. reported OLS coefficients and relative effect size contributions.
* Run `python compute_lofo.py` to execute the Leave-One-Family-Out validation and output the cross-workload Spearman correlation and $R^2$ table (**Table VII**).
* Run `python verify_n420.py` to confirm that exactly 420 robust campaign runs are present in `results-robust-campaign/` (the $n=420$ claim in the paper).
* Run `python verify_joda.py` to verify the Joda-Time elapsed/engine/solver medians against **Table V**.


### 3. Re-running Heuristic Search Scheduling Campaigns (Table V)
To execute the BFS, DFS, and SCISearch scheduling comparison:
* Set up Java 8 and configure JPF path locations inside `code/run_sci_evaluation.py`.
* Run `python run_sci_evaluation.py` to trigger the campaigns. It will execute the runs, save raw logs to `results/results-scaled-eval/`, and print the scheduling performance table (**Table V**).

### 4. Re-running the Robust Campaign (OLS Profiling Data)
To re-run the combinatorial robust JPF campaign and collect fresh SCI profiling data:
* Navigate to the `code/` directory.
* Execute the PowerShell script `run_sci_robust_campaign.ps1` to clean existing folder logs, trigger JPF sweeps across configurations using SCISearch, and save fresh logs to `results-robust-campaign/`.
* Run the plotting and correlation python scripts to see the updated figures and matrices.

### 5. Re-running the JVM-style OOP Feature Overhead Campaign (Table I & Table II)
To re-run the dynamic dispatch and exception overhead experiments:
* Navigate to the `code/` directory.
* Execute the PowerShell script `run-oop-study.ps1` to clean existing folder logs, execute JPF, and print the matched comparison summary.
* To collect the direct VM-level causal attribution profiling metrics (**Table II**):
  * Execute the PowerShell script `harvest_causal_evidence.ps1`.
  * This script runs JPF on the polymorphic dynamic dispatch configuration and its branch control baseline at depth 6. It prints the VM execution metrics comparison table and saves the result to `results/results-sci-budget/causal_profiling.csv`.


---

## Notes on Search Strategies

* **Additional Baselines in Raw Logs**: The raw dataset in `results-robust-campaign/` contains execution runs for additional baseline strategies, specifically **Random** (`Random`) and **Coverage Frequency** (`CoverageFrequency`). While the paper focuses on the primary comparison between the standard JPF strategies (**BFS** and **DFS**) and **SCI**, these additional baseline runs are preserved in the raw logs for completeness and extended analysis.
