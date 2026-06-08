"""Formal count models (NB / ZINB) for B站 health visual-clickbait study.

Upgrades the exploratory log1p-OLS pass to publication-grade specifications:
  - Negative Binomial (NB) for play, like, coin, favorites, share
  - Zero-Inflated NB (ZINB) for coin (18.6% zeros)
  - UP主 (mid) cluster-robust standard errors
  - Average Marginal Effects (AME) for focal visual dimensions
  - Representativeness x visual-clickbait interaction
  - Robustness battery: post-2022, drop top-5% creators, 科学科普 only,
    Poisson cross-check, binary-clickbait specification

Run with a Python environment that has pandas, numpy, and statsmodels:
    python scripts/regression_analysis/formal_nb_zinb_models.py
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PATH = ROOT / "data/private/bilibili_health_visual_clickbait_model_sample.csv"
OUT_DIR = ROOT / "results/tables"
SCRAPE_DATE = pd.Timestamp("2026-05-27", tz="Asia/Shanghai")

# Outcomes that are real, integer counts in the modeling sample.
OUTCOMES = [
    ("play", "播放量", "exposure"),
    ("like", "点赞", "low_cost"),
    ("coin", "投币", "high_cost"),
    ("favorites", "收藏", "high_cost"),
    ("share", "转发", "diffusion"),
]

# Eight standardized visual dimensions (the executed IVs).
DIMENSIONS = [
    ("emotion_z", "情感强度"),
    ("fear_z", "恐惧诉求"),
    ("text_z", "文字覆盖强度"),
    ("suspense_z", "视觉悬念"),
    ("info_gap_z", "信息缺口"),
    ("rep_z", "图文代表性"),
    ("auth_z", "权威线索"),
    ("clip_sim_z", "CLIP图文相似度"),
]

CONTROLS = "is_official_num + log_follower_z + log_duration_z + log_age_z + C(category)"


def stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "+"
    return ""


def load_sample() -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_PATH, encoding="utf-8-sig", low_memory=False)
    age = pd.to_numeric(df["video_age_days"], errors="coerce")
    df["pub_year"] = (SCRAPE_DATE - pd.to_timedelta(age, unit="D")).dt.year
    # Collapse sparse categories so C(category) fixed effects stay estimable.
    top = df["category"].value_counts()
    keep = set(top[top >= 30].index)
    df["category_c"] = np.where(df["category"].isin(keep), df["category"], "其他")
    for outcome, _, _ in OUTCOMES:
        df[outcome] = pd.to_numeric(df[outcome], errors="coerce").fillna(0).round().astype(int)
    return df


def _estimate_alpha(data: pd.DataFrame, outcome: str, rhs_c: str) -> float:
    """Cameron-Trivedi NB2 dispersion estimate via auxiliary OLS on a Poisson fit.

    Full-information NB MLE (smf.negativebinomial) leaves a non-invertible Hessian
    for the most extreme-tailed outcomes here (like, coin), so we estimate alpha
    separately and plug it into a GLM-NB with a stable IRLS Hessian."""
    pois = smf.glm(f"{outcome} ~ {rhs_c}", data=data, family=sm.families.Poisson()).fit()
    mu = pois.mu
    y = data[outcome].to_numpy()
    aux_y = ((y - mu) ** 2 - y) / mu
    alpha = float(sm.OLS(aux_y, mu).fit().params[0])
    return max(alpha, 1e-3)


def fit_nb(
    data: pd.DataFrame,
    outcome: str,
    rhs: str,
    cluster_col: str = "mid",
):
    """NB2 via GLM with pre-estimated dispersion and mid-cluster-robust SE.

    Returns a statsmodels GLMResults; ``.params``/``.bse``/``.pvalues`` are the
    NB count-model coefficients (log-link), so exp(beta) is an IRR."""
    rhs_c = rhs.replace("C(category)", "C(category_c)")
    alpha = _estimate_alpha(data, outcome, rhs_c)
    formula = f"{outcome} ~ {rhs_c}"
    return smf.glm(
        formula, data=data, family=sm.families.NegativeBinomial(alpha=alpha)
    ).fit(cov_type="cluster", cov_kwds={"groups": data[cluster_col]})


def fit_poisson(data: pd.DataFrame, outcome: str, rhs: str, cluster_col: str = "mid"):
    formula = f"{outcome} ~ {rhs.replace('C(category)', 'C(category_c)')}"
    return smf.poisson(formula, data=data).fit(
        maxiter=300, disp=0, cov_type="cluster", cov_kwds={"groups": data[cluster_col]}
    )


def fit_zinb(
    data: pd.DataFrame,
    outcome: str,
    rhs: str,
    inflate_rhs: str = "log_follower_z + log_age_z",
):
    """Zero-Inflated NB. Cluster-robust SE not natively supported here;
    report model-based SE and note clustering as a limitation for ZINB.

    The raw counts overflow the NB exp-link at default starting values, so we
    seed the count part with a plain NB fit and use bfgs, which yields an
    invertible Hessian (usable standard errors)."""
    y = data[outcome].to_numpy()
    X = sm.add_constant(_design(data, rhs)).astype(float)
    Z = sm.add_constant(_design(data, inflate_rhs)).astype(float)

    # Seed: count part from a plain NB, inflate part at zeros.
    nb_seed = sm.NegativeBinomial(y, X).fit(method="lbfgs", maxiter=300, disp=0)
    nb_p = np.asarray(nb_seed.params, dtype=float)  # [betas..., alpha]
    start = np.concatenate([
        np.zeros(Z.shape[1]),  # inflate logit params
        nb_p,                  # count betas + alpha
    ])
    model = ZeroInflatedNegativeBinomialP(y, X, exog_infl=Z, inflation="logit")
    res = model.fit(start_params=start, method="bfgs", maxiter=1000, disp=0)
    if np.any(np.isnan(np.asarray(res.bse, dtype=float))):
        # bfgs Hessian non-invertible; retry with nm then a fresh bfgs pass.
        try:
            res2 = model.fit(start_params=res.params, method="nm",
                             maxiter=5000, disp=0)
            res2 = model.fit(start_params=res2.params, method="bfgs",
                             maxiter=1000, disp=0)
            if not np.any(np.isnan(np.asarray(res2.bse, dtype=float))):
                res = res2
        except np.linalg.LinAlgError:
            pass  # keep bfgs point estimates; SE flagged as unavailable downstream
    return res


def _design(data: pd.DataFrame, rhs: str) -> pd.DataFrame:
    """Build a numeric design matrix from an additive RHS string, expanding
    C(category_c) into dummies."""
    parts = [p.strip() for p in rhs.replace("C(category)", "C(category_c)").split("+")]
    cols = {}
    for p in parts:
        if p.startswith("C("):
            cat = p[2:-1]
            dummies = pd.get_dummies(data[cat], prefix=cat, drop_first=True).astype(float)
            for c in dummies.columns:
                cols[c] = dummies[c].to_numpy()
        else:
            cols[p] = pd.to_numeric(data[p], errors="coerce").to_numpy()
    return pd.DataFrame(cols, index=data.index)


def focal_row(result, var: str, outcome: str, label: str, tier: str, table: str) -> dict:
    beta = result.params.get(var, np.nan)
    p = result.pvalues.get(var, np.nan)
    return {
        "table": table,
        "outcome": outcome,
        "engagement_tier": tier,
        "variable": var,
        "variable_label": label,
        "irr": math.exp(beta) if pd.notna(beta) else np.nan,
        "beta": beta,
        "se": result.bse.get(var, np.nan),
        "z": result.tvalues.get(var, np.nan),
        "p": p,
        "sig": stars(p),
        "pct_change": (math.exp(beta) - 1) * 100 if pd.notna(beta) else np.nan,
        "nobs": int(result.nobs),
    }


def ame_point(result, data: pd.DataFrame, var: str) -> float:
    """AME point estimate for a continuous predictor under the NB log link:
    d mu/d x = mu * beta, averaged over the sample."""
    beta = result.params.get(var, np.nan)
    if pd.isna(beta):
        return np.nan
    return float(np.mean(result.predict(data) * beta))


def ame_cluster_bootstrap(
    df: pd.DataFrame, outcome: str, rhs: str, n_boot: int = 300, seed: int = 42
) -> pd.DataFrame:
    """Cluster bootstrap (resample mid groups) for AME of each focal dimension.

    Replaces the invalid delta-method shortcut: refits the GLM-NB on each
    cluster-resampled dataset and recomputes the AME, then takes the bootstrap
    SD / percentile CI. This propagates coefficient covariance honestly."""
    base = fit_nb(df, outcome, rhs)
    point = {v: ame_point(base, df, v) for v, _ in DIMENSIONS}

    groups = df["mid"].to_numpy()
    uniq = np.unique(groups)
    idx_by_g = {g: np.where(groups == g)[0] for g in uniq}
    rng = np.random.default_rng(seed)

    draws: dict[str, list[float]] = {v: [] for v, _ in DIMENSIONS}
    for _ in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        rows = np.concatenate([idx_by_g[g] for g in pick])
        boot = df.iloc[rows].copy()
        try:
            res = fit_nb(boot, outcome, rhs)
        except Exception:  # noqa: BLE001 - skip degenerate resamples
            continue
        for v, _ in DIMENSIONS:
            draws[v].append(ame_point(res, boot, v))

    out = []
    for v, vlabel in DIMENSIONS:
        d = np.asarray(draws[v], dtype=float)
        d = d[np.isfinite(d)]
        out.append({
            "outcome": outcome, "variable": v, "variable_label": vlabel,
            "ame": point[v],
            "ame_boot_se": float(np.std(d, ddof=1)) if d.size > 2 else np.nan,
            "ame_ci_lo": float(np.percentile(d, 2.5)) if d.size > 2 else np.nan,
            "ame_ci_hi": float(np.percentile(d, 97.5)) if d.size > 2 else np.nan,
            "n_boot_ok": int(d.size),
        })
    return pd.DataFrame(out)


def run_main(df: pd.DataFrame, ame_boot: int = 300) -> None:
    dim_rhs = " + ".join(v for v, _ in DIMENSIONS) + " + " + CONTROLS
    rows, alpha_rows, ame_frames = [], [], []
    rhs_c = dim_rhs.replace("C(category)", "C(category_c)")
    for outcome, label, tier in OUTCOMES:
        res = fit_nb(df, outcome, dim_rhs)
        alpha_rows.append({"outcome": outcome,
                           "nb_alpha": _estimate_alpha(df, outcome, rhs_c)})
        for var, vlabel in DIMENSIONS:
            rows.append(focal_row(res, var, outcome, vlabel, tier, "main_nb_cluster"))
        ame_frames.append(ame_cluster_bootstrap(df, outcome, dim_rhs, n_boot=ame_boot))
    pd.DataFrame(rows).to_csv(OUT_DIR / "nb_main_dimensions.csv", index=False, encoding="utf-8-sig")
    pd.concat(ame_frames, ignore_index=True).to_csv(
        OUT_DIR / "nb_main_ame.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(alpha_rows).to_csv(OUT_DIR / "nb_alpha_by_outcome.csv", index=False, encoding="utf-8-sig")
    print("[main NB] written nb_main_dimensions.csv, nb_main_ame.csv (cluster bootstrap), nb_alpha_by_outcome.csv")


def run_binary(df: pd.DataFrame) -> None:
    rhs = "visual_clickbait_bin + clip_sim_z + " + CONTROLS
    rows = []
    for outcome, label, tier in OUTCOMES:
        res = fit_nb(df, outcome, rhs)
        rows.append(focal_row(res, "visual_clickbait_bin", outcome, "视觉点击诱饵(二分)", tier, "binary_nb_cluster"))
        rows.append(focal_row(res, "clip_sim_z", outcome, "CLIP图文相似度", tier, "binary_nb_cluster"))
    pd.DataFrame(rows).to_csv(OUT_DIR / "nb_binary_clickbait.csv", index=False, encoding="utf-8-sig")
    print("[binary NB] written nb_binary_clickbait.csv")


def run_zinb_coin(df: pd.DataFrame) -> None:
    dim_rhs = " + ".join(v for v, _ in DIMENSIONS) + " + " + CONTROLS
    res = fit_zinb(df, "coin", dim_rhs)
    params, bse, pvals, tvals = res.params, res.bse, res.pvalues, res.tvalues
    rows = []
    # Report the count-part coefficients for the eight focal dimensions.
    for var, vlabel in DIMENSIONS:
        if var not in params.index:
            continue
        beta = params[var]
        p = pvals[var]
        rows.append({
            "table": "zinb_coin_count", "outcome": "coin", "variable": var,
            "variable_label": vlabel, "irr": math.exp(beta),
            "beta": beta, "se": bse[var], "z": tvals[var], "p": p,
            "sig": stars(p), "pct_change": (math.exp(beta) - 1) * 100,
            "nobs": int(res.nobs),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "zinb_coin_dimensions.csv", index=False, encoding="utf-8-sig")
    has_se = not out["se"].isna().all()
    print(f"[ZINB coin] written zinb_coin_dimensions.csv "
          f"(converged={res.mle_retvals.get('converged')}, usable_SE={has_se})")


def run_hurdle_coin(df: pd.DataFrame) -> None:
    """NB hurdle for coin: (1) logit P(coin>0), (2) NB on coin>0 subset.

    More numerically stable than ZINB on these extreme counts; both stages
    carry mid-cluster-robust SE. This is the primary zero-handling model for
    coin; ZINB is retained only as an archived point-estimate sensitivity."""
    dim_rhs = " + ".join(v for v, _ in DIMENSIONS) + " + " + CONTROLS
    rhs_c = dim_rhs.replace("C(category)", "C(category_c)")
    df = df.copy()
    df["coin_pos"] = (df["coin"] > 0).astype(int)

    rows = []
    # Stage 1: logit of any-coin.
    logit = smf.logit(f"coin_pos ~ {rhs_c}", data=df).fit(
        disp=0, cov_type="cluster", cov_kwds={"groups": df["mid"]})
    for var, vlabel in DIMENSIONS:
        rows.append({
            "stage": "hurdle1_logit_anycoin", "outcome": "coin", "variable": var,
            "variable_label": vlabel, "or": math.exp(logit.params[var]),
            "beta": logit.params[var], "se": logit.bse[var], "z": logit.tvalues[var],
            "p": logit.pvalues[var], "sig": stars(logit.pvalues[var]),
            "nobs": int(logit.nobs),
        })
    # Stage 2: zero-truncated NB on positive-coin subset (correct hurdle form).
    # Falls back to an untruncated NB-GLM if the truncated MLE fails to invert.
    pos = df[df["coin"] > 0].copy()
    stage2_kind, nb_params, nb_bse, nb_p, nb_n = _fit_truncated_nb(pos, dim_rhs)
    for var, vlabel in DIMENSIONS:
        beta = nb_params.get(var, np.nan)
        se = nb_bse.get(var, np.nan)
        p = nb_p.get(var, np.nan)
        rows.append({
            "stage": stage2_kind, "outcome": "coin", "variable": var,
            "variable_label": vlabel,
            "or": math.exp(beta) if pd.notna(beta) else np.nan,
            "beta": beta, "se": se,
            "z": beta / se if pd.notna(se) and se else np.nan,
            "p": p, "sig": stars(p), "nobs": nb_n,
        })
    pd.DataFrame(rows).to_csv(OUT_DIR / "hurdle_coin_dimensions.csv", index=False, encoding="utf-8-sig")
    print(f"[hurdle coin] written hurdle_coin_dimensions.csv "
          f"(stage1 N={int(logit.nobs)}, stage2={stage2_kind} N={nb_n})")


def _fit_truncated_nb(pos: pd.DataFrame, dim_rhs: str):
    """Try zero-truncated NB; on failure, fall back to untruncated NB-GLM.
    Returns (stage_label, params_dict, bse_dict, pvalues_dict, nobs)."""
    from statsmodels.discrete.truncated_model import TruncatedLFNegativeBinomialP

    rhs_c = dim_rhs.replace("C(category)", "C(category_c)")
    X = sm.add_constant(_design(pos, rhs_c)).astype(float)
    y = pos["coin"].to_numpy()
    try:
        res = TruncatedLFNegativeBinomialP(y, X, truncation=0).fit(
            method="bfgs", maxiter=1000, disp=0)
        bse = np.asarray(res.bse, dtype=float)
        if not np.any(np.isnan(bse)):
            names = X.columns.tolist()
            p = dict(zip(names, res.params))
            b = dict(zip(names, res.bse))
            pv = dict(zip(names, res.pvalues))
            return "hurdle2_ztnb_poscoin", p, b, pv, int(res.nobs)
    except Exception:  # noqa: BLE001
        pass
    # Fallback: untruncated NB-GLM with cluster SE (approximation).
    nb = fit_nb(pos, "coin", dim_rhs)
    return ("hurdle2_nb_poscoin_approx",
            dict(nb.params), dict(nb.bse), dict(nb.pvalues), int(nb.nobs))


def run_interaction(df: pd.DataFrame) -> None:
    """Representativeness x visual-clickbait (binary) interaction on each outcome."""
    rhs = "visual_clickbait_bin * rep_z + clip_sim_z + " + CONTROLS
    rows = []
    for outcome, label, tier in OUTCOMES:
        res = fit_nb(df, outcome, rhs)
        for var in ("visual_clickbait_bin", "rep_z", "visual_clickbait_bin:rep_z"):
            rows.append(focal_row(res, var, outcome, var, tier, "interaction_nb_cluster"))
    pd.DataFrame(rows).to_csv(OUT_DIR / "nb_interaction_rep.csv", index=False, encoding="utf-8-sig")
    print("[interaction] written nb_interaction_rep.csv")


def run_robustness(df: pd.DataFrame) -> None:
    dim_rhs = " + ".join(v for v, _ in DIMENSIONS) + " + " + CONTROLS
    subsets = {
        "post2022": df[df["pub_year"] >= 2022].copy(),
        "drop_top5pct_follower": df[
            pd.to_numeric(df["follower"], errors="coerce")
            < pd.to_numeric(df["follower"], errors="coerce").quantile(0.95)
        ].copy(),
        "science_only": df[df["category"] == "科学科普"].copy(),
    }
    rows = []
    for sub_name, sub in subsets.items():
        for outcome, label, tier in OUTCOMES:
            try:
                res = fit_nb(sub, outcome, dim_rhs)
            except Exception as exc:  # noqa: BLE001 - record convergence issues
                rows.append({"subset": sub_name, "outcome": outcome, "variable": "ERROR",
                             "variable_label": str(exc)[:80], "beta": np.nan, "p": np.nan,
                             "sig": "", "nobs": len(sub)})
                continue
            for var, vlabel in DIMENSIONS:
                r = focal_row(res, var, outcome, vlabel, tier, f"robust_{sub_name}")
                r["subset"] = sub_name
                rows.append(r)
    pd.DataFrame(rows).to_csv(OUT_DIR / "nb_robustness.csv", index=False, encoding="utf-8-sig")
    print("[robustness] written nb_robustness.csv")

    # Poisson cross-check (main spec) for over-dispersion sensitivity.
    pois_rows = []
    for outcome, label, tier in OUTCOMES:
        res = fit_poisson(df, outcome, dim_rhs)
        for var, vlabel in DIMENSIONS:
            pois_rows.append(focal_row(res, var, outcome, vlabel, tier, "poisson_cluster"))
    pd.DataFrame(pois_rows).to_csv(OUT_DIR / "poisson_crosscheck.csv", index=False, encoding="utf-8-sig")
    print("[poisson] written poisson_crosscheck.csv")


def main() -> None:
    df = load_sample()
    print(f"Sample N={len(df)}, unique mid={df['mid'].nunique()}")
    run_main(df)
    run_binary(df)
    run_hurdle_coin(df)
    run_interaction(df)
    run_robustness(df)
    run_zinb_coin(df)  # archived point-estimate sensitivity (SE often unavailable)
    print("\nAll formal models complete. Outputs in:", OUT_DIR)


if __name__ == "__main__":
    main()
