"""
合并 4 个 CSV 为 master 表，去重，输出质量报告。

输入:
  Web crawler/output/bilibili_health_500.csv          (老 pilot)
  Web crawler/output/bilibili_health_related_1000.csv (老 related)
  Web crawler/output/bilibili_health_3000_part1.csv   (本次加速前)
  Web crawler/output/bilibili_health_3000.csv         (本次加速后)

输出:
  Data process/master_bilibili_health.csv             (去重后总表)
  Data process/audit_report.md                        (质量报告)
"""

import os
import sys
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRAWLER_OUT = os.path.join(ROOT, "Web crawler", "output")
DATA_OUT = os.path.join(ROOT, "Data process")
os.makedirs(DATA_OUT, exist_ok=True)

INPUTS = [
    ("old_pilot_500",    os.path.join(CRAWLER_OUT, "bilibili_health_500.csv")),
    ("old_related_1000", os.path.join(CRAWLER_OUT, "bilibili_health_related_1000.csv")),
    ("v3000_part1",      os.path.join(CRAWLER_OUT, "bilibili_health_3000_part1.csv")),
    ("v3000_part2",      os.path.join(CRAWLER_OUT, "bilibili_health_3000.csv")),
    ("v10k_part1",       os.path.join(CRAWLER_OUT, "bilibili_health_10k_part1.csv")),
    ("v10k_part2",       os.path.join(CRAWLER_OUT, "bilibili_health_10k.csv")),
]

MASTER_PATH = os.path.join(DATA_OUT, "master_bilibili_health.csv")
REPORT_PATH = os.path.join(DATA_OUT, "audit_report.md")

# -------- 1. 读取所有 CSV，统一字段 --------
all_rows = []
per_file_count = {}
all_fields = set()

for src_name, path in INPUTS:
    if not os.path.exists(path):
        print(f"WARN missing: {path}")
        per_file_count[src_name] = 0
        continue
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cnt = 0
        for row in reader:
            row["_source_file"] = src_name
            all_rows.append(row)
            all_fields.update(row.keys())
            cnt += 1
    per_file_count[src_name] = cnt
    print(f"OK {src_name}: {cnt} rows")

print(f"\n总行数（去重前）: {len(all_rows)}")
print(f"字段并集: {len(all_fields)} 个")

# -------- 2. 去重（按 bvid，保留信息最全的那条） --------
def info_score(row):
    return sum(1 for v in row.values() if v not in ("", None, "0", 0))

by_bvid = {}
no_bvid = 0
for row in all_rows:
    bvid = (row.get("bvid") or "").strip()
    if not bvid:
        no_bvid += 1
        continue
    if bvid not in by_bvid or info_score(row) > info_score(by_bvid[bvid]):
        by_bvid[bvid] = row

print(f"\n去重后唯一视频数: {len(by_bvid)}")
print(f"丢弃无bvid行: {no_bvid}")

# -------- 3. 写 master CSV --------
priority = [
    "bvid","aid","title","description","tag","pubdate","duration",
    "category","tid","copyright",
    "author","mid","follower","is_official","official_title",
    "uploader_level","uploader_sign",
    "play","danmaku","review","favorites","coin","share","like",
    "like_to_play_ratio","fav_to_play_ratio","engagement_score",
    "pic_url","thumbnail_local_path","query","rank","order","order_api",
    "crawl_timestamp","video_age_days",
    "_source_file",
]
extra = sorted(f for f in all_fields if f not in priority)
columns = priority + extra

def csv_esc(v):
    if v is None:
        return ""
    s = str(v).replace("\r", " ").replace("\n", " ")
    if "," in s or '"' in s:
        s = '"' + s.replace('"', '""') + '"'
    return s

with open(MASTER_PATH, "w", encoding="utf-8-sig") as f:
    f.write(",".join(columns) + "\n")
    for row in by_bvid.values():
        f.write(",".join(csv_esc(row.get(c, "")) for c in columns) + "\n")

print(f"\n写入 master: {MASTER_PATH}")

# -------- 4. 质量报告 --------
rows = list(by_bvid.values())
N = len(rows)

def field_complete(field):
    return sum(1 for r in rows if r.get(field) not in ("", None))

def numeric_field(field):
    vals = []
    for r in rows:
        v = r.get(field, "")
        if v in ("", None):
            continue
        try:
            vals.append(float(v))
        except Exception:
            pass
    return vals

