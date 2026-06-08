"""
bilibili_health_3000.py
目标：采集 3000 条去重唯一健康科普视频，跳过已有 bvid。
策略：
  - 关键词覆盖14类健康主题，每类用 totalrank / pubdate / click 三种排序
  - 每 (keyword, order) 最多爬 15 页，每页 20 条
  - 全局去重（含已有数据）
  - 每爬 50 条自动存盘
  - 封面图本地保存到 thumbnails_3000/
"""

import requests
import time
import random
import os
import json
import csv
import http.cookiejar
import ssl

# ── API ──────────────────────────────────────────────────────────────────────
SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"
DETAIL_API  = "https://api.bilibili.com/x/web-interface/view"
CARD_API    = "https://api.bilibili.com/x/web-interface/card"

# Referer 必须用 search.bilibili.com，否则搜索接口返回 HTML 而非 JSON
HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer":         "https://search.bilibili.com/",
    "Origin":          "https://search.bilibili.com",
    "Accept":          "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ── 关键词（60 大健康科普主题词，去除中医，聚焦循证健康内容） ────────────────
KEYWORDS = [
    # ───── 原 28 词（保留, 已爬过的会被 dedup 自动跳过）─────
    "健康科普", "医学科普", "医生提醒", "体检报告", "养生科普", "饮食健康",
    "糖尿病 科普", "高血压 科普", "心脏病 科普", "脂肪肝 科普",
    "糖尿病", "高血压", "高血压 危险信号",
    "癌症 早期信号", "HPV 疫苗", "肺癌 科普", "HPV",
    "减肥 科学", "脱发 医生", "睡眠 健康", "减肥", "脱发",
    "医生提醒 千万别", "医生终于说了", "体检报告 异常", "这个习惯 致癌",
    "健康科普 千万别吃", "医生提醒 致癌",

    # ───── 新 32 词（v10k 扩展, 全部聚焦循证健康科普）─────
    # 新增慢性病
    "胃病 科普", "肾病 科普", "甲状腺 科普", "痛风 科普",
    "颈椎病 科普", "腰椎间盘突出", "骨质疏松 科普",
    # 新增肿瘤/筛查
    "乳腺癌 早期", "胃癌 早期信号", "结直肠癌 筛查", "肝癌 预防",
    # 预防医学
    "疫苗 科普", "免疫力", "感冒 流感",
    # 心血管/卒中急救
    "心梗 急救", "脑梗 预防", "心律失常 科普",
    # 营养/代谢
    "蛋白质 摄入", "维生素 补充", "膳食纤维",
    # 妇幼健康
    "孕期健康", "儿童身高",
    # 心理健康/睡眠
    "焦虑 抑郁 科普", "失眠 治疗", "压力 健康",
    # 老年健康
    "老年痴呆 预防", "阿尔茨海默",
    # 用药安全
    "用药 安全", "副作用",
    # 新增 clickbait 句式（健康语境）
    "身体 发出 信号", "千万 不要忽视", "这些 症状 警惕",
]

ORDERS         = ["totalrank", "pubdate", "click"]
PAGE_SIZE      = 20
MAX_PAGES      = 15          # 每 (keyword, order) 最多爬15页

TARGET_TOTAL   = 4500        # 已经在 part1 里有 1500，这次再要 4500 → 总 6000 新增 ≈ 10k 总样本
TARGET_PER_KO  = 100         # 每 (keyword, order) 最多贡献100条（60→100, 新词命中率较低）

REQUEST_MIN_SLEEP = 0.8
REQUEST_MAX_SLEEP = 1.8
RETRY_TIMES   = 3
RETRY_SLEEP   = 6
TIMEOUT       = 20

# ── 路径 ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR     = os.path.join(SCRIPT_DIR, "output")
THUMBNAIL_DIR  = os.path.join(OUTPUT_DIR, "thumbnails")      # 复用统一文件夹
CSV_PATH       = os.path.join(OUTPUT_DIR, "bilibili_health_10k.csv")
LOG_PATH       = os.path.join(OUTPUT_DIR, "crawl_10k.log")

