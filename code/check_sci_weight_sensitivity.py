import os
import glob
import csv
import numpy as np

# Concordance index helper
def concordance_index(y_true, y_pred):
    n = len(y_true)
    concordant = 0
    discordant = 0
    ties = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            if y_true[i] != y_true[j]:
                # check direction
                pred_diff = y_pred[i] - y_pred[j]
                true_diff = y_true[i] - y_true[j]
                
                # We want higher y_pred to mean higher y_true (runtime)
                if pred_diff * true_diff > 0:
                    concordant += 1
                elif pred_diff == 0:
                    ties += 1
                else:
                    discordant += 1
                    
    total = concordant + discordant + ties
    if total == 0:
        return 0.5
    return (concordant + 0.5 * ties) / total

results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "results-robust-campaign"))
summary_files = glob.glob(os.path.join(results_dir, "*_limit_*_summary.csv"))

# Workload configurations from paper for McCabe complexity
workload_metrics = {
    "real-configresolver": {"loc": 75, "branches": 16, "mccabe": 17},
    "real-expressionevaluator": {"loc": 60, "branches": 14, "mccabe": 15},
    "real-expressionevaluator-control": {"loc": 45, "branches": 10, "mccabe": 11},
    "real-jsonparser": {"loc": 85, "branches": 18, "mccabe": 19},
    "real-jsonparser-control": {"loc": 55, "branches": 12, "mccabe": 13},
    "adverse-dispatch-branches": {"loc": 40, "branches": 8, "mccabe": 9},
    "mixed-dispatch-branches": {"loc": 30, "branches": 6, "mccabe": 7},
    "real-factories-depth6-realstyle": {"loc": 45, "branches": 12, "mccabe": 13},
    "real-treemap": {"loc": 50, "branches": 12, "mccabe": 13},
    "real-decisiongraph": {"loc": 65, "branches": 15, "mccabe": 16},
    "real-scalability-branchfactor": {"loc": 35, "branches": 8, "mccabe": 9},
    "real-scalability-cardinality": {"loc": 35, "branches": 8, "mccabe": 9},
    "real-scalability-dispatch": {"loc": 35, "branches": 8, "mccabe": 9},
    "real-scalability-objectgraph": {"loc": 35, "branches": 8, "mccabe": 9},
}
for i in range(1, 20):
    name = f"real-exceptions{i}"
    workload_metrics[name] = {"loc": 30, "branches": 6, "mccabe": 7}

runs_data = []
for f in summary_files:
    basename = os.path.basename(f)
    parts = basename.split("_limit_")
    wl_name = parts[0]
    for suffix in ["_SCI", "_BFS", "_DFS", "_Random", "_CoverageFrequency", "_SCIPure"]:
        if wl_name.endswith(suffix):
            wl_name = wl_name[:-len(suffix)]
            break
            
    metrics = workload_metrics.get(wl_name)
    if not metrics:
        if wl_name.startswith("real-exceptions"):
            metrics = {"loc": 30, "branches": 6, "mccabe": 7}
        else:
            continue
            
    # Exclude configresolver, expressionevaluator, and jsonparser to match the 420 completed runs campaign
    if any(x in wl_name for x in ["configresolver", "expressionevaluator", "jsonparser"]):
        continue
            
    with open(f, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                runtime_ms = float(row['engine_time_ns']) / 1e6
                cgs = float(row['choice_generators'])
                heap_bytes = float(row['heap_allocations_bytes'])
                heap_mb = heap_bytes / (1024.0 * 1024.0)
                new_states = float(row['new_states'])
                
                runs_data.append({
                    'runtime': runtime_ms,
                    'heap_mb': heap_mb,
                    'cgs': cgs,
                    'new_states': new_states,
                    'mccabe': metrics['mccabe']
                })
            except Exception as e:
                continue

print(f"Loaded {len(runs_data)} runs")
y = np.array([r['runtime'] for r in runs_data])
cgs = np.array([r['cgs'] for r in runs_data])
heap = np.array([r['heap_mb'] for r in runs_data])
states = np.array([r['new_states'] for r in runs_data])
mccabe = np.array([r['mccabe'] for r in runs_data])

# 1. Sweep w2 from 0 to 50 for Overall concordance
print("\n=== Weight Sensitivity Sweep (Overall C-index) ===")
print("w2  | C-index")
print("----|--------")
for w2 in [0.0, 1.0, 2.0, 5.0, 10.0, 20.0, 25.0, 30.0, 50.0]:
    sci = cgs + w2 * heap
    c_index = concordance_index(y, sci)
    print(f"{w2:3.1f} | {c_index:.5f}")

# 2. Print per constant-state group concordance indices for state, mccabe, and sci (w2 = 5.0)
print("\n=== Per Constant-State Group Concordance Index ===")
print("Group      | Runs | State Count | McCabe Comp | SCI (w2=5.0)")
print("-----------|------|-------------|-------------|-------------")

# Overall
sci_all = cgs + 5.0 * heap
c_state = concordance_index(y, states)
c_mccabe = concordance_index(y, mccabe)
c_sci = concordance_index(y, sci_all)
print(f"Overall    | {len(runs_data):4d} | {c_state:11.4f} | {c_mccabe:11.4f} | {c_sci:11.4f}")

# Constant-state groups discussed in the paper
target_ns = [7, 13, 19, 25, 52, 502]
for n_val in target_ns:
    group_runs = [r for r in runs_data if int(r['new_states']) == n_val]
    if len(group_runs) > 1:
        y_g = [r['runtime'] for r in group_runs]
        states_g = [r['new_states'] for r in group_runs]
        mccabe_g = [r['mccabe'] for r in group_runs]
        sci_g = [r['cgs'] + 5.0 * r['heap_mb'] for r in group_runs]
        
        cg_state = concordance_index(y_g, states_g)
        cg_mccabe = concordance_index(y_g, mccabe_g)
        cg_sci = concordance_index(y_g, sci_g)
        print(f"N = {n_val:<6d} | {len(group_runs):4d} | {cg_state:11.4f} | {cg_mccabe:11.4f} | {cg_sci:11.4f}")
