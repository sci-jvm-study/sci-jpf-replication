import os
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt

# Set Matplotlib parameters for professional academic figures (Times New Roman / Serif style)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif", "Nimbus Roman", "serif"],
    "font.size": 9.5,
    "axes.titlesize": 11,
    "axes.labelsize": 10.5,
    "xtick.labelsize": 9.0,
    "ytick.labelsize": 9.0,
    "legend.fontsize": 9.0,
    "figure.titlesize": 12.0,
    "axes.grid": True,
    "grid.color": "#e2e8f0",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
})

# Resolve base directory relative to this script
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

cas_dir = os.path.join(base_dir, "Artifacts", "results", "results-robust-campaign")
oop_dir = os.path.join(base_dir, "Artifacts", "results", "results-oop-realbatch1-fix")

# Output Directories
output_dirs = [
    os.path.join(base_dir, "Artifacts", "figures"),
    os.path.join(base_dir, "figures"),
]

for d in output_dirs:
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------
# 1. WORKLOAD METRICS & TAXONOMY CONFIGURATION
# ----------------------------------------------------
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
    if name not in workload_metrics:
        workload_metrics[name] = {"loc": 30, "branches": 6, "mccabe": 7}

# ----------------------------------------------------
# 2. LOAD DATA
# ----------------------------------------------------
robust_runs = []
robust_files = glob.glob(os.path.join(cas_dir, "*_limit_*_summary.csv"))

for f in robust_files:
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
                heap_bytes = float(row['heap_allocations_bytes'])
                runtime_ms = float(row['engine_time_ns']) / 1e6
                states = float(row['choice_generators']) + float(row['pc_choice_generators'])
                new_states = float(row['new_states'])
                cgs = float(row['choice_generators'])
                pc_cgs = float(row['pc_choice_generators'])
                heap_mb = heap_bytes / (1024.0 * 1024.0)
                
                is_synthetic = "dispatch-branches" in wl_name or "synthetic" in wl_name
                
                if "decisiongraph" in wl_name:
                    family = "decisiongraph"
                elif "treemap" in wl_name:
                    family = "treemap"
                elif "exception" in wl_name:
                    family = "exceptions"
                elif "factories" in wl_name or "factory" in wl_name:
                    family = "factories"
                elif is_synthetic:
                    family = "synthetic"
                else:
                    family = "other"
                    
                robust_runs.append({
                    'wl': wl_name,
                    'runtime': runtime_ms,
                    'states': states,
                    'new_states': new_states,
                    'cgs': cgs,
                    'pc_cgs': pc_cgs,
                    'heap_mb': heap_mb,
                    'is_synthetic': is_synthetic,
                    'family': family,
                    'mccabe': metrics['mccabe']
                })
            except (KeyError, ValueError, TypeError):
                continue

all_campaign_runs = []

