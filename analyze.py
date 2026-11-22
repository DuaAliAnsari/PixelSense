"""Phase 3 analysis. Run after data collection:  python analyze.py
Reads study_data/*.csv (or the CSVs you downloaded from the study finish screen) and prints the numbers the paper needs, in RQ order.
scipy is optional: pip install scipy  (for paired tests)."""
from pathlib import Path
import sys
import pandas as pd

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "study_data"
try:
    from scipy import stats
except ImportError:
    stats = None

tasks = pd.read_csv(D / "tasks.csv")
tasks["gave_up"] = (tasks["outcome"] == "gave up").astype(int)
tasks["success"] = tasks["success"].map({"yes": 1, "no": 0}).fillna(tasks["success"]).astype(float)   # the app logs yes / no
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

print("\n=== Final survey (15 questions, answered once after both versions) ===")
if (D / "final.csv").exists():
    f = pd.read_csv(D / "final.csv")
    import study as _ST
    print(f"Participants with survey data: {f['participant'].nunique()}")
    for n, q in enumerate(_ST.FINAL_FORM, 1):
        if q["key"] not in f.columns:
            continue
        col = f[q["key"]].dropna().astype(str)
        print(f"\n{n}. {q['text']}")
        if q["kind"] == "multi":
            print(col.str.split(" \\| ").explode().value_counts().to_string())       # up to two answers per person
        elif q.get("ordered"):
            pos = col.map({o: i + 1 for i, o in enumerate(q["options"])})
            top2 = (pos >= len(q["options"]) - 1).mean() * 100
            print(col.value_counts().reindex(q["options"]).fillna(0).astype(int).to_string())
            print(f"mean {pos.mean():.2f} of {len(q['options'])}, top two answers: {top2:.0f}%")
        else:
            print(col.value_counts().to_string())
        fu = q.get("follow")
        if fu and fu["key"] in f.columns:
            print(f"  {fu['text']}\n" + f[fu["key"]].value_counts().to_string())
        if q.get("other_key") and q["other_key"] in f.columns:
            texts = f[q["other_key"]].dropna().astype(str)
            texts = texts[texts.str.strip() != ""]
            if len(texts):
                print("  Free text (code these thematically):\n   - " + "\n   - ".join(texts))
    if "freq" in f.columns:
        likely = f["freq"].isin(["Daily", "Weekly", "Monthly"]).mean() * 100
        print(f"\nH4: {likely:.0f}% would use PixelSense at least monthly (Daily, Weekly or Monthly).")
else:
    print("No final.csv yet.")
print("\nFor the Gallery vs PixelSense comparison use the task data above (success, time, errors, SEQ) and question 12.")
