"""
Negative Binomial regression for count outcomes.
Zero-Inflated NB for high-zero outcomes (coin, danmaku, share).
Outputs: output/regression_nb.txt
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP
from statsmodels.discrete.discrete_model import NegativeBinomial

SRC = "output/bilibili_health_clean_clip.csv"
OUT = "output/regression_nb.txt"

# ── load & prep ───────────────────────────────────────────────────────────────
df = pd.read_csv(SRC, encoding="utf-8-sig", low_memory=False)

num_cols = ["play","like","coin","favorites","share","danmaku","review",
            "follower","duration","video_age_days","clip_sim"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["is_official"] = df["is_official"].astype(str).str.upper().eq("TRUE").astype(int)

# log-transform continuous predictors
df["log_follower"] = np.log1p(df["follower"])
df["log_duration"] = np.log1p(df["duration"])
df["log_age"]      = np.log1p(df["video_age_days"])
df["log_play"]     = np.log1p(df["play"])  # offset for rate models

# standardise predictors
for col, src in [("clip_sim_z","clip_sim"),("log_follower_z","log_follower"),
                 ("log_duration_z","log_duration"),("log_age_z","log_age")]:
    df[col] = (df[src] - df[src].mean()) / df[src].std()

# drop rows with missing predictors
pred_cols = ["clip_sim_z","is_official","log_follower_z","log_duration_z","log_age_z"]
df = df.dropna(subset=pred_cols)
print(f"N after dropna: {len(df)}")

X = sm.add_constant(df[pred_cols])

# zero rates
print("\nZero rates:")
for c in ["like","coin","favorites","share","danmaku","review"]:
    zr = (df[c]==0).mean()
    print(f"  {c:<12} {zr:.1%}")

lines = []
lines.append("=" * 72)
lines.append("NEGATIVE BINOMIAL REGRESSION: clip_sim → engagement count outcomes")
lines.append(f"N = {len(df)}")
lines.append("Predictor: clip_sim_z  |  Controls: is_official, log_follower_z, log_duration_z, log_age_z")
lines.append("=" * 72)

# ── outcomes config ───────────────────────────────────────────────────────────
# (column, label, use_zinb)  — ZINB for zero > 20%
outcomes = [
    ("like",      "点赞       [低成本]", False),
    ("danmaku",   "弹幕       [低成本]", True),
    ("review",    "评论       [低成本]", False),
    ("favorites", "收藏       [高成本]", False),
    ("coin",      "投币       [高成本]", True),
    ("share",     "转发       [高成本]", True),
]

summary_rows = []

for col, label, use_zinb in outcomes:
    y = df[col].astype(int)
    try:
        if use_zinb:
            model = ZeroInflatedNegativeBinomialP(y, X, exog_infl=X, p=2)
            res = model.fit(method="bfgs", maxiter=300, disp=False)
        else:
            model = NegativeBinomial(y, X)
            res = model.fit(method="bfgs", maxiter=300, disp=False)

        b  = res.params["clip_sim_z"]
        se = res.bse["clip_sim_z"]
        z  = res.tvalues["clip_sim_z"]
        p  = res.pvalues["clip_sim_z"]
        irr = np.exp(b)  # incidence rate ratio
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        model_type = "ZINB" if use_zinb else "NB"

        line = (f"\n{label}  [{model_type}]")
        line2 = (f"  β={b:+.4f}  IRR={irr:.4f}  SE={se:.4f}  z={z:+.2f}  p={p:.4f} {stars}")
        lines.append(line)
        lines.append(line2)
        summary_rows.append(dict(outcome=label, model=model_type, beta=b, irr=irr,
                                 se=se, z=z, p=p, stars=stars))
        print(f"OK  {label}: β={b:+.4f} IRR={irr:.4f} {stars}")

    except Exception as e:
        lines.append(f"\n{label}: FAILED — {e}")
        print(f"FAIL {label}: {e}")

# ── summary table ─────────────────────────────────────────────────────────────
lines.append("\n" + "=" * 72)
lines.append("SUMMARY TABLE  (IRR = Incidence Rate Ratio; IRR<1 = negative effect)")
lines.append(f"{'结果变量':<26} {'模型':>5} {'β':>8} {'IRR':>7} {'SE':>8} {'z':>8} {'p':>8} {'sig':>5}")
lines.append("-" * 72)
for row in summary_rows:
    lines.append(
        f"{row['outcome']:<26} {row['model']:>5} {row['beta']:>8.4f} {row['irr']:>7.4f} "
        f"{row['se']:>8.4f} {row['z']:>8.2f} {row['p']:>8.4f} {row['stars']:>5}"
    )

lines.append("\nNote: β interpreted as log-IRR. IRR=0.90 means 10% fewer counts per +1SD clip_sim.")

text = "\n".join(lines)
print("\n" + text)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print(f"\n→ Saved to {OUT}")
