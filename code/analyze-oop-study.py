import csv
import math
import os
import statistics
import sys


WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RESULTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORKSPACE, "results-oop")
SUMMARY_PATH = os.path.join(RESULTS_DIR, "summary.csv")
PAIRWISE_PATH = os.path.join(RESULTS_DIR, "pairwise.csv")
COMBINED_PATH = os.path.join(RESULTS_DIR, "all_paths.csv")
RUN_SUMMARY_COMBINED_PATH = os.path.join(RESULTS_DIR, "all_run_summaries.csv")
RUN_SUMMARY_AGG_PATH = os.path.join(RESULTS_DIR, "run_summary_aggregate.csv")
RUN_PAIRWISE_PATH = os.path.join(RESULTS_DIR, "run_pairwise.csv")


PAIRWISE_COMPARISONS = [
    ("oop-exceptionTryCatch", "oop-guardedExceptionControl", "exception_vs_guarded"),
    ("oop-exceptionTryCatchRepeat4", "oop-guardedExceptionControlRepeat4", "exception_repeat4_vs_guarded_repeat4"),
    ("oop-exceptionLinearTryCatch", "oop-guardedExceptionLinearControl", "exception_linear_vs_guarded_linear"),
    ("oop-exceptionLinearTryCatchRepeat4", "oop-guardedExceptionLinearRepeat4", "exception_linear_repeat4_vs_guarded_linear_repeat4"),
    ("real-exceptions1-realstyle", "real-exceptions1-branchcontrol", "real_exceptions1_vs_branchcontrol"),
    ("real-exceptions2-realstyle", "real-exceptions2-branchcontrol", "real_exceptions2_vs_branchcontrol"),
    ("real-exceptions3-realstyle", "real-exceptions3-branchcontrol", "real_exceptions3_vs_branchcontrol"),
    ("real-exceptions4-realstyle", "real-exceptions4-branchcontrol", "real_exceptions4_vs_branchcontrol"),
    ("real-exceptions5-realstyle", "real-exceptions5-branchcontrol", "real_exceptions5_vs_branchcontrol"),
    ("real-exceptions6-realstyle", "real-exceptions6-branchcontrol", "real_exceptions6_vs_branchcontrol"),
    ("real-exceptions7-realstyle", "real-exceptions7-branchcontrol", "real_exceptions7_vs_branchcontrol"),
    ("real-exceptions8-realstyle", "real-exceptions8-branchcontrol", "real_exceptions8_vs_branchcontrol"),
    ("real-exceptions9-realstyle", "real-exceptions9-branchcontrol", "real_exceptions9_vs_branchcontrol"),
    ("real-exceptions10-realstyle", "real-exceptions10-branchcontrol", "real_exceptions10_vs_branchcontrol"),
    ("real-exceptions11-realstyle", "real-exceptions11-branchcontrol", "real_exceptions11_vs_branchcontrol"),
    ("real-exceptions12-realstyle", "real-exceptions12-branchcontrol", "real_exceptions12_vs_branchcontrol"),
    ("real-exceptions13-realstyle", "real-exceptions13-branchcontrol", "real_exceptions13_vs_branchcontrol"),
    ("real-exceptions14-realstyle", "real-exceptions14-branchcontrol", "real_exceptions14_vs_branchcontrol"),
    ("real-exceptions15-realstyle", "real-exceptions15-branchcontrol", "real_exceptions15_vs_branchcontrol"),
    ("real-exceptions16-realstyle", "real-exceptions16-branchcontrol", "real_exceptions16_vs_branchcontrol"),
    ("real-exceptions18-realstyle", "real-exceptions18-branchcontrol", "real_exceptions18_vs_branchcontrol"),
    ("real-factories-realstyle", "real-factories-branchcontrol", "real_factories_vs_branchcontrol"),
    ("real-factories-depth1-realstyle", "real-factories-depth1-branchcontrol", "real_factories_depth1_real_vs_control"),
    ("real-factories-depth2-realstyle", "real-factories-depth2-branchcontrol", "real_factories_depth2_real_vs_control"),
    ("real-factories-depth4-realstyle", "real-factories-depth4-branchcontrol", "real_factories_depth4_real_vs_control"),
    ("real-factories-depth6-realstyle", "real-factories-depth6-branchcontrol", "real_factories_depth6_real_vs_control"),
    ("real-exception-depth1-realstyle", "real-exception-depth1-branchcontrol", "real_exception_depth1_real_vs_control"),
    ("real-exception-depth2-realstyle", "real-exception-depth2-branchcontrol", "real_exception_depth2_real_vs_control"),
    ("real-exception-depth4-realstyle", "real-exception-depth4-branchcontrol", "real_exception_depth4_real_vs_control"),
    ("real-exception-depth6-realstyle", "real-exception-depth6-branchcontrol", "real_exception_depth6_real_vs_control"),
    ("exception-depth1-realstyle", "exception-depth1-branchcontrol", "exception_depth1_real_vs_control"),
    ("exception-depth2-realstyle", "exception-depth2-branchcontrol", "exception_depth2_real_vs_control"),
    ("exception-depth4-realstyle", "exception-depth4-branchcontrol", "exception_depth4_real_vs_control"),
    ("exception-depth6-realstyle", "exception-depth6-branchcontrol", "exception_depth6_real_vs_control"),
    ("oop-polymorphicDispatch", "oop-directDispatchControl", "polymorphism_vs_direct"),
    ("oop-polymorphicDispatchRepeat4", "oop-directDispatchRepeat4", "polymorphism_repeat4_vs_direct_repeat4"),
    ("oop-loopControlKernel", "oop-baselineKernel", "loop_vs_baseline"),
]


