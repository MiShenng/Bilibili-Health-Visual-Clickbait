"""
规则粗筛：把 master_bilibili_health.csv 中的"非健康"视频标记为 topic_relevance_rule=0

判断逻辑（双向）：
  - 白名单命中（医/药/病/症/血压/糖尿病/...）→ 健康嫌疑
  - 黑名单命中（鸡汤/搞笑/直播切片/广告/...）→ 非健康嫌疑
  - 分区是 "科学科普" → 健康加权
  - 分区是 "影视/搞笑/娱乐/游戏" → 非健康加权
  - 综合打分: 健康分 - 非健康分 ≥ 阈值 → 保留

输出:
  - master_with_rule_filter.csv: 原数据 + 新增 3 列 (rule_health_score, rule_keep)
  - rule_filter_report.md: 保留/剔除分布报告
  - rule_filter_dropped_sample.csv: 被剔除的 50 条随机样本（人工 spot-check 用）
"""

import csv
import re
import random
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_OUT = os.path.join(ROOT, "Data process")
MASTER = os.path.join(DATA_OUT, "master_bilibili_health.csv")
OUT_CSV = os.path.join(DATA_OUT, "master_with_rule_filter.csv")
REPORT = os.path.join(DATA_OUT, "rule_filter_report.md")
DROPPED_SAMPLE = os.path.join(DATA_OUT, "rule_filter_dropped_sample.csv")

# ─── 白名单：明确医学/健康词 ───
WHITELIST_STRONG = [
    # 疾病
    "癌症", "肿瘤", "糖尿病", "高血压", "心脏病", "脂肪肝", "胃病", "肾病", "甲状腺",
    "痛风", "颈椎病", "腰椎间盘", "骨质疏松", "乳腺癌", "胃癌", "肝癌", "肺癌",
    "结直肠癌", "白血病", "中风", "脑梗", "心梗", "梗死", "心律失常", "高血脂",
    "高胆固醇", "脱发", "失眠", "焦虑", "抑郁", "阿尔茨海默", "老年痴呆",
    "帕金森", "癫痫", "哮喘", "肺炎", "肠炎", "胃炎", "肾炎", "膀胱炎",
    "前列腺", "更年期", "宫颈", "HPV", "肝炎", "艾滋", "结核", "贫血", "白血病",
    # 症状/部位
    "症状", "病灶", "结节", "息肉", "炎症", "感染", "免疫力",
    # 药物/治疗
    "用药", "副作用", "药品", "药物", "处方", "化疗", "放疗", "手术",
    "治疗", "康复", "护理", "急救",
    # 医疗
    "医生", "医院", "门诊", "急诊", "医保", "护士", "病人", "患者",
    "体检", "检查", "化验", "检测", "诊断", "确诊", "复查",
    "三甲", "主任医师", "副主任医师", "医师", "医学", "临床",
    # 健康/营养
    "健康", "养生", "保健", "营养", "饮食", "膳食",
    "维生素", "蛋白质", "膳食纤维", "碳水", "脂肪", "钙", "铁",
    # 预防/筛查
    "疫苗", "接种", "筛查", "预防", "早期", "早筛", "信号", "征兆", "预警",
    # 妇幼
    "孕期", "孕妇", "产后", "新生儿", "儿童身高", "辅食",
    # 健康行为
    "减肥", "增肌", "BMI", "肥胖", "睡眠",
]

# ─── 黑名单：明确非健康/噪音词 ───
BLACKLIST = [
    # 鸡汤
    "鸡汤", "情商", "高情商", "心态", "成长", "蜕变", "顿悟", "觉醒",
    "自律", "自我提升", "改变自己",
    # 娱乐
    "影视", "电影", "电视剧", "综艺", "明星", "演员", "歌手", "rapper",
    "二次元", "动漫", "番剧", "vlog", "VLOG", "Vlog",
    # 游戏
    "游戏", "原神", "崩坏", "王者荣耀", "lol", "LOL", "电竞", "主播",
    # 政治/八卦
    "政治", "时政", "国际", "战争", "俄乌", "以色列", "巴勒斯坦",
    # 广告/带货
    "种草", "拔草", "好物", "购物", "开箱", "测评", "双11", "618",
    # 教学（非健康）
    "编程", "代码", "Python", "Java", "前端", "后端", "AI", "深度学习",
    "考研", "考公", "雅思", "托福",
    # 其他主题
    "汽车", "房产", "财经", "股票", "基金", "理财",
    "美食教学", "做菜", "菜谱", "烘焙", "甜品",
    # 健身教学（与医学健康不同）
    "瑜伽", "舞蹈", "舞蹈教学", "燃脂操", "暴汗", "塑形",
]