def load_all_campaign(directory, category):
    files = glob.glob(os.path.join(directory, "*_summary.csv"))
    for f in files:
        with open(f, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    engine_ms = float(row.get('engine_time_ns', 0) or row.get('elapsed_time_ns', 0)) / 1e6
                    if engine_ms <= 0:
                        continue
                    states = float(row.get('states', 0) or row.get('new_states', 0) or row.get('explored_states', 0))
                    if states <= 0:
                        continue
                    heap_mb = float(row.get('heap_allocations_bytes', 0)) / (1024.0 * 1024.0)
                    q_size = float(row.get('max_queue_size', 0))
                    gc = float(row.get('gc_cycles', 0))
                    cgs = float(row.get('choice_generators', 0))
                    pc_cgs = float(row.get('pc_choice_generators', 0))
                    
                    benchmark = row.get('benchmark', '').lower()
                    wl_name = os.path.basename(f).split('_summary')[0]
                    
                    # Exclude configresolver, expressionevaluator, and jsonparser to match the 420 completed runs campaign
                    if any(x in wl_name for x in ["configresolver", "expressionevaluator", "jsonparser"]):
                        continue
                    
                    if "decisiongraph" in benchmark or "decisiongraph" in wl_name:
                        family = "decisiongraph"
                    elif "treemap" in benchmark or "treemap" in wl_name:
                        family = "treemap"
                    elif "exception" in benchmark or "exception" in wl_name:
                        family = "exceptions"
                    elif "factory" in benchmark or "factories" in benchmark or "factory" in wl_name or "factories" in wl_name:
                        family = "factories"
                    elif "adverse" in benchmark or "mixed" in benchmark or "adverse" in wl_name or "mixed" in wl_name:
                        family = "synthetic"
                    else:
                        family = "other"
                        
                    all_campaign_runs.append({
                        'wl': wl_name,
                        'runtime': engine_ms,
                        'states': states,
                        'cgs': cgs,
                        'pc_cgs': pc_cgs,
                        'heap_mb': heap_mb,
                        'gc': gc,
                        'q_size': q_size,
                        'family': family,
                        'category': category
                    })
                except Exception:
                    continue

load_all_campaign(cas_dir, "cas_robust")
load_all_campaign(oop_dir, "oop_pairwise")

print(f"Loaded {len(robust_runs)} robust runs, {len(all_campaign_runs)} campaign runs.")

# ----------------------------------------------------
# 3. STYLING CONFIGURATIONS
# ----------------------------------------------------
FAMILY_STYLES = {
    "synthetic": {"color": "#d95f02", "marker": "o", "label": "Synthetic Dispatch"},
    "decisiongraph": {"color": "#7570b3", "marker": "s", "label": "DecisionGraph"},
    "treemap": {"color": "#1b9e77", "marker": "D", "label": "TreeMap Simple"},
    "factories": {"color": "#7e2f8e", "marker": "^", "label": "OOP Factories"},
    "exceptions": {"color": "#666666", "marker": "v", "label": "Exception Unwind"},
    "other": {"color": "#a6761d", "marker": "h", "label": "Config & Parsers"}
}

def OLS_fit(x, y):
    A = np.column_stack((np.ones(len(x)), x))
    return np.linalg.pinv(A.T @ A) @ A.T @ y

# Helper to save figures across multiple directories
def save_fig(name):
    for d in output_dirs:
        # Save SVG
        path_svg = os.path.join(d, f"{name}.svg")
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        # Save PDF
        path_pdf = os.path.join(d, f"{name}.pdf")
        plt.savefig(path_pdf, format='pdf', bbox_inches='tight')
    plt.close()

# ----------------------------------------------------
# FIGURE 1: Explored States vs. Engine Latency
# ----------------------------------------------------
def make_fig1():
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.grid(True, axis='y')
    ax.grid(False, axis='x')
    
    # Extract data (using new_states for explored states)
    x_val = np.array([r['new_states'] for r in robust_runs])
    y_val = np.array([r['runtime'] for r in robust_runs])
    
    # Regression line
    beta = OLS_fit(x_val, y_val)
    x_grid = np.linspace(0, 1100, 100)
    y_pred = beta[0] + beta[1] * x_grid
    ax.plot(x_grid, y_pred, color='#475569', linestyle='--', linewidth=1.2, label='Baseline Fit')
    
    # Scatter points grouped by family
    for fam, style in FAMILY_STYLES.items():
        fam_runs = [r for r in robust_runs if r['family'] == fam]
        if not fam_runs:
            continue
        xs = [r['new_states'] for r in fam_runs]
        ys = [r['runtime'] for r in fam_runs]
        ax.scatter(xs, ys, color=style['color'], marker=style['marker'], 
                   edgecolors='black', linewidths=0.5, alpha=0.75, s=35, label=style['label'])
        
    # Calculate R^2 dynamically
    ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
    ss_res = np.sum((y_val - (beta[0] + beta[1] * x_val)) ** 2)
    r2 = 1.0 - (ss_res / ss_tot)
    
    ax.text(820, beta[0] + beta[1]*820 - 75, f"R² = {r2:.4f} (Baseline)", 
            color='#334155', fontsize=9.5, fontweight='bold', ha='center')
    
    ax.set_xlim(0, 1100)
    ax.set_ylim(0, 1300)
    ax.set_xlabel("Explored States")
    ax.set_ylabel("Engine Latency (ms)")
    
    # Clean and tight layout legend
    ax.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', framealpha=0.9, loc='upper left')
    save_fig("fig1_state_count_failure")

# ----------------------------------------------------
# FIGURE 2: Latency Variance under Constant States
# ----------------------------------------------------
def make_fig2():
    runs_502 = [r for r in all_campaign_runs if abs(r['states'] - 502) < 0.1]
    
    families = ["treemap", "decisiongraph", "factories"]
    labels = ["TreeMap Simple", "DecisionGraph Routing", "Polymorphic Factories"]
    
    data = []
    for fam in families:
        times = [r['runtime'] for r in runs_502 if r['family'] == fam]
        times.sort()
        data.append(times)
        
    fig, ax = plt.subplots(figsize=(4.8, 3.5))
    ax.grid(True, axis='y')
    ax.grid(False, axis='x')
    
    # Make boxplot
    bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                    medianprops=dict(color='white', linewidth=2.0),
                    whiskerprops=dict(color='#334155', linewidth=1.2),
                    capprops=dict(color='#334155', linewidth=1.2),
                    boxprops=dict(linewidth=1.2))
    
    # Color the boxes
    for idx, patch in enumerate(bp['boxes']):
        fam = families[idx]
        color = FAMILY_STYLES[fam]['color']
        patch.set_facecolor(color)
        patch.set_edgecolor('black')
        patch.set_alpha(0.8)
        
    # Annotate medians and group size
    for idx, fam in enumerate(families):
        times = data[idx]
        n = len(times)
        median_val = np.median(times)
        max_val = max(times)
        ax.text(idx + 1, max_val + 35, f"Median: {median_val:.1f} ms\n(n = {n})", 
                ha='center', fontsize=9.0, color='#0f172a', fontweight='bold')
        
    ax.set_xticklabels(labels, fontweight='bold')
    ax.set_ylabel("Engine Latency (ms)")
    ax.set_ylim(0, 1350)
    ax.set_xlabel("Workload Configuration (Constant Explore States N_states = 502)", labelpad=10)
    
    save_fig("fig2_constant_state_variance")

