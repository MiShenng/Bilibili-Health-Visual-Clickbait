from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[2]
ANN_PATH = ROOT / "data/private/visual_clickbait_codes.csv"
CLIP_PATH = ROOT / "data/private/bilibili_health_clean_clip.csv"
OUT_DIR = ROOT / "results/tables"


OUTCOMES = [
    ("play", "播放量", "exposure"),
    ("like", "点赞", "low_cost"),
    ("coin", "投币", "high_cost"),
    ("favorites", "收藏", "high_cost"),
    ("share", "转发", "diffusion"),
]

DIMENSIONS = [
    ("clip_sim_z", "CLIP图文相似度"),
    ("emotion_z", "情感强度"),
    ("fear_z", "恐惧诉求"),
    ("text_z", "文字覆盖强度"),
    ("suspense_z", "视觉悬念"),
    ("info_gap_z", "信息缺口"),
    ("rep_z", "图文代表性"),
    ("auth_z", "权威线索"),
]


def to_num(frame: pd.DataFrame, cols: list[str]) -> None:
    for col in cols:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")


def zscore(series: pd.Series) -> pd.Series:
    sd = series.std(skipna=True)
    if sd == 0 or math.isnan(sd):
        return series * np.nan
    return (series - series.mean(skipna=True)) / sd