# 关键字段完整率
key_fields = [
    "bvid","title","pic_url","thumbnail_local_path","pubdate",
    "play","like","coin","favorites","share","danmaku",
    "follower","is_official","tid","copyright","uploader_level",
    "video_age_days","crawl_timestamp",
]
completeness = {f: (field_complete(f), field_complete(f)/N*100) for f in key_fields}

# 来源分布
source_dist = Counter(r.get("_source_file","") for r in rows)
query_dist  = Counter(r.get("query","") for r in rows)
order_dist  = Counter(r.get("order","") or r.get("order_api","") for r in rows)
official_dist = Counter(r.get("is_official","") for r in rows)
copyright_dist = Counter(r.get("copyright","") for r in rows)
category_dist = Counter(r.get("category","") for r in rows)

# UP主数
unique_mids = len({r.get("mid","") for r in rows if r.get("mid","")})

# 缩略图本地存在
thumb_exist = 0
for r in rows:
    p = r.get("thumbnail_local_path","")
    if p and os.path.exists(p):
        thumb_exist += 1

# 因变量分布
def stats(vals, name):
    if not vals:
        return f"  - **{name}**: N/A"
    vals_sorted = sorted(vals)
    n = len(vals)
    mean = sum(vals)/n
    median = vals_sorted[n//2]
    p25 = vals_sorted[n//4]
    p75 = vals_sorted[3*n//4]
    p95 = vals_sorted[int(n*0.95)]
    zero = sum(1 for v in vals if v == 0)
    return f"  - **{name}**: N={n}  mean={mean:,.0f}  median={median:,.0f}  p25={p25:,.0f}  p75={p75:,.0f}  p95={p95:,.0f}  zero={zero/n*100:.1f}%"

dv_stats = {dv: numeric_field(dv) for dv in ["play","like","coin","favorites","share","danmaku","review"]}
follower_vals = numeric_field("follower")
age_vals = numeric_field("video_age_days")

# 写 markdown 报告
report = f"""# B站健康科普视频数据 — 质量审计报告

*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

## 1. 总览

| 项目 | 值 |
|---|---|
| **唯一视频数（去重后）** | **{N:,}** |
| 唯一 UP 主数 | {unique_mids:,} |
| 字段总数 | {len(columns)} |
| 缩略图本地已下载 | {thumb_exist:,} / {N:,} ({thumb_exist/N*100:.1f}%) |
| Master CSV 路径 | `{MASTER_PATH}` |

---

## 2. 来源文件统计

| 来源 | 原始行数 | 去重后保留 |
|---|---|---|
"""
for src, p in INPUTS:
    src_name = src
    raw = per_file_count.get(src, 0)
    kept = source_dist.get(src, 0)
    report += f"| `{src_name}` | {raw:,} | {kept:,} |\n"

report += f"""| **合计** | **{sum(per_file_count.values()):,}** | **{N:,}** |

去重消除的重复行数: **{sum(per_file_count.values()) - N - no_bvid:,}** 条
无 bvid 行（已丢弃）: {no_bvid} 条

---

## 3. 关键字段完整率

| 字段 | 非空数 | 完整率 |
|---|---|---|
"""
for f in key_fields:
    cnt, pct = completeness[f]
    icon = "✅" if pct >= 95 else ("⚠️" if pct >= 70 else "❌")
    report += f"| `{f}` | {cnt:,} | {icon} {pct:.1f}% |\n"

report += f"""
---

## 4. 因变量分布（用于回归建模诊断）

{stats(dv_stats['play'], 'play 播放')}
{stats(dv_stats['like'], 'like 点赞')}
{stats(dv_stats['coin'], 'coin 投币')}
{stats(dv_stats['favorites'], 'favorites 收藏')}
{stats(dv_stats['share'], 'share 分享')}
{stats(dv_stats['danmaku'], 'danmaku 弹幕')}
{stats(dv_stats['review'], 'review 评论')}

**零值比例诊断（决定计数模型选择）:**

| 变量 | 零值比例 | 推荐模型 |
|---|---|---|
"""
for dv in ["play","like","coin","favorites","share","danmaku","review"]:
    vals = dv_stats[dv]
    if not vals:
        continue
    zr = sum(1 for v in vals if v == 0) / len(vals) * 100
    if zr < 5:
        rec = "负二项 NB"
    elif zr < 20:
        rec = "NB（检验是否需 ZINB）"
    else:
        rec = "**ZINB / Hurdle**"
    report += f"| {dv} | {zr:.1f}% | {rec} |\n"

report += f"""
---

## 5. 控制变量分布

### 5.1 视频年龄 (video_age_days)
"""
if age_vals:
    n = len(age_vals)
    age_sorted = sorted(age_vals)
    report += f"""
- N = {n:,}
- min = {min(age_vals):.0f} 天 ({min(age_vals)/365:.2f} 年)
- max = {max(age_vals):.0f} 天 ({max(age_vals)/365:.2f} 年)
- median = {age_sorted[n//2]:.0f} 天
- mean = {sum(age_vals)/n:.0f} 天
- **>2年的视频数**: {sum(1 for v in age_vals if v > 730)} ({sum(1 for v in age_vals if v > 730)/n*100:.1f}%)
"""

report += f"""
### 5.2 UP主粉丝数 (follower)
"""
if follower_vals:
    n = len(follower_vals)
    fs = sorted(follower_vals)
    report += f"""
- N = {n:,}
- median = {fs[n//2]:,.0f}
- p95 = {fs[int(n*0.95)]:,.0f}
- max = {max(follower_vals):,.0f}
"""

report += f"""
### 5.3 认证状态 (is_official)

| 状态 | 数量 | 比例 |
|---|---|---|
"""
for k, v in official_dist.most_common():
    report += f"| `{k}` | {v:,} | {v/N*100:.1f}% |\n"

report += f"""
### 5.4 自制/转载 (copyright; 1=自制, 2=转载)

| 值 | 数量 | 比例 |
|---|---|---|
"""
for k, v in copyright_dist.most_common():
    label = {"1":"自制原创", "2":"转载搬运"}.get(str(k), "未知")
    report += f"| `{k}` ({label}) | {v:,} | {v/N*100:.1f}% |\n"

report += f"""
### 5.5 分区分布 (category)

| 分区 | 数量 |
|---|---|
"""
for k, v in category_dist.most_common(10):
    report += f"| {k or '(空)'} | {v:,} |\n"

report += f"""
---

## 6. 抽样元数据

### 6.1 关键词分布 (query) — Top 15

| 关键词 | 数量 |
|---|---|
"""
for k, v in query_dist.most_common(15):
    report += f"| {k} | {v:,} |\n"

report += f"""
### 6.2 排序方式分布 (order)

| 排序 | 数量 |
|---|---|
"""
for k, v in order_dist.most_common():
    report += f"| {k} | {v:,} |\n"

report += f"""
---

## 7. 样本量评估（按 decision-memo §8 标准）

| 分析 | 所需最小N | 当前N | 是否充足 |
|---|---|---|---|
| 视觉标题党 → 5 个 DV 主效应 | ~150 | {N:,} | {'✅' if N >= 150 else '❌'} 充足 |
| 图文代表性调节（H2/H3） | ~300 | {N:,} | {'✅' if N >= 300 else '❌'} 充足 |
| 认证×普通账号交互（H5；每组≥80） | 160 | 认证 {official_dist.get('TRUE',0):,} / 非认证 {official_dist.get('FALSE',0):,} | {'✅' if official_dist.get('TRUE',0) >= 80 and official_dist.get('FALSE',0) >= 80 else '⚠️'} |
| 自制/转载分层（每组≥100） | 200 | 自制 {copyright_dist.get('1',0):,} / 转载 {copyright_dist.get('2',0):,} | {'✅' if copyright_dist.get('1',0) >= 100 and copyright_dist.get('2',0) >= 100 else '⚠️'} |
| 200张人工标注（分层抽样） | 200 | 总池 {N:,} | ✅ 充足 |

---

## 8. 建议的下一步

1. **建立 200 张缩略图分层抽样脚本** —— 按 query × 认证 × 播放分位分层
2. **编写人工标注编码手册** —— 4 个视觉标题党子维度的打分标准
3. **数据预处理** —— `log_followers`、`coin_rate`、`fav_rate`、按月份固定效应
4. **CLIP 余弦相似度** —— 封面 vs 标题，算图文代表性自动化指标

---

*报告由 `Data process/merge_and_audit.py` 自动生成*
"""

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

print(f"写入报告: {REPORT_PATH}")
print("\n=== 完成 ===")
print(f"Master CSV:  {MASTER_PATH}")
print(f"Audit report: {REPORT_PATH}")
print(f"\n核心结果: 去重后 {N:,} 条唯一视频，{unique_mids:,} 个唯一UP主")
