import csv
import os
import re
from pathlib import Path


WORKSPACE = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
SV_BENCH_ROOT = WORKSPACE / "benchmarks" / "sv-benchmarks" / "java"
OUT_DIR = WORKSPACE / "benchmark-analysis"
OUT_DIR.mkdir(exist_ok=True)

SUMMARY_CSV = OUT_DIR / "sv_java_feature_scan.csv"
EXCEPTION_CSV = OUT_DIR / "sv_java_exception_candidates.csv"
DISPATCH_CSV = OUT_DIR / "sv_java_dispatch_candidates.csv"


JAVA_FILE_RE = re.compile(r".*\.java$")
EXCEPTION_PATTERNS = [
    re.compile(r"\btry\b"),
    re.compile(r"\bcatch\s*\("),
    re.compile(r"\bthrow\b"),
    re.compile(r"\bthrows\b"),
]
DISPATCH_PATTERNS = [
    re.compile(r"\binterface\b"),
    re.compile(r"\bimplements\b"),
    re.compile(r"\bextends\b"),
    re.compile(r"\bnew\s+[A-Z]\w*\s*\("),
]
VIRTUAL_CALL_RE = re.compile(r"\b\w+\.\w+\s*\(")


def iter_java_files(root: Path):
    for path in root.rglob("*.java"):
        if path.is_file():
            yield path


def count_matches(text, patterns):
    total = 0
    for pattern in patterns:
        total += len(pattern.findall(text))
    return total


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    exception_hits = count_matches(text, EXCEPTION_PATTERNS)
    dispatch_hits = count_matches(text, DISPATCH_PATTERNS)
    virtual_calls = len(VIRTUAL_CALL_RE.findall(text))
    line_count = text.count("\n") + 1

    rel = path.relative_to(SV_BENCH_ROOT)
    family = rel.parts[0] if rel.parts else ""

    return {
        "family": family,
        "relative_path": str(rel).replace("\\", "/"),
        "lines": line_count,
        "exception_hits": exception_hits,
        "dispatch_hits": dispatch_hits,
        "virtual_call_like_hits": virtual_calls,
    }


def write_csv(path: Path, rows):
    rows = list(rows)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = []
    for java_file in iter_java_files(SV_BENCH_ROOT):
        item = scan_file(java_file)
        if item:
            rows.append(item)

    rows.sort(key=lambda r: (r["family"], r["relative_path"]))
    write_csv(SUMMARY_CSV, rows)

    exception_rows = [
        r for r in rows
        if r["exception_hits"] > 0 and r["lines"] <= 400
    ]
    exception_rows.sort(
        key=lambda r: (-r["exception_hits"], r["lines"], r["relative_path"])
    )
    write_csv(EXCEPTION_CSV, exception_rows[:100])

    dispatch_rows = [
        r for r in rows
        if r["dispatch_hits"] > 0 and r["lines"] <= 400
    ]
    dispatch_rows.sort(
        key=lambda r: (-r["dispatch_hits"], r["lines"], r["relative_path"])
    )
    write_csv(DISPATCH_CSV, dispatch_rows[:100])


if __name__ == "__main__":
    main()