def read_rows():
    rows = []
    run_summary_rows = []
    for name in sorted(os.listdir(RESULTS_DIR)):
        if not name.endswith(".csv"):
            continue
        if name in {"summary.csv", "pairwise.csv", "all_paths.csv", "all_run_summaries.csv", "run_summary_aggregate.csv", "run_pairwise.csv"}:
            continue
        path = os.path.join(RESULTS_DIR, name)
        with open(path, newline="", encoding="utf-8") as f:
            data = []
            for row in csv.DictReader(f):
                if None in row:
                    continue
                if any(value is None for value in row.values()):
                    continue
                data.append(row)
            if name.endswith("_summary.csv"):
                run_summary_rows.extend(
                    row for row in data if "warmup" not in row.get("run_id", "")
                )
            else:
                rows.extend(data)
    return rows, run_summary_rows


def median(values):
    return statistics.median(values) if values else math.nan


def mean(values):
    return statistics.mean(values) if values else math.nan


def stdev(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


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


def mann_whitney_u(sample_a, sample_b):
    n1 = len(sample_a)
    n2 = len(sample_b)
    all_values = sample_a + sample_b
    ranks = rankdata(all_values)
    r1 = sum(ranks[:n1])
    u1 = r1 - (n1 * (n1 + 1)) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)

    tie_counts = {}
    for value in all_values:
      tie_counts[value] = tie_counts.get(value, 0) + 1
    tie_sum = sum(t ** 3 - t for t in tie_counts.values() if t > 1)

    mean_u = n1 * n2 / 2.0
    denom = (n1 + n2) * (n1 + n2 - 1)
    if denom == 0:
      return u1, u2, u, 1.0

    variance_u = (n1 * n2 / 12.0) * ((n1 + n2 + 1) - tie_sum / denom)
    if variance_u <= 0:
      return u1, u2, u, 1.0

    z = (u - mean_u) / math.sqrt(variance_u)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return u1, u2, u, p


def cliffs_delta(sample_a, sample_b):
    gt = 0
    lt = 0
    for a in sample_a:
      for b in sample_b:
        if a > b:
          gt += 1
        elif a < b:
          lt += 1
    total = len(sample_a) * len(sample_b)
    if total == 0:
      return 0.0
    return (gt - lt) / total


