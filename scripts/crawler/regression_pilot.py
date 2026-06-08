"""
Pilot OLS regression on log-transformed engagement outcomes.
Uses bilibili_health_clean_clip.csv.
Outputs summary tables to output/regression_pilot.txt
"""
import csv
import math
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

SRC = "output/bilibili_health_clean_clip.csv"
OUT = "output/regression_pilot.txt"

# ── load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False)
print(f"Loaded {len(df)} rows, {len(df.columns)} cols")

# ── numeric coercion ──────────────────────────────────────────────────────────
num_cols = ["play","like","coin","favorites","share","danmaku","review",
            "follower","duration","video_age_days","clip_sim"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["is_official"] = df["is_official"].astype(str).str.upper().eq("TRUE").astype(int)

# ── derived variables ─────────────────────────────────────────────────────────
# log(x+1) transforms for all count outcomes
for c in ["play","like","coin","favorites","share","danmaku","review","follower"]:
    df[f"log_{c}"] = np.log1p(df[c])

# log duration, log age
df["log_duration"]    = np.log1p(df["duration"])
df["log_video_age"]   = np.log1p(df["video_age_days"])
df["log_follower"]    = np.log1p(df["follower"])

# clip_sim already 0-1 continuous, no transform needed
# standardise for easier beta comparison
df["clip_sim_z"] = (df["clip_sim"] - df["clip_sim"].mean()) / df["clip_sim"].std()
df["log_follower_z"] = (df["log_follower"] - df["log_follower"].mean()) / df["log_follower"].std()
df["log_duration_z"] = (df["log_duration"] - df["log_duration"].mean()) / df["log_duration"].std()
df["log_age_z"]      = (df["log_video_age"] - df["log_video_age"].mean()) / df["log_video_age"].std()

# ── formula ───────────────────────────────────────────────────────────────────
# Main predictor: clip_sim_z (图文代表性)
# Controls: is_official, log_follower_z, log_duration_z, log_age_z
controls = "is_official + log_follower_z + log_duration_z + log_age_z"
pred     = "clip_sim_z"

outcomes = {
    "log_play":      "播放量 (log)",
    "log_like":      "点赞 (log)",
    "log_coin":      "投币 (log)   [高成本]",
    "log_favorites": "收藏 (log)   [高成本]",
    "log_share":     "转发 (log)   [高成本]",
    "log_danmaku":   "弹幕 (log)   [低成本]",
    "log_review":    "评论 (log)   [低成本]",
}

lines = []
lines.append("=" * 70)
lines.append("PILOT OLS REGRESSION: clip_sim → engagement outcomes")
lines.append(f"N = {len(df)}")
lines.append("Predictor: clip_sim_z (standardised CLIP cosine similarity)")
lines.append("Controls: is_official, log_follower_z, log_duration_z, log_age_z")
lines.append("=" * 70)

summary_rows = []

for dv, label in outcomes.items():
    formula = f"{dv} ~ {pred} + {controls}"
    res = smf.ols(formula, data=df).fit(cov_type="HC3")
    b  = res.params[pred]
    se = res.bse[pred]
    t  = res.tvalues[pred]
    p  = res.pvalues[pred]
    r2 = res.rsquared

    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    lines.append(f"\n{label}")
    lines.append(f"  β={b:+.4f}  SE={se:.4f}  t={t:+.2f}  p={p:.4f} {stars}  R²={r2:.4f}")

    summary_rows.append(dict(outcome=label, beta=b, se=se, t=t, p=p, stars=stars, r2=r2))

# ── correlation matrix quick look ─────────────────────────────────────────────
lines.append("\n" + "=" * 70)
lines.append("CORRELATIONS (Pearson) between clip_sim and engagement (log)")
lines.append("=" * 70)
for dv in outcomes:
    r = df["clip_sim"].corr(df[dv])
    lines.append(f"  clip_sim × {dv:<18}  r = {r:+.4f}")

# ── summary table ─────────────────────────────────────────────────────────────
lines.append("\n" + "=" * 70)
lines.append("SUMMARY TABLE")
lines.append(f"{'结果变量':<28} {'β':>8} {'SE':>8} {'t':>8} {'p':>8} {'sig':>5} {'R²':>7}")
lines.append("-" * 70)
for row in summary_rows:
    lines.append(
        f"{row['outcome']:<28} {row['beta']:>8.4f} {row['se']:>8.4f} "
        f"{row['t']:>8.2f} {row['p']:>8.4f} {row['stars']:>5} {row['r2']:>7.4f}"
    )

text = "\n".join(lines)
print(text)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print(f"\n→ Saved to {OUT}")
