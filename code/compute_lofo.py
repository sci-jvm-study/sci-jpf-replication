import os
import glob
import csv
import numpy as np

# Resolve results directory relative to this script
results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "results-robust-campaign"))
files = glob.glob(os.path.join(results_dir, "*_limit_*_summary.csv"))

# Mapping of workload base names to families
families_map = {
    "real-configresolver": "config",
    "real-decisiongraph": "decisiongraph",
    "real-expressionevaluator": "expression",
    "real-expressionevaluator-control": "expression",
    "real-factories-depth6-realstyle": "factories",
    "real-jsonparser": "json",
    "real-jsonparser-control": "json",
    "real-treemap": "treemap",
    "adverse-dispatch-branches": "synthetic",
    "mixed-dispatch-branches": "synthetic"
}

all_runs = []
for f in files:
    basename = os.path.basename(f)
    wl_name = basename.split("_limit_")[0]
    for suffix in ["_SCI", "_BFS", "_DFS", "_Random", "_CoverageFrequency", "_SCIPure"]:
        if wl_name.endswith(suffix):
            wl_name = wl_name[:-len(suffix)]
            break
            
    family = families_map.get(wl_name)
    if not family:
        continue
        
    with open(f, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                runtime_ms = float(row['engine_time_ns']) / 1e6
                cgs = float(row['choice_generators'])
                pc_cgs = float(row['pc_choice_generators'])
                heap_bytes = float(row['heap_allocations_bytes'])
                heap_mb = heap_bytes / (1024.0 * 1024.0)
                new_states = float(row['new_states'])
                gc = float(row['gc_cycles'])
                q_size = float(row['max_queue_size'])
                
                all_runs.append({
                    'wl': wl_name,
                    'family': family,
                    'runtime': runtime_ms,
                    'new_states': new_states,
                    'pc_cgs': pc_cgs,
                    'heap_mb': heap_mb,
                    'gc_cycles': gc,
                    'queue_size': q_size
                })
            except Exception as e:
                continue

# Custom rank data & Spearman/Pearson functions to avoid external dependencies like scipy
def mean(x):
    return sum(x) / len(x)

def std_dev(x, mx):
    import math
    return math.sqrt(sum((xi - mx) ** 2 for xi in x))

def pearson(x, y):
    mx = mean(x)
    my = mean(y)
    numerator = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    denom = std_dev(x, mx) * std_dev(y, my)
    return numerator / denom if denom > 0 else 0.0

def rankdata(values):
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
      j = i
      while j < len(indexed) and indexed[j][1] == indexed[i][1]:
        j += 1
      avg_rank = (i + 1 + j) / 2.0
      for k in range(i, j):
        ranks[indexed[k][0]] = avg_rank
      i = j
    return ranks

def get_spearman(x, y):
    rx = rankdata(x)
    ry = rankdata(y)
    return pearson(rx, ry)

def get_r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

families = ["config", "decisiongraph", "expression", "factories", "json", "treemap"]

print("=====================================================================")
print("  Leave-One-Family-Out (LOFO) Cross-Workload Validation Results      ")
print("=====================================================================")
print(f"{'Left-Out Family':<15} | {'Test Spearman rho':<18} | {'Train R^2':<10} | {'Test R^2':<10}")
print("-" * 65)

latex_lines = []
for left_out in families:
    # Split train and test sets
    train_runs = [r for r in all_runs if r['family'] != left_out]
    test_runs = [r for r in all_runs if r['family'] == left_out]
    
    y_train = np.array([r['runtime'] for r in train_runs])
    X_train = np.column_stack((
        [r['new_states'] for r in train_runs],
        [r['pc_cgs'] for r in train_runs],
        [r['heap_mb'] for r in train_runs],
        [r['gc_cycles'] for r in train_runs],
        [r['queue_size'] for r in train_runs]
    ))
    
    y_test = np.array([r['runtime'] for r in test_runs])
    X_test = np.column_stack((
        [r['new_states'] for r in test_runs],
        [r['pc_cgs'] for r in test_runs],
        [r['heap_mb'] for r in test_runs],
        [r['gc_cycles'] for r in test_runs],
        [r['queue_size'] for r in test_runs]
    ))
    
    # Standardize train features & target
    y_mean, y_std = np.mean(y_train), np.std(y_train)
    X_mean = np.mean(X_train, axis=0)
    X_std = np.std(X_train, axis=0)
    X_std[X_std == 0] = 1.0
    
    y_train_norm = (y_train - y_mean) / y_std
    X_train_norm = (X_train - X_mean) / X_std
    X_test_norm = (X_test - X_mean) / X_std
    
    # Fit OLS model on normalized training data (no intercept needed when fully standardized)
    beta = np.linalg.pinv(X_train_norm.T @ X_train_norm) @ X_train_norm.T @ y_train_norm
    
    # Train R^2
    y_train_pred_norm = X_train_norm @ beta
    train_r2 = get_r2(y_train_norm, y_train_pred_norm)
    
    # Test Prediction & Scaling back
    y_test_pred_norm = X_test_norm @ beta
    y_test_pred = y_test_pred_norm * y_std + y_mean
    
    # Evaluate Test R^2 and Spearman rho
    test_r2 = get_r2(y_test, y_test_pred)
    test_rho = get_spearman(y_test, y_test_pred)
    
    print(f"{left_out:<15} | {test_rho:18.4f} | {train_r2:10.4f} | {test_r2:10.4f}")
    latex_lines.append(f"{left_out} & {test_rho:.4f} & {train_r2:.4f} & {test_r2:.4f} \\\\")

print("-" * 65)
print("\nLaTeX Code for Table VII:")
for line in latex_lines:
    print(line)