# ─── B 站分区映射 ───
CATEGORY_HEALTH_BOOST = {
    "科学科普": 3,    # 强加权
    "知识": 2,
    "社科·法律·心理": 2,
    "校园学习": 1,
    "日常": 0,        # 中性
    "搞笑": -3,       # 强黑名单
    "影视剪辑": -3,
    "游戏": -3,
    "明星": -3,
    "动画": -2,
    "舞蹈": -2,
    "音乐": -2,
    "时尚": -2,
    "美食": -1,       # 美食有部分跟健康相关
    "运动": 0,        # 运动可能是健身
    "汽车": -2,
    "鬼畜": -3,
    "人文历史": -1,
}

# ─── 评分阈值 ───
KEEP_THRESHOLD = 1   # 综合得分 ≥ 1 保留 (出现 ≥1 白名单 + 没有强黑信号)

def compile_patterns(words):
    """编译为单个 regex, 加速匹配"""
    escaped = [re.escape(w) for w in words]
    return re.compile("|".join(escaped))

WHITE_RE = compile_patterns(WHITELIST_STRONG)
BLACK_RE = compile_patterns(BLACKLIST)

def score_row(row):
    """
    返回 (health_score, white_hits, black_hits, cat_boost)
    """
    # 拼接文本
    text = " ".join([
        row.get("title", "") or "",
        row.get("description", "") or "",
        row.get("tag", "") or "",
    ])

    # 命中数量（不重复, 每个词最多算一次）
    white_hits = len(set(WHITE_RE.findall(text)))
    black_hits = len(set(BLACK_RE.findall(text)))

    # 分区加权
    cat = (row.get("category", "") or "").strip()
    cat_boost = CATEGORY_HEALTH_BOOST.get(cat, 0)

    # 综合分: 白名单 - 2*黑名单 + 分区加权
    score = white_hits - 2 * black_hits + cat_boost
    return score, white_hits, black_hits, cat_boost