# ----------------------------------------------------
# FIGURE 3: Residual Recovery (SCI vs residuals)
# ----------------------------------------------------
def make_fig3():
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.grid(True, axis='y')
    ax.grid(False, axis='x')
    
    x_states = np.array([r['new_states'] for r in robust_runs])
    y_time = np.array([r['runtime'] for r in robust_runs])
    beta_states = OLS_fit(x_states, y_time)
    y_pred_states = beta_states[0] + beta_states[1] * x_states
    
    residuals = y_time - y_pred_states
    x_sci = np.array([r['cgs'] + 5.0 * r['heap_mb'] for r in robust_runs])
    
    # Orthogonalize x_sci against states (regress out the state count baseline from SCI)
    beta_sci_states = OLS_fit(x_states, x_sci)
    x_sci_pred = beta_sci_states[0] + beta_sci_states[1] * x_states
    sci_residuals = x_sci - x_sci_pred
    
    beta_resid = OLS_fit(sci_residuals, residuals)
    
    # Plot zero reference line
    ax.axhline(0, color='#94a3b8', linestyle=':', linewidth=1.2)
    
    # Scatter plot
    for fam, style in FAMILY_STYLES.items():
        indices = [i for i, r in enumerate(robust_runs) if r['family'] == fam]
        if not indices:
            continue
        xs = sci_residuals[indices]
        ys = residuals[indices]
        ax.scatter(xs, ys, color=style['color'], marker=style['marker'], 
                   edgecolors='black', linewidths=0.5, alpha=0.75, s=35, label=style['label'])
        
    # Regression line
    x_grid = np.linspace(-50, 50, 100)
    y_pred = beta_resid[0] + beta_resid[1] * x_grid
    ax.plot(x_grid, y_pred, color='#0072bd', linewidth=1.8, label='Residual Trend')
    
    # Calculate R^2 dynamically (should be 0.7334)
    ss_tot_res = np.sum((residuals - np.mean(residuals)) ** 2)
    ss_res_res = np.sum((residuals - (beta_resid[0] + beta_resid[1] * sci_residuals)) ** 2)
    r2_res = 1.0 - (ss_res_res / ss_tot_res)
    
    ax.text(0, 450, f"Residual Fit R² = {r2_res:.4f}", 
            color='#0072bd', fontsize=9.5, fontweight='bold', ha='center')
    
    ax.set_xlim(-50, 50)
    ax.set_ylim(-400, 600)
    ax.set_xlabel("State-Orthogonalized SCI Residuals")
    ax.set_ylabel("Engine Latency Residuals (ms)")
    ax.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', framealpha=0.9, loc='upper right')
    
    save_fig("fig3_residual_recovery")


