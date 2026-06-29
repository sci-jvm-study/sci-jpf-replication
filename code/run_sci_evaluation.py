import subprocess
import os
import csv
import time
import statistics

# Define JAVA_HOME. Set JAVA_HOME environment variable or modify the path below.
# Must point to a Java 8 (1.8.x) installation.
java_home = os.environ.get("JAVA_HOME", r"C:\Program Files\RedHat\java-1.8.0-openjdk-1.8.0.422-1")
java_exe = os.path.join(java_home, "bin", "java.exe")
# Resolve relative workspace path (3 levels up from Artifacts/code)
workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
run_jpf_jar = os.path.join(workspace, "jpf-core-symbc", "build", "RunJPF.jar")
z3_jar = os.path.join(workspace, "jpf-symbc", "lib", "com.microsoft.z3.jar")

out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "results-scaled-eval"))
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

strategies = {
    "BFS": "gov.nasa.jpf.search.heuristic.BFSHeuristic",
    "DFS": "gov.nasa.jpf.search.heuristic.DFSHeuristic",
    "SCI": "gov.nasa.jpf.search.heuristic.SCISearch"
}

# Define the runs to perform
# (Workload, JPF file path, state budget limit, description)
runs_config = [
    # Factories scaling
    ("Factories-D8", os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "real-factories-depth8-realstyle.jpf"), 1000, "Depth 8 (1,000 states)"),
    ("Factories-D10", os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "real-factories-depth10-realstyle.jpf"), 5000, "Depth 10 (5,000 states)"),
    ("Factories-D12", os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "real-factories-depth12-realstyle.jpf"), 10000, "Depth 12 (10,000 states)"),
    
    # Guava scaling
    ("Guava-I6", os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "real-guava-input6.jpf"), None, "Input Size = 6"),
    ("Guava-I9", os.path.join(workspace, "jpf-symbc", "src", "examples", "research", "real-guava-input9.jpf"), None, "Input Size = 9")
]

results = {}

# We will run 1 warmup, 3 measurements to save time while ensuring median accuracy.
# With 3 measurements, we get robust medians without taking all day.
repetitions = 4 # 0 is warmup, 1,2,3 are measured

for name, jpf_path, budget, desc in runs_config:
    results[name] = {}
    print(f"\n==========================================")
    print(f"Running scaled workload: {name} ({desc})")
    print(f"==========================================")
    
    for strat_label, strat_class in strategies.items():
        print(f"\n  >>> Strategy {strat_label}...")
        csv_out = os.path.join(out_dir, f"{name}_{strat_label}.csv")
        if os.path.exists(csv_out):
            try:
                os.remove(csv_out)
            except Exception:
                pass
        
        run_times = []
        engine_times = []
        solver_times = []
        states_list = []
        paths_list = []
        coverage_list = []
        
        for rep in range(repetitions):
            run_id = f"{strat_label}-rep-{rep}"
            print(f"    Repetition {rep} (warmup={rep==0})...")
            
            # Setup JPF command
            cmd = [
                java_exe,
                "-Xmx8g", # Give JPF plenty of heap
                "-cp", f"{run_jpf_jar};{z3_jar}",
                "gov.nasa.jpf.tool.RunJPF",
                f"+research.output={csv_out}",
                "+research.append=true",
                f"+research.run_id={run_id}",
                f"+search.class={strat_class}",
                f"+research.search_label={strat_label}",
                f"+research.benchmark={name}"
            ]
            
            # Add listener and budget config
            listeners = "gov.nasa.jpf.symbc.ResearchDataListener"
            if budget is not None:
                listeners = "gov.nasa.jpf.listener.BudgetChecker," + listeners
                cmd.extend([
                    f"+listener={listeners}",
                    f"+budget.max_state={budget}"
                ])
            else:
                cmd.extend([
                    f"+listener={listeners}"
                ])
                
            cmd.append(jpf_path)
            
            t0 = time.time()
            try:
                # 10 minutes timeout per run
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
                elapsed_wall = time.time() - t0
                print(f"      Finished in {elapsed_wall:.2f} seconds.")
                
                # Check exit code
                if res.returncode != 0:
                    print(f"      WARNING: JPF exited with code {res.returncode}")
                    # print(res.stderr.decode(errors='ignore'))
                
                if rep > 0: # skip warmup
                    summary_csv = csv_out.replace(".csv", "_summary.csv")
                    if os.path.exists(summary_csv):
                        with open(summary_csv, "r") as f:
                            reader = csv.DictReader(f)
                            row = None
                            for r in reader:
                                if r.get("run_id") == run_id:
                                    row = r
                            if row:
                                run_times.append(float(row['total_elapsed_ns']) / 1e9) # in seconds
                                engine_times.append(float(row['engine_time_ns']) / 1e9) # in seconds
                                solver_times.append(float(row['total_solver_time_ns']) / 1e9) # in seconds
                                paths_list.append(int(row['completed_paths']))
                                states_list.append(int(row['new_states']))
                                coverage_list.append(float(row['branches_covered']))
                            else:
                                print("      ERROR: Could not find run_id in summary CSV.")
                    else:
                        print("      ERROR: Summary CSV does not exist.")
            except subprocess.TimeoutExpired:
                print(f"      TIMEOUT! Exceeded 600 seconds.")
                if rep > 0:
                    run_times.append(600.0)
                    engine_times.append(600.0)
                    solver_times.append(0.0)
                    states_list.append(0)
                    paths_list.append(0)
                    coverage_list.append(0.0)
            except Exception as e:
                print(f"      ERROR running process: {e}")
                
        if run_times:
            results[name][strat_label] = {
                "elapsed": statistics.median(run_times),
                "engine": statistics.median(engine_times),
                "solver": statistics.median(solver_times),
                "paths": statistics.median(paths_list),
                "states": statistics.median(states_list),
                "coverage": statistics.median(coverage_list)
            }
            print(f"    >>> Median Wall-Clock: {results[name][strat_label]['elapsed']:.2f} s, States: {results[name][strat_label]['states']}, Paths: {results[name][strat_label]['paths']}, Coverage: {results[name][strat_label]['coverage']}%")
        else:
            print(f"    >>> Failed to collect data for {strat_label}")

# Print summary table
print("\n=== FINAL SCALED EVALUATION SUMMARY ===")
print("| Workload | Strategy | Elapsed Time (s) | Engine Time (s) | Solver Time (s) | Explored States | Completed Paths | Coverage (%) |")
print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
for name in results:
    for strat in ["BFS", "DFS", "SCI"]:
        if strat in results[name]:
            data = results[name][strat]
            print(f"| {name} | {strat} | {data['elapsed']:.3f} | {data['engine']:.3f} | {data['solver']:.3f} | {data['states']:.0f} | {data['paths']:.0f} | {data['coverage']:.1f} |")
