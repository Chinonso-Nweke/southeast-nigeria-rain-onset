"""The data auditor: compares the rainfall sources and says, in plain words, how far they can be trusted.

assess() turns the numbers from compare_sources.compare() into an agreement level and a list of flags.
The thresholds are my own rule of thumb, not an official standard. They are written down here so
anyone can change them.
Run it by hand:  python audit.py     (writes audit_report.md and audit_report.json)
"""
import json
import pandas as pd
from compare_sources import compare, load
from download_all import LOCATIONS

# Thresholds for the agreement level
WEAK_YEARLY_R = 0.5         # yearly totals correlate less than this: weak
STRONG_YEARLY_R = 0.8       # ...and at least this for strong
WEAK_SHIFT_GAP = 10         # later-start estimates differ by more than this many days: weak
STRONG_SHIFT_GAP = 5
WEAK_DROP_GAP = 8           # yearly-rain change differs by more than this many percentage points: weak
STRONG_DROP_GAP = 4
STRONG_DAILY_R = 0.5
BIG_MEAN_DIFF = 0.15        # average yearly rain differs by more than 15%: flagged


def assess(c, other_label="ERA5"):
    n, o = c["nasa"], c["other"]
    yr, dr = c["yearly_total_correlation"], c["daily_correlation"]
    shift_gap = abs(n["shift_days"] - o["shift_days"])
    drop_gap = abs(n["annual_change_pct"] - o["annual_change_pct"])
    mean_n, mean_o = c["mean_annual_mm"]["nasa"], c["mean_annual_mm"]["other"]
    mean_diff = abs(mean_n - mean_o) / max(mean_n, mean_o)

    flags = []
    if yr < WEAK_YEARLY_R:
        flags.append(f"Yearly totals barely agree (correlation {yr:.2f}): the two sources disagree on which years were wet or dry.")
    if shift_gap > STRONG_SHIFT_GAP:
        flags.append(f"The later start differs: {n['shift_days']:+d} days in NASA POWER, {o['shift_days']:+d} days in {other_label}.")
    if drop_gap > STRONG_DROP_GAP:
        flags.append(f"The change in yearly rain differs: {n['annual_change_pct']:+.0f}% in NASA POWER, {o['annual_change_pct']:+.0f}% in {other_label}.")
    if mean_diff > BIG_MEAN_DIFF:
        flags.append(f"Average yearly rain differs by {mean_diff * 100:.0f}% ({mean_n} mm in NASA POWER, {mean_o} mm in {other_label}).")
    sig_n, sig_o = n["step_p"] < 0.05, o["step_p"] < 0.05
    if sig_n != sig_o:
        who, other = ("NASA POWER", other_label) if sig_n else (other_label, "NASA POWER")
        flags.append(f"Only {who} shows a statistically significant jump in the start date; {other} does not.")

    if yr < WEAK_YEARLY_R or shift_gap > WEAK_SHIFT_GAP or drop_gap > WEAK_DROP_GAP:
        level = "weak"
    elif yr >= STRONG_YEARLY_R and shift_gap <= STRONG_SHIFT_GAP and drop_gap <= STRONG_DROP_GAP and dr >= STRONG_DAILY_R:
        level = "strong"
    else:
        level = "moderate"
    return {"level": level, "flags": flags,
            "numbers": {"daily_r": dr, "five_day_r": c["five_day_correlation"], "yearly_r": yr,
                        "start_r": c["onset_year_correlation"], "start_diff_days": c["onset_mean_abs_diff_days"],
                        "shift": {"nasa": n["shift_days"], "other": o["shift_days"]},
                        "annual_change_pct": {"nasa": n["annual_change_pct"], "other": o["annual_change_pct"]},
                        "mean_mm": {"nasa": mean_n, "other": mean_o}}}


def summary_text(results, other_label="ERA5"):
    levels = [r["level"] for r in results.values()]
    weak, strong = levels.count("weak"), levels.count("strong")
    n = len(levels)
    if weak == n:
        head = f"NASA POWER and {other_label} agree weakly at all {n} places."
    elif weak:
        head = f"NASA POWER and {other_label} agree weakly at {weak} of {n} places."
    elif strong == n:
        head = f"NASA POWER and {other_label} agree well at all {n} places."
    else:
        head = f"NASA POWER and {other_label} agree moderately or well at all {n} places."
    advice = ("Treat the planting-date numbers as indicative and read the later-start finding as unconfirmed."
              if weak else "The sources broadly support each other, but neither is a rain gauge measurement.")
    return head + " " + advice


def main():
    results = {}
    for name in LOCATIONS:
        try:
            c = compare(load(f"rain_{name}.csv"), load(f"era5_{name}.csv"))
        except FileNotFoundError as e:
            print(f"{name}: missing {e.filename}")
            continue
        results[name] = assess(c)
    if not results:
        raise SystemExit("Nothing to audit. Download both sources first.")
    text = summary_text(results)
    lines = [f"# Data trust report", "", text, ""]
    for name, r in results.items():
        lines += [f"## {name.capitalize()}: {r['level']} agreement", ""] + [f"- {f}" for f in r["flags"]] + [""]
        print(f"{name:<10}{r['level']:<10}{len(r['flags'])} flag(s)")
    print("\n" + text)
    open("audit_report.md", "w").write("\n".join(lines))
    json.dump({"summary": text, "places": results}, open("audit_report.json", "w"), indent=1)
    print("Saved audit_report.md and audit_report.json")


if __name__ == "__main__":
    main()
