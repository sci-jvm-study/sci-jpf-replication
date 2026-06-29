import glob, csv, os

base = os.path.join(os.path.dirname(__file__), "..", "results", "results-robust-campaign")
EXCLUDE = ['configresolver', 'expressionevaluator', 'jsonparser']

count = 0
for f in glob.glob(os.path.join(base, '*_limit_*_summary.csv')):
    name = os.path.basename(f).split('_limit_')[0]
    for s in ['_SCI', '_BFS', '_DFS', '_Random', '_CoverageFrequency']:
        if name.endswith(s):
            name = name[:-len(s)]
            break
    if any(x in name for x in EXCLUDE):
        continue
    with open(f) as cf:
        count += sum(1 for _ in csv.DictReader(cf))

print(f'Total rows: {count}')
print(f'Expected: 420')
print(f'Match: {count == 420}')
