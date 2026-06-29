import csv
import glob
import os

results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "results-sci-budget"))
output_csv = os.path.join(results_dir, "budget_campaign_comparison.csv")

strategies = ["BFS", "DFS", "SCI"]
budgets = [5, 10, 20, 50, 100, 200, 500]

with open(output_csv, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow([
        "strategy", "budget_states", "median_elapsed_ms", "median_engine_ms", 
        "median_solver_ms", "median_paths", "median_states"
    ])
    
    print("                    BUDGET-CONSTRAINED EMPIRICAL CAMPAIGN SUMMARY                      ")
    print(f"{'Strategy':<10} | {'Budget (States)':<15} | {'Elapsed (ms)':<14} | {'Engine (ms)':<13} | {'Paths Completed':<17} | {'States Explored':<15}")
    print("-" * 92)
    
    for strategy in strategies:
        for budget in budgets:
            pattern = os.path.join(results_dir, f"{strategy}_limit_{budget}_*_summary.csv")
            matching_files = glob.glob(pattern)
            if not matching_files:
                continue
                
            summary_file = matching_files[0]
            
            elapsed_list = []
            engine_list = []
            solver_list = []
            paths_list = []
            states_list = []
            
            with open(summary_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    elapsed_list.append(float(row['total_elapsed_ns']))
                    engine_list.append(float(row['engine_time_ns']))
                    solver_list.append(float(row['total_solver_time_ns']))
                    paths_list.append(int(row['completed_paths']))
                    states_list.append(int(row['new_states']))
            
            # Compute medians
            elapsed_list.sort()
            engine_list.sort()
            solver_list.sort()
            paths_list.sort()
            states_list.sort()
            
            n = len(elapsed_list)
            mid = n // 2
            
            if n % 2 == 0:
                elapsed = (elapsed_list[mid - 1] + elapsed_list[mid]) / 2.0
                engine = (engine_list[mid - 1] + engine_list[mid]) / 2.0
                solver = (solver_list[mid - 1] + solver_list[mid]) / 2.0
                paths = (paths_list[mid - 1] + paths_list[mid]) / 2.0
                states = (states_list[mid - 1] + states_list[mid]) / 2.0
            else:
                elapsed = elapsed_list[mid]
                engine = engine_list[mid]
                solver = solver_list[mid]
                paths = paths_list[mid]
                states = states_list[mid]
            
            # Print row
            print(f"{strategy:<10} | {budget:<15} | {elapsed/1e6:12.2f} | {engine/1e6:11.2f} | {paths:17.0f} | {states:15.0f}")
            
            # Write to CSV
            writer.writerow([
                strategy, budget, f"{elapsed/1e6:.2f}", f"{engine/1e6:.2f}",
                f"{solver/1e6:.2f}", f"{paths:.0f}", f"{states:.0f}"
            ])

print(f"Aggregated budget campaign results compiled in {output_csv}.")
