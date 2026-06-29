import os
import glob
import csv
import math

results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "results-robust-campaign"))
summary_files = glob.glob(os.path.join(results_dir, "*_limit_*_summary.csv"))

# Data lists for correlation calculation
engine_latency_list = []
heap_alloc_list = []
queue_growth_list = []
gc_cycles_list = []
type_cg_density_list = []

EXCLUDE_WORKLOADS = ["configresolver", "expressionevaluator", "jsonparser"]

for f in summary_files:
    basename = os.path.basename(f)
    wl_name = basename.split("_limit_")[0]
    for suffix in ["_SCI", "_BFS", "_DFS", "_Random", "_CoverageFrequency", "_SCIPure"]:
        if wl_name.endswith(suffix):
            wl_name = wl_name[:-len(suffix)]
            break
    if any(x in wl_name for x in EXCLUDE_WORKLOADS):
        continue
    with open(f, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Engine latency in ms
                engine_ms = float(row['engine_time_ns']) / 1e6
                # Heap allocations in MB
                heap_mb = float(row['heap_allocations_bytes']) / (1024.0 * 1024.0)
                # Queue size
                q_size = float(row['max_queue_size'])
                # GC cycles
                gc = float(row['gc_cycles'])
                
                # TypeCG density = pc_choice_generators / (choice_generators + 1.0)
                cgs = float(row['choice_generators'])
                pc_cgs = float(row['pc_choice_generators'])
                density = pc_cgs / (cgs + 1.0)
                
                engine_latency_list.append(engine_ms)
                heap_alloc_list.append(heap_mb)
                queue_growth_list.append(q_size)
                gc_cycles_list.append(gc)
                type_cg_density_list.append(density)
            except Exception as e:
                # Skip any malformed or incomplete rows
                continue

n = len(engine_latency_list)
print(f"Loaded {n} data points for system correlation profiling.")

if n < 3:
    print("Insufficient data for correlation calculation.")
    exit(1)

def mean(x):
    return sum(x) / len(x)

def std_dev(x, mx):
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

def spearman(x, y):
    rx = rankdata(x)
    ry = rankdata(y)
    return pearson(rx, ry)

variables = {
    "Engine Latency (ms)": engine_latency_list,
    "Heap Allocations (MB)": heap_alloc_list,
    "Queue Growth (States)": queue_growth_list,
    "GC Cycles": gc_cycles_list,
    "TypeCG Density": type_cg_density_list
}

var_names = list(variables.keys())

# Print Markdown correlation matrix
md_output = "# Causal Attributions and JVM Metric Correlations\n\n"
md_output += "Below is the Pearson / Spearman rank correlation matrix computed across all campaign runs. Each cell contains `Pearson (Spearman)` coefficients.\n\n"
md_output += "| Metric | " + " | ".join(var_names) + " |\n"
md_output += "| :--- | " + " | ".join([":---:" for _ in var_names]) + " |\n"

for name_y in var_names:
    row_str = f"| **{name_y}** | "
    row_cells = []
    for name_x in var_names:
        p_val = pearson(variables[name_y], variables[name_x])
        s_val = spearman(variables[name_y], variables[name_x])
        row_cells.append(f"{p_val:.3f} ({s_val:.3f})")
    row_str += " | ".join(row_cells) + " |\n"
    md_output += row_str

print(md_output)

# Save to artifacts directory
out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "system_metric_correlations.md"))
with open(out_path, 'w') as f:
    f.write(md_output)

print(f"Successfully computed correlations and saved to: {out_path}")