def stars(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    if p_value < 0.1:
        return "+"
    return ""


def cohen_kappa(a: pd.Series, b: pd.Series) -> float:
    tab = pd.crosstab(a, b)
    n = tab.values.sum()
    if n == 0:
        return float("nan")
    po = np.trace(tab.values) / n
    row = tab.sum(axis=1).to_numpy() / n
    col = tab.sum(axis=0).to_numpy() / n
    pe = float(np.dot(row, col))
    if pe == 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def ols_focal_table(
    data: pd.DataFrame,
    formula_rhs: str,
    focal_vars: list[tuple[str, str]],
    table_name: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for outcome, outcome_label, tier in OUTCOMES:
        model_data = data.copy()
        model_data[f"log_{outcome}"] = np.log1p(model_data[outcome].fillna(0))
        formula = f"log_{outcome} ~ {formula_rhs}"
        result = smf.ols(formula, data=model_data).fit(cov_type="HC3")
        for var, label in focal_vars:
            beta = result.params.get(var, np.nan)
            p_value = result.pvalues.get(var, np.nan)
            rows.append(
                {
                    "table": table_name,
                    "outcome": outcome,
                    "outcome_label": outcome_label,
                    "engagement_tier": tier,
                    "variable": var,
                    "variable_label": label,
                    "beta": beta,
                    "se_hc3": result.bse.get(var, np.nan),
                    "t": result.tvalues.get(var, np.nan),
                    "p": p_value,
                    "sig": stars(p_value),
                    "percent_change_approx": (math.exp(beta) - 1) * 100 if pd.notna(beta) else np.nan,
                    "nobs": int(result.nobs),
                    "r2": result.rsquared,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ann = pd.read_csv(ANN_PATH, encoding="utf-8-sig", low_memory=False)
    clip = pd.read_csv(CLIP_PATH, encoding="utf-8-sig", low_memory=False)

    success = ann.loc[ann["status"].eq("success")].copy()
    success = success.rename(columns={"video_id": "bvid"})

    clip_extra_cols = ["bvid", "clip_sim", "follower", "duration"]
    clip_extra = clip.loc[:, clip_extra_cols].drop_duplicates("bvid")
    merged = success.merge(clip_extra, on="bvid", how="left", validate="many_to_one")

    numeric_cols = [
        "play",
        "like",
        "coin",
        "favorites",
        "share",
        "video_age_days",
        "emotion_intensity",
        "fear_appeal",
        "text_overlay_intensity",
        "visual_suspense",
        "info_gap",
        "thumbnail_title_representativeness",
        "medical_authority_cue",
        "llm_clickbait_direct",
        "visual_clickbait_binary",
        "visual_clickbait_type",
        "confidence",
        "clip_sim",
        "follower",
        "duration",
    ]
    to_num(merged, numeric_cols)

    merged["is_official_num"] = merged["is_official"].astype(str).str.upper().eq("TRUE").astype(int)
    merged["visual_clickbait_bin"] = merged["visual_clickbait_binary"]
    merged["direct_clickbait_bin"] = merged["llm_clickbait_direct"]
    merged["category"] = merged["category"].fillna("未知").astype(str)
    merged["log_follower"] = np.log1p(merged["follower"])
    merged["log_duration"] = np.log1p(merged["duration"])
    merged["log_age"] = np.log1p(merged["video_age_days"])

    model_required = [
        "clip_sim",
        "follower",
        "duration",
        "video_age_days",
        "visual_clickbait_bin",
        "emotion_intensity",
        "fear_appeal",
        "text_overlay_intensity",
        "visual_suspense",
        "info_gap",
        "thumbnail_title_representativeness",
        "medical_authority_cue",
    ]
    model_df = merged.dropna(subset=model_required).copy()

    z_sources = {
        "clip_sim_z": "clip_sim",
        "log_follower_z": "log_follower",
        "log_duration_z": "log_duration",
        "log_age_z": "log_age",
        "emotion_z": "emotion_intensity",
        "fear_z": "fear_appeal",
        "text_z": "text_overlay_intensity",
        "suspense_z": "visual_suspense",
        "info_gap_z": "info_gap",
        "rep_z": "thumbnail_title_representativeness",
        "auth_z": "medical_authority_cue",
    }
    for z_col, raw_col in z_sources.items():
        model_df[z_col] = zscore(model_df[raw_col])

    merged.to_csv(OUT_DIR / "bilibili_health_visual_clickbait_merged_success.csv", index=False, encoding="utf-8-sig")
    model_df.to_csv(OUT_DIR / "bilibili_health_visual_clickbait_model_sample.csv", index=False, encoding="utf-8-sig")

    sample_flow = pd.DataFrame(
        [
            {"step": "annotation_rows", "n": len(ann)},
            {"step": "annotation_success", "n": len(success)},
            {"step": "annotation_failed", "n": int(ann["status"].ne("success").sum())},
            {"step": "success_with_clip_sim", "n": int(merged["clip_sim"].notna().sum())},
            {"step": "success_with_follower", "n": int(merged["follower"].notna().sum())},
            {"step": "complete_model_sample", "n": len(model_df)},
        ]
    )
    sample_flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")

    desc_vars = [
        ("visual_clickbait_bin", "视觉点击诱饵二分"),
        ("direct_clickbait_bin", "LLM直接点击诱饵二分"),
        ("emotion_intensity", "情感强度"),
        ("fear_appeal", "恐惧诉求"),
        ("text_overlay_intensity", "文字覆盖强度"),
        ("visual_suspense", "视觉悬念"),
        ("info_gap", "信息缺口"),
        ("thumbnail_title_representativeness", "图文代表性"),
        ("medical_authority_cue", "权威线索"),
        ("clip_sim", "CLIP图文相似度"),
        ("play", "播放量"),
        ("like", "点赞"),
        ("coin", "投币"),
        ("favorites", "收藏"),
        ("share", "转发"),
    ]
    desc_rows = []
    for col, label in desc_vars:
        data = merged[col].dropna()
        desc_rows.append(
            {
                "variable": col,
                "label": label,
                "n": int(data.shape[0]),
                "mean": data.mean(),
                "sd": data.std(),
                "median": data.median(),
                "p25": data.quantile(0.25),
                "p75": data.quantile(0.75),
                "min": data.min(),
                "max": data.max(),
            }
        )
    pd.DataFrame(desc_rows).to_csv(OUT_DIR / "descriptive_stats.csv", index=False, encoding="utf-8-sig")

    type_dist = (
        merged["visual_clickbait_type"]
        .value_counts(dropna=False)
        .rename_axis("visual_clickbait_type")
        .reset_index(name="n")
    )
    type_dist["pct"] = type_dist["n"] / len(merged)
    type_dist.to_csv(OUT_DIR / "visual_clickbait_type_distribution.csv", index=False, encoding="utf-8-sig")

    mean_rows = []
    for subset_name, frame in [("all_success", merged), ("complete_model_sample", model_df)]:
        for outcome, label, tier in OUTCOMES:
            g = frame.groupby("visual_clickbait_bin")[outcome].agg(["count", "mean", "median", "std"]).reset_index()
            if set(g["visual_clickbait_bin"].dropna().astype(int)) >= {0, 1}:
                g0 = g.loc[g["visual_clickbait_bin"].eq(0), "mean"].iloc[0]
                g1 = g.loc[g["visual_clickbait_bin"].eq(1), "mean"].iloc[0]
                diff = g1 - g0
                pct = diff / g0 * 100 if g0 else np.nan
            else:
                diff = np.nan
                pct = np.nan
            for _, row in g.iterrows():
                mean_rows.append(
                    {
                        "subset": subset_name,
                        "outcome": outcome,
                        "outcome_label": label,
                        "engagement_tier": tier,
                        "visual_clickbait_bin": row["visual_clickbait_bin"],
                        "n": row["count"],
                        "mean": row["mean"],
                        "median": row["median"],
                        "sd": row["std"],
                        "mean_difference_clickbait_minus_non": diff,
                        "mean_difference_pct": pct,
                    }
                )
    pd.DataFrame(mean_rows).to_csv(OUT_DIR / "mean_comparison_by_clickbait.csv", index=False, encoding="utf-8-sig")

    controls = "is_official_num + log_follower_z + log_duration_z + log_age_z + C(category)"
    binary_rhs = "visual_clickbait_bin + clip_sim_z + " + controls
    binary_table = ols_focal_table(
        model_df,
        binary_rhs,
        [("visual_clickbait_bin", "视觉点击诱饵"), ("clip_sim_z", "CLIP图文相似度")],
        "binary_clickbait_ols_hc3",
    )
    binary_table.to_csv(OUT_DIR / "ols_binary_clickbait.csv", index=False, encoding="utf-8-sig")

    dim_rhs = " + ".join([var for var, _ in DIMENSIONS]) + " + " + controls
    dim_table = ols_focal_table(model_df, dim_rhs, DIMENSIONS, "dimension_ols_hc3")
    dim_table.to_csv(OUT_DIR / "ols_visual_dimensions.csv", index=False, encoding="utf-8-sig")

    if merged["direct_clickbait_bin"].notna().any():
        agreement_frame = merged.dropna(subset=["direct_clickbait_bin", "visual_clickbait_bin"]).copy()
        agreement = pd.crosstab(
            agreement_frame["direct_clickbait_bin"].astype(int),
            agreement_frame["visual_clickbait_bin"].astype(int),
            rownames=["llm_direct"],
            colnames=["derived_rule"],
        )
        agreement.to_csv(OUT_DIR / "direct_vs_derived_clickbait_crosstab.csv", encoding="utf-8-sig")
        kappa = cohen_kappa(
            agreement_frame["direct_clickbait_bin"].astype(int),
            agreement_frame["visual_clickbait_bin"].astype(int),
        )
        agreement_pct = (
            agreement_frame["direct_clickbait_bin"].astype(int).eq(agreement_frame["visual_clickbait_bin"].astype(int)).mean()
        )
    else:
        agreement_pct = float("nan")
        kappa = float("nan")

    # Pull the main effects used in the narrative.
    def effect(table: pd.DataFrame, outcome: str, variable: str) -> pd.Series:
        return table.loc[(table["outcome"].eq(outcome)) & (table["variable"].eq(variable))].iloc[0]

    emotion_like = effect(dim_table, "like", "emotion_z")
    emotion_play = effect(dim_table, "play", "emotion_z")
    clip_like = effect(dim_table, "like", "clip_sim_z")
    auth_like = effect(dim_table, "like", "auth_z")
    rep_play = effect(dim_table, "play", "rep_z")
    binary_like = effect(binary_table, "like", "visual_clickbait_bin")

    summary = f"""# B站健康视频视觉点击诱饵编码结果整合分析

## 1. 样本与合并结果

- 编码表原始样本：{len(ann):,} 条。
- LLM 成功编码：{len(success):,} 条；失败：{int(ann["status"].ne("success").sum()):,} 条。
- 成功样本中可合并到 CLIP / 粉丝数 / 时长信息的完整建模样本：{len(model_df):,} 条。
- 因此，描述统计基于成功编码样本，主回归基于完整建模样本；这比把缺失粉丝数或 CLIP 相似度当成 0 更稳妥。

## 2. 编码分布

- 派生规则判定的视觉点击诱饵：{int(merged["visual_clickbait_bin"].eq(1).sum()):,} / {len(merged):,}（{merged["visual_clickbait_bin"].eq(1).mean():.1%}）。
- LLM 直接判定的点击诱饵：{int(merged["direct_clickbait_bin"].eq(1).sum()):,} / {int(merged["direct_clickbait_bin"].notna().sum()):,}（{merged["direct_clickbait_bin"].eq(1).mean():.1%}）。
- 直接判定与派生判定的一致率：{agreement_pct:.1%}；Cohen's kappa = {kappa:.3f}。

## 3. 均值对比：点击诱饵视频的参与更高，但这是未控制差异

在全部成功编码样本中，视觉点击诱饵视频的平均播放、点赞、投币、收藏均高于非点击诱饵视频；转发略低。这个结果适合写作中作为描述性证据，但不能单独作为因果或净效应证据，因为创作者粉丝数、视频时长、发布时间、分区等因素尚未控制。

## 4. 主回归结果：真正稳定的是“视觉机制”，不是简单二分

主模型使用 log(参与量+1) OLS、HC3 稳健标准误，并控制官方账号、粉丝数、视频时长、视频年龄与分区固定效应。

- 情感强度是最稳定的正向机制：对点赞 β={emotion_like["beta"]:.3f}, p={emotion_like["p"]:.4f}；对播放 β={emotion_play["beta"]:.3f}, p={emotion_play["p"]:.4f}。缩略图越情绪化，用户越容易产生低成本参与和观看。
- CLIP 图文相似度呈负向：对点赞 β={clip_like["beta"]:.3f}, p={clip_like["p"]:.4f}。也就是说，图文越语义一致，参与越低；图文落差或不完全代表性更能制造点击动机。
- 权威线索强烈负向：对点赞 β={auth_like["beta"]:.3f}, p={auth_like["p"]:.4f}。白大褂、机构、论文截图等“正规”符号提升可信感，但未必提升平台互动。
- 图文代表性对播放为负：β={rep_play["beta"]:.3f}, p={rep_play["p"]:.4f}。这与 CLIP 相似度的负向结果互相印证。
- 简单二分的视觉点击诱饵变量在控制后并不一定正向：点赞模型中 β={binary_like["beta"]:.3f}, p={binary_like["p"]:.4f}。这说明论文最好不要只讲“是不是点击诱饵”，而要讲“点击诱饵由哪些视觉机制构成”。

## 5. 一句话结论

B站健康类短视频的用户参与不是由“权威、规范、图文高度一致”的视觉呈现推动，而更像是由情绪强度、图文落差和低代表性所激发的注意力机制推动；但这种机制主要体现在具体视觉维度上，而不是一个粗糙的点击诱饵二分变量上。

## 6. 输出文件

- 合并成功样本：`{OUT_DIR / "bilibili_health_visual_clickbait_merged_success.csv"}`
- 完整建模样本：`{OUT_DIR / "bilibili_health_visual_clickbait_model_sample.csv"}`
- 描述统计：`{OUT_DIR / "descriptive_stats.csv"}`
- 均值对比：`{OUT_DIR / "mean_comparison_by_clickbait.csv"}`
- 二分点击诱饵 OLS：`{OUT_DIR / "ols_binary_clickbait.csv"}`
- 视觉维度 OLS：`{OUT_DIR / "ols_visual_dimensions.csv"}`
"""
    (OUT_DIR / "analysis_summary.md").write_text(summary, encoding="utf-8")

    print(summary)
    print(f"\nSaved outputs to: {OUT_DIR}")


if __name__ == "__main__":
    main()
