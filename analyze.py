"""Phase 3 analysis. Run after data collection:  python analyze.py
Reads study_data/*.csv (or the CSVs you downloaded from Settings) and prints the numbers the paper needs, in RQ order.
scipy is optional: pip install scipy  (for paired tests and the SUS benchmark test)."""
from pathlib import Path
import sys
import pandas as pd

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "study_data"
try:
    from scipy import stats
except ImportError:
    stats = None

tasks = pd.read_csv(D / "tasks.csv")
qs = pd.read_csv(D / "questionnaires.csv")
tasks["gave_up"] = (tasks["outcome"] == "gave_up").astype(int)
print(f"Participants with task data: {tasks['participant'].nunique()}\n")

print("=== Task performance by condition (F1 = RQ1, C1 = RQ2, S1 = RQ3, E1 = RQ4) ===")
g = tasks.groupby(["task_id", "rq", "condition"])
summary = g.agg(n=("participant", "nunique"), success_rate=("success", "mean"), gave_up_rate=("gave_up", "mean"),
                median_s=("seconds", "median"), mean_s=("seconds", "mean"), wrong=("wrong_actions", "mean"), opened=("photos_opened", "mean"), searches=("searches", "mean"),
                screens=("screens_visited", "mean"), undos=("undos", "mean"), seq=("seq", "mean")).round(2)
print(summary.to_string(), "\n")
# Time is compared on successful attempts only; gave-up times are censored and reported as a rate.
ok = tasks[tasks["success"] == 1]
print("=== Paired comparison (PixelSense vs Gallery), per task ===")
for tid, t in tasks.groupby("task_id"):
    if t["condition"].nunique() < 2:
        continue
    for metric, src in (("time on success (s)", ok[ok.task_id == tid]), ("SEQ (1-7)", t), ("success (0/1)", t)):
        col = {"time on success (s)": "seconds", "SEQ (1-7)": "seq", "success (0/1)": "success"}[metric]
        w = src.pivot_table(index="participant", columns="condition", values=col).dropna()
        if len(w) < 3:
            print(f"{tid} {metric}: fewer than 3 complete pairs, report descriptively"); continue
        a, b = w["PixelSense"], w["Gallery (baseline)"]
        line = f"{tid} {metric}: PixelSense {a.mean():.2f} vs Gallery {b.mean():.2f} (n={len(w)} pairs)"
        if stats is not None and (a - b).abs().sum() > 0:
            line += f", Wilcoxon p={stats.wilcoxon(a, b).pvalue:.3f}, r={(a - b).mean() / (a - b).std(ddof=1) if (a - b).std(ddof=1) else float('nan'):.2f} (dz)"
        print(line)

print("\n=== Questionnaires ===")
print(qs.groupby("condition")[["sus_score", "tlx_raw", "ueq_hedonic"]].agg(["mean", "std", "count"]).round(2).to_string())
ps = qs[qs.condition == "PixelSense"]["sus_score"].dropna()
if stats is not None and len(ps) > 2:
    r = stats.ttest_1samp(ps, 68)
    print(f"\nH3: SUS PixelSense mean {ps.mean():.1f} vs benchmark 68, one-sample t p={r.pvalue:.3f}")
tr = qs[qs.condition == "PixelSense"][[c for c in qs.columns if c.startswith("trust_")]]
if len(tr):
    print(f"H4: trust items mean (1-7, midpoint 4): {tr.mean().round(2).to_dict()}")
if (D / "final.csv").exists():
    f = pd.read_csv(D / "final.csv")
    print("\nPreferred version:\n", f["preferred"].value_counts().to_string())
    print("\nFree-text answers for thematic coding saved in final.csv (columns easiest, most_confusing).")