def main():
    with open(MASTER, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    N = len(rows)
    print(f"读取 master: {N} rows")

    # 评分
    for r in rows:
        s, w, b, c = score_row(r)
        r["rule_health_score"] = s
        r["rule_white_hits"] = w
        r["rule_black_hits"] = b
        r["rule_cat_boost"] = c
        r["rule_keep"] = 1 if s >= KEEP_THRESHOLD else 0

    n_keep = sum(1 for r in rows if r["rule_keep"] == 1)
    n_drop = N - n_keep
    print(f"保留: {n_keep} ({n_keep/N*100:.1f}%)")
    print(f"剔除: {n_drop} ({n_drop/N*100:.1f}%)")

    # 写新 CSV
    original_cols = list(rows[0].keys())
    # 把新列移到前面方便查看
    extra = ["rule_keep", "rule_health_score", "rule_white_hits", "rule_black_hits", "rule_cat_boost"]
    cols = [c for c in original_cols if c not in extra] + extra

    def csv_esc(v):
        if v is None: return ""
        s = str(v).replace("\r", " ").replace("\n", " ")
        if "," in s or '"' in s:
            s = '"' + s.replace('"', '""') + '"'
        return s

    with open(OUT_CSV, "w", encoding="utf-8-sig") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(csv_esc(r.get(c, "")) for c in cols) + "\n")
    print(f"写入: {OUT_CSV}")

    # 50 条被剔除的随机样本
    dropped = [r for r in rows if r["rule_keep"] == 0]
    random.seed(42)
    sample = random.sample(dropped, min(50, len(dropped)))
    with open(DROPPED_SAMPLE, "w", encoding="utf-8-sig") as f:
        f.write("bvid,rule_health_score,category,title\n")
        for r in sample:
            f.write(f"{csv_esc(r['bvid'])},{r['rule_health_score']},{csv_esc(r.get('category',''))},{csv_esc(r.get('title',''))}\n")
    print(f"剔除样本（50 条）: {DROPPED_SAMPLE}")

    # 50 条保留的随机样本（确认没误留）
    kept = [r for r in rows if r["rule_keep"] == 1]
    sample_k = random.sample(kept, min(50, len(kept)))
    with open(DATA_OUT + "/rule_filter_kept_sample.csv", "w", encoding="utf-8-sig") as f:
        f.write("bvid,rule_health_score,category,title\n")
        for r in sample_k:
            f.write(f"{csv_esc(r['bvid'])},{r['rule_health_score']},{csv_esc(r.get('category',''))},{csv_esc(r.get('title',''))}\n")
    print(f"保留样本（50 条）: {DATA_OUT}/rule_filter_kept_sample.csv")

    # 写报告
    score_dist = Counter(r["rule_health_score"] for r in rows)
    cat_keep = Counter((r.get("category","") or "(空)", r["rule_keep"]) for r in rows)

    report = f"""# 规则粗筛报告 — {len(rows):,} 条数据

## 总览

| 项目 | 值 |
|---|---|
| 输入 N | {N:,} |
| **保留** | **{n_keep:,} ({n_keep/N*100:.1f}%)** |
| **剔除** | **{n_drop:,} ({n_drop/N*100:.1f}%)** |
| 阈值 | health_score ≥ {KEEP_THRESHOLD} |

## 评分公式
`health_score = white_hits − 2 × black_hits + category_boost`

- 白名单词表: {len(WHITELIST_STRONG)} 个医学/健康词
- 黑名单词表: {len(BLACKLIST)} 个噪音词（鸡汤/娱乐/游戏/广告等）
- 分区加权: 科学科普 +3, 知识 +2, 搞笑/影视/游戏 -3

## 健康得分分布

| 分数 | 数量 |
|---|---|
"""
    for s in sorted(score_dist.keys()):
        cnt = score_dist[s]
        mark = "✅ 保留" if s >= KEEP_THRESHOLD else "❌ 剔除"
        report += f"| {s} | {cnt:,} {mark if s == KEEP_THRESHOLD or s == KEEP_THRESHOLD - 1 else ''} |\n"

    report += f"""

## 按分区的保留率（Top 15）

| 分区 | 总数 | 保留 | 保留率 |
|---|---|---|---|
"""
    cat_total = Counter(r.get("category","") or "(空)" for r in rows)
    for cat, total in cat_total.most_common(15):
        kept_in_cat = sum(1 for r in rows if (r.get("category","") or "(空)") == cat and r["rule_keep"] == 1)
        rate = kept_in_cat / total * 100 if total else 0
        report += f"| {cat} | {total:,} | {kept_in_cat:,} | {rate:.1f}% |\n"

    report += f"""

## 输出文件

- `master_with_rule_filter.csv` — 全部 {N} 条 + 新增 5 列（rule_keep/rule_health_score/...）
- `rule_filter_dropped_sample.csv` — 50 条被剔除的随机样本（**人工 spot-check**）
- `rule_filter_kept_sample.csv` — 50 条保留的随机样本（**人工 spot-check**）

## 下一步建议

1. 人工抽查上述两个 sample 文件, 估算 false positive / false negative 比例
2. 如果误删率 < 5% → 直接采纳此过滤
3. 如果误删率 5-15% → 调整阈值（KEEP_THRESHOLD）或加白名单词
4. 如果误删率 > 15% → 改用 VLM 精筛

"""

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"报告: {REPORT}")

    print(f"\n=== 完成 ===")
    print(f"  保留: {n_keep:,} / {N:,} ({n_keep/N*100:.1f}%)")
    print(f"  剔除: {n_drop:,} / {N:,} ({n_drop/N*100:.1f}%)")

if __name__ == "__main__":
    main()
