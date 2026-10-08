#!/usr/bin/env python3
import argparse
import csv
import re
import statistics
from pathlib import Path

try:
    from scipy.stats import mannwhitneyu, spearmanr
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False


def parse_float(text):
    if text is None:
        return None
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", str(text))
    if not m:
        return None
    return float(m.group(1))


def parse_gap(value):
    try:
        return int(str(value).strip())
    except Exception:
        return None


def parse_group(root_cause_category):
    text = str(root_cause_category or "")
    if text.startswith("RC-A"):
        return "RC-A"
    if text.startswith("RC-B"):
        return "RC-B"
    return "Unknown"


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def safe_median(vals):
    return statistics.median(vals) if vals else None


def fmt_num(v, nd=3):
    if v is None:
        return "N/A"
    return f"{v:.{nd}f}"


def main():
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(description="RQ3 stats: gap summary, Spearman, and Mann-Whitney U.")
    parser.add_argument(
        "--input",
        default="rq3_data.csv",
        help="Input CSV path (relative paths are resolved from script directory)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (relative paths are resolved from script directory)",
    )
    parser.add_argument("--low-max-gap", type=int, default=1, help="Low-gap upper bound (inclusive)")
    parser.add_argument("--high-min-gap", type=int, default=2, help="High-gap lower bound (inclusive)")
    parser.add_argument("--print-only", action="store_true", help="Print results only, do not save CSV files")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    if not input_path.is_absolute():
        input_path = script_dir / input_path

    out_dir = Path(args.output_dir).expanduser()
    if not out_dir.is_absolute():
        out_dir = script_dir / out_dir

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {input_path}. "
            "Use --input to provide a valid file path."
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            gap = parse_gap(r.get("Stage Gap"))
            cost = parse_float(r.get("Fix Cost"))
            group = parse_group(r.get("Root Cause Category"))
            if gap is None or cost is None:
                continue
            rows.append({"gap": gap, "cost": cost, "group": group})

    # 1) Gap count + median fix cost
    gap_summary_rows = []
    for g in range(6):
        vals = [x["cost"] for x in rows if x["gap"] == g]
        med = safe_median(vals)
        gap_summary_rows.append([g, len(vals), "N/A" if med is None else f"{med:.1f}"])

    gap_summary_path = out_dir / "rq3_gap_count_median.csv"
    if not args.print_only:
        write_csv(gap_summary_path, ["Stage Gap", "Count", "Median Fix Cost (h)"], gap_summary_rows)

    # 2) Spearman correlation
    spearman_rows = []

    def add_spearman(label, subset):
        gaps = [x["gap"] for x in subset]
        costs = [x["cost"] for x in subset]
        n = len(subset)
        if HAS_SCIPY and n >= 2:
            rho, p = spearmanr(gaps, costs)
            spearman_rows.append([label, n, fmt_num(rho, 4), fmt_num(p, 4)])
        else:
            spearman_rows.append([label, n, "N/A", "N/A"])

    add_spearman("Overall", rows)
    add_spearman("RC-A", [x for x in rows if x["group"] == "RC-A"])
    add_spearman("RC-B", [x for x in rows if x["group"] == "RC-B"])

    spearman_path = out_dir / "rq3_spearman_results.csv"
    if not args.print_only:
        write_csv(spearman_path, ["Group", "N", "Spearman rho", "p-value"], spearman_rows)

    # 3) Mann-Whitney U test (Low vs High)
    mwu_rows = []

    def add_mwu(label, subset):
        low = [x["cost"] for x in subset if x["gap"] <= args.low_max_gap]
        high = [x["cost"] for x in subset if x["gap"] >= args.high_min_gap]

        low_med = safe_median(low)
        high_med = safe_median(high)
        mult = None
        if low_med is not None and low_med != 0 and high_med is not None:
            mult = high_med / low_med

        if HAS_SCIPY and low and high:
            u = mannwhitneyu(low, high, alternative="two-sided")
            u_stat = u.statistic
            p = u.pvalue
            mwu_rows.append([
                label,
                len(low),
                "N/A" if low_med is None else f"{low_med:.1f}",
                len(high),
                "N/A" if high_med is None else f"{high_med:.1f}",
                "N/A" if mult is None else f"{mult:.2f}x",
                f"{u_stat:.3f}",
                f"{p:.4f}",
            ])
        else:
            mwu_rows.append([
                label,
                len(low),
                "N/A" if low_med is None else f"{low_med:.1f}",
                len(high),
                "N/A" if high_med is None else f"{high_med:.1f}",
                "N/A" if mult is None else f"{mult:.2f}x",
                "N/A",
                "N/A",
            ])

    add_mwu("Overall", rows)
    add_mwu("RC-A", [x for x in rows if x["group"] == "RC-A"])
    add_mwu("RC-B", [x for x in rows if x["group"] == "RC-B"])

    mwu_path = out_dir / "rq3_mwu_results.csv"
    if not args.print_only:
        write_csv(
            mwu_path,
            ["Group", "Low N", "Low Median", "High N", "High Median", "Multiplier", "U statistic", "p-value"],
            mwu_rows,
        )

    print("Done")
    print(f"Input: {input_path.resolve()}")
    print(f"Valid rows: {len(rows)}")

    print("\n[1] Gap Count + Median Fix Cost")
    print("Stage Gap,Count,Median Fix Cost (h)")
    for r in gap_summary_rows:
        print(f"{r[0]},{r[1]},{r[2]}")

    print("\n[2] Spearman Correlation")
    print("Group,N,Spearman rho,p-value")
    for r in spearman_rows:
        print(",".join(str(x) for x in r))

    print("\n[3] Mann-Whitney U (Low vs High)")
    print("Group,Low N,Low Median,High N,High Median,Multiplier,U statistic,p-value")
    for r in mwu_rows:
        print(",".join(str(x) for x in r))

    if not args.print_only:
        print(f"\nGap summary saved: {gap_summary_path.resolve()}")
        print(f"Spearman saved: {spearman_path.resolve()}")
        print(f"MWU saved: {mwu_path.resolve()}")


if __name__ == "__main__":
    main()