# 已有数据（用于全局去重）— 所有现有 5 个 CSV 都加入（+10k_part1 新增）
EXISTING_CSVS  = [
    os.path.join(OUTPUT_DIR, "bilibili_health_500.csv"),
    os.path.join(OUTPUT_DIR, "bilibili_health_related_1000.csv"),
    os.path.join(OUTPUT_DIR, "bilibili_health_3000_part1.csv"),
    os.path.join(OUTPUT_DIR, "bilibili_health_3000.csv"),
    os.path.join(OUTPUT_DIR, "bilibili_health_10k_part1.csv"),  # 第一次 10k 跑挂前的 1500 条
]

COLUMNS = [
    "bvid","aid","title","description","tag","pubdate","duration",
    "category","tid","copyright",
    "author","mid","follower","is_official","official_title",
    "uploader_level","uploader_sign",
    "play","danmaku","review","favorites","coin","share","like",
    "like_to_play_ratio","fav_to_play_ratio","engagement_score",
    "pic_url","thumbnail_local_path","query","rank","order","order_api",
    "crawl_timestamp","video_age_days",
]

ORDER_LABELS = {"totalrank":"综合","pubdate":"最新","click":"最多播放"}

# ── Session ──────────────────────────────────────────────────────────────────
session = requests.Session()
session.headers.update(HEADERS)


# ── 工具函数 ─────────────────────────────────────────────────────────────────
def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def polite_sleep():
    time.sleep(random.uniform(REQUEST_MIN_SLEEP, REQUEST_MAX_SLEEP))


def clean(v):
    if v is None:
        return ""
    return (str(v)
            .replace('<em class="keyword">', "")
            .replace("</em>", "")
            .replace("&quot;", '"')
            .replace("&amp;", "&")
            .replace("\n", " ").replace("\r", " ").strip())


def norm_url(url):
    if not url:
        return ""
    return ("https:" + url) if url.startswith("//") else url


def safe_ratio(n, d):
    try:
        n, d = float(n or 0), float(d or 0)
        return n / d if d > 0 else 0
    except Exception:
        return 0


def readable_time(ts):
    try:
        ts = int(ts)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts > 0 else ""
    except Exception:
        return ""


def dur_secs(v):
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    s = str(v).strip()
    if s.isdigit():
        return int(s)
    try:
        total = 0
        for p in s.split(":"):
            total = total * 60 + int(p)
        return total
    except Exception:
        return 0


def request_json(url, params=None):
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            polite_sleep()
            r = session.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 412:
                warm_up()
                r = session.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if data.get("code") not in (0, None):
                raise RuntimeError(f"API code={data.get('code')} msg={data.get('message')}")
            return data
        except Exception as e:
            log(f"WARN attempt={attempt}/{RETRY_TIMES} url={url} err={e}")
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    log(f"ERROR failed url={url}")
    return None


def request_binary(url):
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            polite_sleep()
            r = session.get(norm_url(url), timeout=TIMEOUT)
            r.raise_for_status()
            return r.content
        except Exception as e:
            log(f"WARN img attempt={attempt}/{RETRY_TIMES} url={url} err={e}")
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    return None