# ----------------------------------------------------
# FIGURE 4: Synthetic-to-Real Generalization Failure
# ----------------------------------------------------
def make_fig4():
    synthetic_runs = [r for r in robust_runs if r['is_synthetic']]
    real_runs = [r for r in robust_runs if not r['is_synthetic']]
    
    def get_features(runs):
        return np.column_stack((
            [r['new_states'] for r in runs],
            [r['heap_mb'] for r in runs],
            [r['cgs'] for r in runs]
        ))
        
    X_synth = get_features(synthetic_runs)
    y_synth = np.array([r['runtime'] for r in synthetic_runs])
    
    X_real = get_features(real_runs)
    y_real = np.array([r['runtime'] for r in real_runs])
    
    beta_synth = np.linalg.pinv(np.column_stack((np.ones(len(y_synth)), X_synth))) @ y_synth
    y_pred_real = np.column_stack((np.ones(len(y_real)), X_real)) @ beta_synth
    
    beta_real = np.linalg.pinv(np.column_stack((np.ones(len(y_real)), X_real))) @ y_real
    y_pred_synth = np.column_stack((np.ones(len(y_synth)), X_synth)) @ beta_real
    
    # Calculate out-of-sample R^2 dynamically
    ss_tot_real = np.sum((y_real - np.mean(y_real)) ** 2)
    ss_res_real = np.sum((y_real - y_pred_real) ** 2)
    r2_synth_to_real = 1.0 - (ss_res_real / ss_tot_real) if ss_tot_real > 0 else 0.0
    
    ss_tot_synth = np.sum((y_synth - np.mean(y_synth)) ** 2)
    ss_res_synth = np.sum((y_synth - y_pred_synth) ** 2)
    r2_real_to_synth = 1.0 - (ss_res_synth / ss_tot_synth) if ss_tot_synth > 0 else 0.0
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 4.0), sharey=True)
    
    # Common layout settings
    for ax in (ax1, ax2):
        ax.grid(True, axis='y')
        ax.grid(False, axis='x')
        ax.plot([0, 1300], [0, 1300], color='#94a3b8', linestyle=':', linewidth=1.2)
        ax.set_xlim(0, 1300)
        ax.set_ylim(0, 1300)
        ax.set_xlabel("Predicted Runtime (ms)")
        
    ax1.set_ylabel("Actual Engine Runtime (ms)")
    
    # Panel A: Train Synthetic, Test Real (legend here — all real-run families shown)
    for fam, style in FAMILY_STYLES.items():
        indices = [i for i, r in enumerate(real_runs) if r['family'] == fam]
        if not indices:
            continue
        xs = y_pred_real[indices]
        ys = y_real[indices]
        ax1.scatter(xs, ys, color=style['color'], marker=style['marker'],
                    edgecolors='black', linewidths=0.5, alpha=0.75, s=35, label=style['label'])

    ax1.set_title("Panel A: Train Synthetic, Test Real", fontweight='bold', pad=12)
    ax1.text(650, 1180, f"Out-of-sample R² = {r2_synth_to_real:.4f}", color='#be123c', fontweight='bold', fontsize=9.5, ha='center')
    ax1.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', framealpha=0.9, loc='lower right')

    # Panel B: Train Real, Test Synthetic (only synthetic dispatch points — no dummy entries)
    for fam, style in FAMILY_STYLES.items():
        indices = [i for i, r in enumerate(synthetic_runs) if r['family'] == fam]
        if not indices:
            continue
        xs = y_pred_synth[indices]
        ys = y_synth[indices]
        ax2.scatter(xs, ys, color=style['color'], marker=style['marker'],
                    edgecolors='black', linewidths=0.5, alpha=0.75, s=35, label=style['label'])

    ax2.set_title("Panel B: Train Real, Test Synthetic", fontweight='bold', pad=12)
    ax2.text(650, 1180, f"Out-of-sample R² = {r2_real_to_synth:.4f}", color='#be123c', fontweight='bold', fontsize=9.5, ha='center')
    ax2.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', framealpha=0.9, loc='lower right')
    
    plt.tight_layout()
    save_fig("fig5_synthetic_to_real_failure")

