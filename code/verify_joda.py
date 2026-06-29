import csv, statistics, glob, os

base = os.path.join(os.path.dirname(__file__), "..", "results", "results-mini-eval")

for strat in ['BFS', 'DFS', 'SCI']:
    files = glob.glob(os.path.join(base, f'Joda-Time_{strat}_summary.csv'))
    el, eng, sol = [], [], []
    for f in files:
        with open(f) as cf:
            for row in csv.DictReader(cf):
                el.append(float(row['total_elapsed_ns'])/1e9)
                eng.append(float(row['engine_time_ns'])/1e9)
                sol.append(float(row['total_solver_time_ns'])/1e9)
    if el:
        print(f'{strat}: elapsed={statistics.median(el):.3f}s  engine={statistics.median(eng):.3f}s  solver={statistics.median(sol):.3f}s')
    else:
        print(f'{strat}: NO FILES FOUND in {base}')