def warm_up():
    """访问搜索页面让 requests Session 获取必要的 Cookie（buvid3 等）。"""
    try:
        session.get(
            "https://search.bilibili.com/video?keyword=健康科普",
            headers={
                "User-Agent": HEADERS["User-Agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            timeout=TIMEOUT,
        )
        time.sleep(random.uniform(1.0, 2.0))
    except Exception as e:
        log(f"WARN warm_up failed: {e}")


def load_existing_bvids():
    seen = set()
    for path in EXISTING_CSVS:
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    bv = row.get("bvid", "").strip()
                    if bv:
                        seen.add(bv)
        except Exception as e:
            log(f"WARN load existing {path}: {e}")
    log(f"INFO loaded {len(seen)} existing bvids to skip")
    return seen


# ── 核心抓取 ─────────────────────────────────────────────────────────────────
def search_videos(keyword, order, target_count):
    results, seen_local = [], set()
    for page in range(1, MAX_PAGES + 1):
        if len(results) >= target_count:
            break
        params = {
            "search_type": "video",
            "keyword":     keyword,
            "order":       order,
            "page":        page,
            "page_size":   PAGE_SIZE,
        }
        payload = request_json(SEARCH_API, params=params)
        if not payload:
            break
        items = payload.get("data", {}).get("result", []) or []
        if not items:
            break

        for idx, item in enumerate(items, start=1):
            bvid = item.get("bvid") or ""
            aid  = item.get("aid")  or ""
            key  = bvid or str(aid)
            if not key or key in seen_local:
                continue
            seen_local.add(key)
            rank = (page - 1) * PAGE_SIZE + idx
            results.append({
                "bvid":        bvid,
                "aid":         aid,
                "title":       clean(item.get("title")),
                "description": clean(item.get("description")),
                "tag":         clean(item.get("tag")),
                "pubdate":     readable_time(item.get("pubdate")),
                "duration":    dur_secs(item.get("duration")),
                "category":    clean(item.get("typename") or item.get("type")),
                "author":      clean(item.get("author")),
                "mid":         item.get("mid") or "",
                "play":        item.get("play") or 0,
                "danmaku":     item.get("video_review") or 0,
                "review":      item.get("review") or 0,
                "favorites":   item.get("favorites") or 0,
                "pic_url":     norm_url(item.get("pic") or ""),
                "query":       keyword,
                "rank":        rank,
                "order":       ORDER_LABELS.get(order, order),
                "order_api":   order,
            })
            if len(results) >= target_count:
                break

        log(f"OK search q={keyword} ord={order} pg={page} so_far={len(results)}")

    return results


def get_detail(bvid):
    payload = request_json(DETAIL_API, params={"bvid": bvid})
    if not payload:
        return {}
    data = payload.get("data", {}) or {}
    stat  = data.get("stat", {})  or {}
    owner = data.get("owner", {}) or {}
    return {
        "aid":         data.get("aid") or "",
        "bvid":        data.get("bvid") or bvid,
        "description": clean(data.get("desc")),
        "pubdate":     readable_time(data.get("pubdate")),
        "pubdate_ts":  data.get("pubdate") or 0,
        "duration":    dur_secs(data.get("duration")),
        "category":    clean(data.get("tname")),
        "tid":         data.get("tid") or "",
        "copyright":   data.get("copyright") or "",
        "pic_url":     norm_url(data.get("pic") or ""),
        "author":      clean(owner.get("name")),
        "mid":         owner.get("mid") or "",
        "play":        stat.get("view")     or 0,
        "danmaku":     stat.get("danmaku")  or 0,
        "review":      stat.get("reply")    or 0,
        "favorites":   stat.get("favorite") or 0,
        "coin":        stat.get("coin")     or 0,
        "share":       stat.get("share")    or 0,
        "like":        stat.get("like")     or 0,
    }


def get_uploader(mid):
    empty = {"follower": "", "is_official": False, "official_title": "",
             "uploader_level": "", "uploader_sign": ""}
    if not mid:
        return empty
    payload = request_json(CARD_API, params={"mid": mid})
    if not payload:
        return empty
    data    = payload.get("data", {}) or {}
    card    = data.get("card", {}) or {}
    offic   = card.get("official_verify", {}) or {}
    otype   = offic.get("type", -1)
    lvl_inf = card.get("level_info", {}) or {}
    return {
        "follower":       data.get("follower") or 0,
        "is_official":    otype != -1,
        "official_title": clean(offic.get("desc")),
        "uploader_level": lvl_inf.get("current_level") if lvl_inf.get("current_level") is not None else card.get("level", ""),
        "uploader_sign":  clean(card.get("sign")),
    }


def download_thumb(pic_url, bvid):
    if not pic_url or not bvid:
        return ""
    path = os.path.join(THUMBNAIL_DIR, f"{bvid}.jpg")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    content = request_binary(pic_url)
    if not content:
        return ""
    try:
        with open(path, "wb") as f:
            f.write(content)
        return path
    except Exception as e:
        log(f"ERROR save thumb bvid={bvid} err={e}")
        return ""


def merge(search_item, detail, uploader):
    rec = dict(search_item)
    for k, v in detail.items():
        if v not in ("", None):
            rec[k] = v
    rec.update(uploader)
    play = rec.get("play") or 0
    like = rec.get("like") or 0
    fav  = rec.get("favorites") or 0
    coin = rec.get("coin") or 0
    shr  = rec.get("share") or 0
    rec["like_to_play_ratio"] = safe_ratio(like, play)
    rec["fav_to_play_ratio"]  = safe_ratio(fav, play)
    rec["engagement_score"]   = safe_ratio(like + fav + coin + shr, play)
    rec["thumbnail_local_path"] = download_thumb(rec.get("pic_url", ""), rec.get("bvid", ""))

    now_ts = int(time.time())
    rec["crawl_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_ts))
    pub_ts = detail.get("pubdate_ts") or 0
    try:
        pub_ts = int(pub_ts)
    except Exception:
        pub_ts = 0
    rec["video_age_days"] = round((now_ts - pub_ts) / 86400, 2) if pub_ts > 0 else ""
    return rec


def csv_esc(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    s = str(v).replace("\r", " ").replace("\n", " ")
    if "," in s or '"' in s:
        s = '"' + s.replace('"', '""') + '"'
    return s


def write_csv(records):
    with open(CSV_PATH, "w", encoding="utf-8-sig") as f:
        f.write(",".join(COLUMNS) + "\n")
        for rec in records:
            f.write(",".join(csv_esc(rec.get(c, "")) for c in COLUMNS) + "\n")


# ── 主流程 ───────────────────────────────────────────────────────────────────
def main():
    ensure_dirs()
    warm_up()

    # 加载已有bvid用于去重
    existing_bvids = load_existing_bvids()
    seen_bvids     = set(existing_bvids)   # 全局去重集合（含本次新采）
    uploader_cache = {}
    records        = []

    log(f"START target_new={TARGET_TOTAL} keywords={len(KEYWORDS)} orders={ORDERS}")

    for keyword in KEYWORDS:
        if len(records) >= TARGET_TOTAL:
            break

        for order in ORDERS:
            if len(records) >= TARGET_TOTAL:
                break

            search_items = search_videos(keyword, order, target_count=TARGET_PER_KO * 3)
            ko_count = 0

            for item in search_items:
                if len(records) >= TARGET_TOTAL or ko_count >= TARGET_PER_KO:
                    break

                bvid = item.get("bvid", "")
                if not bvid or bvid in seen_bvids:
                    continue

                seen_bvids.add(bvid)

                detail   = get_detail(bvid)
                mid      = str(detail.get("mid") or item.get("mid") or "")
                uploader = uploader_cache.get(mid) or get_uploader(mid)
                if mid:
                    uploader_cache[mid] = uploader

                rec = merge(item, detail, uploader)
                records.append(rec)
                ko_count += 1

                log(f"OK #{len(records)} q={keyword} ord={order} bvid={bvid} "
                    f"title={item.get('title','')[:30]}")

                if len(records) % 50 == 0:
                    write_csv(records)
                    log(f"CHECKPOINT saved {len(records)} rows → {CSV_PATH}")

            log(f"DONE q={keyword} ord={order} new_this_combo={ko_count} total={len(records)}")

    write_csv(records)

    summary = {
        "finished_at":    time.strftime("%Y-%m-%d %H:%M:%S"),
        "keywords":       KEYWORDS,
        "orders":         ORDERS,
        "target_total":   TARGET_TOTAL,
        "new_records":    len(records),
        "csv_path":       CSV_PATH,
        "thumbnail_dir":  THUMBNAIL_DIR,
        "skipped_existing": len(existing_bvids),
    }
    with open(os.path.join(OUTPUT_DIR, "crawl_3000_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    log(f"FINISH new_records={len(records)} csv={CSV_PATH}")

    # 字段完整率
    print("\n字段完整率：")
    for col in COLUMNS:
        n = sum(1 for r in records if r.get(col) not in ("", None))
        print(f"  {col}: {n/len(records):.1%}" if records else f"  {col}: N/A")


if __name__ == "__main__":
    main()