# ----------------------------------------------------
# FIGURE 5: Ranking Accuracy (Concordance Index)
# ----------------------------------------------------
def make_fig5():
    # Helper to calculate Harrell's Concordance Index
    def concordance_index(y_true, y_pred):
        n = len(y_true)
        concordant = 0
        discordant = 0
        ties = 0
        for i in range(n):
            for j in range(i + 1, n):
                if y_true[i] != y_true[j]:
                    pred_diff = y_pred[i] - y_pred[j]
                    true_diff = y_true[i] - y_true[j]
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

    # Extract overall metrics
    y_all = [r['runtime'] for r in robust_runs]
    sci_all = [r['cgs'] + 5.0 * r['heap_mb'] for r in robust_runs]
    states_all = [r['new_states'] for r in robust_runs]
    mccabe_all = [r['mccabe'] for r in robust_runs]
    
    overall_state = concordance_index(y_all, states_all)
    overall_mccabe = concordance_index(y_all, mccabe_all)
    overall_sci = concordance_index(y_all, sci_all)
    
    groups = [{"label": "Overall", "state": overall_state, "mccabe": overall_mccabe, "sci": overall_sci}]
    
    # We sweep the exact constant-state groups discussed in the paper: N = 7, 13, 19, 25, 52, 502
    target_ns = [7, 13, 19, 25, 52, 502]
    for n_val in target_ns:
        group_runs = [r for r in robust_runs if int(r['new_states']) == n_val]
        if len(group_runs) > 1:
            y_g = [r['runtime'] for r in group_runs]
            sci_g = [r['cgs'] + 5.0 * r['heap_mb'] for r in group_runs]
            states_g = [r['new_states'] for r in group_runs]
            mccabe_g = [r['mccabe'] for r in group_runs]
            
            c_state = concordance_index(y_g, states_g)
            c_mccabe = concordance_index(y_g, mccabe_g)
            c_sci = concordance_index(y_g, sci_g)
            
            groups.append({
                "label": f"N = {n_val}",
                "state": c_state,
                "mccabe": c_mccabe,
                "sci": c_sci
            })
            
    labels = [g['label'] for g in groups]
    state_vals = [g['state'] for g in groups]
    mccabe_vals = [g['mccabe'] for g in groups]
    sci_vals = [g['sci'] for g in groups]
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.grid(True, axis='y')
    ax.grid(False, axis='x')
    
    # Plot bars with distinctive hatching patterns for grayscale readability
    rects1 = ax.bar(x - width, state_vals, width, label='State Count Baseline', 
                    color='#cbd5e1', edgecolor='#475569', hatch='', linewidth=1.0)
    rects2 = ax.bar(x, mccabe_vals, width, label='McCabe Complexity', 
                    color='#e0a96d', edgecolor='#b45309', hatch='//', linewidth=1.0)
    rects3 = ax.bar(x + width, sci_vals, width, label='SCI Complexity (Ours)', 
                    color='#002d62', edgecolor='#0f172a', hatch='..', linewidth=1.0)
    
    ax.set_ylabel("Harrell's Concordance Index (C-index)")
    ax.set_xlabel("Workload State-Count Groups")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontweight='bold')
    ax.set_ylim(0.40, 1.00)
    
    # Legend
    ax.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', framealpha=0.9, loc='upper right')
    
    # Add vertical divider lines between ticks for visual grouping
    for val in range(len(labels) - 1):
        ax.axvline(val + 0.5, color='#e2e8f0', linestyle='-', linewidth=0.5)
        
    save_fig("fig4_ranking_accuracy")

if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    print("All figures successfully generated in SVG vector format.")