def write_combined(rows):
    if not rows:
        return
    with open(COMBINED_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_run_summaries(rows):
    if not rows:
        return
    with open(RUN_SUMMARY_COMBINED_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_run_summaries(rows):
    if not rows:
        return {}
    grouped = {}
    for row in rows:
        grouped.setdefault(row["benchmark"], []).append(row)

    out_rows = []
    for benchmark in sorted(grouped):
        items = grouped[benchmark]
        total_elapsed = [int(r["total_elapsed_ns"]) for r in items]
        total_solver = [int(r["total_solver_time_ns"]) for r in items]
        engine = [int(r["engine_time_ns"]) for r in items]
        new_states = [int(r["new_states"]) for r in items]
        state_adv = [int(r["state_advanced_events"]) for r in items]
        cgs = [int(r["choice_generators"]) for r in items]
        pc_cgs = [int(r["pc_choice_generators"]) for r in items]
        paths = [int(r["completed_paths"]) for r in items]

        out_rows.append({
            "benchmark": benchmark,
            "runs": len(items),
            "median_total_elapsed_ns": int(median(total_elapsed)),
            "median_total_solver_time_ns": int(median(total_solver)),
            "median_engine_time_ns": int(median(engine)),
            "median_completed_paths": int(median(paths)),
            "median_new_states": int(median(new_states)),
            "median_state_advanced_events": int(median(state_adv)),
            "median_choice_generators": int(median(cgs)),
            "median_pc_choice_generators": int(median(pc_cgs)),
        })

    with open(RUN_SUMMARY_AGG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    return grouped


def write_run_pairwise(grouped):
    rows = []
    for left, right, label in PAIRWISE_COMPARISONS:
        if left not in grouped or right not in grouped:
            continue

        left_elapsed = [int(r["total_elapsed_ns"]) for r in grouped[left]]
        right_elapsed = [int(r["total_elapsed_ns"]) for r in grouped[right]]
        left_solver = [int(r["total_solver_time_ns"]) for r in grouped[left]]
        right_solver = [int(r["total_solver_time_ns"]) for r in grouped[right]]
        left_engine = [int(r["engine_time_ns"]) for r in grouped[left]]
        right_engine = [int(r["engine_time_ns"]) for r in grouped[right]]

        _, _, u_elapsed, p_elapsed = mann_whitney_u(left_elapsed, right_elapsed)
        _, _, u_solver, p_solver = mann_whitney_u(left_solver, right_solver)
        _, _, u_engine, p_engine = mann_whitney_u(left_engine, right_engine)

        rows.append({
            "comparison": label,
            "left": left,
            "right": right,
            "left_runs": len(left_elapsed),
            "right_runs": len(right_elapsed),
            "median_total_elapsed_left_ns": int(median(left_elapsed)),
            "median_total_elapsed_right_ns": int(median(right_elapsed)),
            "elapsed_ratio_left_over_right": round(median(left_elapsed) / median(right_elapsed), 4),
            "elapsed_p_value_two_sided": "{:.6g}".format(p_elapsed),
            "elapsed_cliffs_delta": round(cliffs_delta(left_elapsed, right_elapsed), 4),
            "median_total_solver_left_ns": int(median(left_solver)),
            "median_total_solver_right_ns": int(median(right_solver)),
            "solver_ratio_left_over_right": round(median(left_solver) / median(right_solver), 4),
            "solver_p_value_two_sided": "{:.6g}".format(p_solver),
            "solver_cliffs_delta": round(cliffs_delta(left_solver, right_solver), 4),
            "median_engine_left_ns": int(median(left_engine)),
            "median_engine_right_ns": int(median(right_engine)),
            "engine_ratio_left_over_right": round(median(left_engine) / median(right_engine), 4),
            "engine_p_value_two_sided": "{:.6g}".format(p_engine),
            "engine_cliffs_delta": round(cliffs_delta(left_engine, right_engine), 4),
            "u_elapsed_min": round(u_elapsed, 2),
            "u_solver_min": round(u_solver, 2),
            "u_engine_min": round(u_engine, 2),
        })

    if rows:
        with open(RUN_PAIRWISE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def summarize(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["benchmark"], []).append(row)

    summary_rows = []
    for benchmark in sorted(grouped):
        items = grouped[benchmark]
        solver_times = [int(row["solver_time_ns"]) for row in items]
        constraint_counts = [int(row["constraint_count"]) for row in items]
        summary_rows.append({
            "benchmark": benchmark,
            "paths": len(items),
            "unique_runs": len({row["run_id"] for row in items}),
            "median_solver_time_ns": int(median(solver_times)),
            "mean_solver_time_ns": round(mean(solver_times), 2),
            "stdev_solver_time_ns": round(stdev(solver_times), 2),
            "min_solver_time_ns": min(solver_times),
            "max_solver_time_ns": max(solver_times),
            "median_constraint_count": int(median(constraint_counts)),
            "mean_constraint_count": round(mean(constraint_counts), 2),
        })

    with open(SUMMARY_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    return grouped


def write_pairwise(grouped):
    rows = []
    for left, right, label in PAIRWISE_COMPARISONS:
        if left not in grouped or right not in grouped:
            continue
        left_vals = [int(row["solver_time_ns"]) for row in grouped[left]]
        right_vals = [int(row["solver_time_ns"]) for row in grouped[right]]
        u1, u2, u, p = mann_whitney_u(left_vals, right_vals)
        left_median = median(left_vals)
        right_median = median(right_vals)
        rows.append({
            "comparison": label,
            "left": left,
            "right": right,
            "left_n": len(left_vals),
            "right_n": len(right_vals),
            "left_median_ns": int(left_median),
            "right_median_ns": int(right_median),
            "median_ratio_left_over_right": round(left_median / right_median, 4),
            "u1": round(u1, 2),
            "u2": round(u2, 2),
            "u_min": round(u, 2),
            "p_value_two_sided": "{:.6g}".format(p),
            "cliffs_delta": round(cliffs_delta(left_vals, right_vals), 4),
        })

    if rows:
        with open(PAIRWISE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    rows, run_summary_rows = read_rows()
    write_combined(rows)
    write_run_summaries(run_summary_rows)
    if rows:
        grouped = summarize(rows)
        write_pairwise(grouped)
    if run_summary_rows:
        run_grouped = aggregate_run_summaries(run_summary_rows)
        write_run_pairwise(run_grouped)


if __name__ == "__main__":
    main()
