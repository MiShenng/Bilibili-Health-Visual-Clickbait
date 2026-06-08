import csv
import json
import os
import random
import time
from collections import deque
from pathlib import Path

import requests


DETAIL_API = "https://api.bilibili.com/x/web-interface/view"
CARD_API = "https://api.bilibili.com/x/web-interface/card"
RELATED_API = "https://api.bilibili.com/x/web-interface/archive/related"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

TARGET_TOTAL = 1000
OUTPUT_DIR = Path("output")
THUMBNAIL_DIR = OUTPUT_DIR / "thumbnails"
BASE_CSV = OUTPUT_DIR / "bilibili_health_500.csv"
PILOT_CSV = Path("data/bilibili_search_results.csv")
RAW_DIR = Path("data/raw")
OUT_CSV = OUTPUT_DIR / "bilibili_health_related_1000.csv"
SUMMARY_PATH = OUTPUT_DIR / "related_expand_summary.json"
LOG_PATH = OUTPUT_DIR / "related_expand_1000.log"

REQUEST_MIN_SLEEP = 1.2
REQUEST_MAX_SLEEP = 2.8
RETRY_TIMES = 3
RETRY_SLEEP = 5
TIMEOUT = 20

BASE_COLUMNS = [
    "bvid",
    "aid",
    "title",
    "description",
    "tag",
    "pubdate",
    "duration",
    "category",
    "author",
    "mid",
    "follower",
    "is_official",
    "official_title",
    "play",
    "danmaku",
    "review",
    "favorites",
    "coin",
    "share",
    "like",
    "like_to_play_ratio",
    "fav_to_play_ratio",
    "engagement_score",
    "pic_url",
    "thumbnail_local_path",
    "query",
    "rank",
    "order",
    "order_api",
]

EXTRA_COLUMNS = [
    "sample_source",
    "seed_bvid",
    "seed_query",
    "source_depth",
    "passes_health_heuristic",
]

HEALTH_TERMS = [
    "健康",
    "医学",
    "医疗",
    "医生",
    "科普",
    "体检",
    "疾病",
    "症状",
    "治疗",
    "用药",
    "药",
    "医院",
    "糖尿病",
    "高血压",
    "癌症",
    "HPV",
    "脱发",
    "减肥",
    "营养",
    "饮食",
    "养生",
    "心理",
    "睡眠",
    "疫苗",
    "病毒",
    "感染",
    "血压",
    "血糖",
]


session = requests.Session()
session.headers.update(HEADERS)


def log(message):
    line = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + message
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def polite_sleep():
    time.sleep(random.uniform(REQUEST_MIN_SLEEP, REQUEST_MAX_SLEEP))


def clean_text(value):
    if value is None:
        return ""
    return (
        str(value)
        .replace('<em class="keyword">', "")
        .replace("</em>", "")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def normalize_url(url):
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    return url


def readable_time(timestamp):
    try:
        timestamp = int(timestamp)
        if timestamp <= 0:
            return ""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    except (TypeError, ValueError):
        return ""


def duration_to_seconds(value):
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if text.isdigit():
        return int(text)
    total = 0
    try:
        for part in text.split(":"):
            total = total * 60 + int(part)
        return total
    except ValueError:
        return 0


def safe_ratio(numerator, denominator):
    try:
        numerator = float(numerator or 0)
        denominator = float(denominator or 0)
        if denominator <= 0:
            return 0
        return numerator / denominator
    except (TypeError, ValueError):
        return 0


def request_json(url, params=None):
    last_error = None
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            polite_sleep()
            response = session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") not in (0, None):
                raise RuntimeError("API code={} message={}".format(payload.get("code"), payload.get("message")))
            return payload
        except Exception as exc:
            last_error = exc
            log("WARN request failed attempt={}/{} url={} error={}".format(attempt, RETRY_TIMES, url, repr(exc)))
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    log("ERROR request failed url={} error={}".format(url, repr(last_error)))
    return None


def request_binary(url):
    last_error = None
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            polite_sleep()
            response = session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_error = exc
            log("WARN image failed attempt={}/{} url={} error={}".format(attempt, RETRY_TIMES, url, repr(exc)))
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    log("ERROR image failed url={} error={}".format(url, repr(last_error)))
    return None


def get_video_detail(bvid):
    payload = request_json(DETAIL_API, params={"bvid": bvid})
    if not payload:
        return {}
    data = payload.get("data", {}) or {}
    stat = data.get("stat", {}) or {}
    owner = data.get("owner", {}) or {}
    return {
        "aid": data.get("aid") or "",
        "bvid": data.get("bvid") or bvid,
        "title": clean_text(data.get("title")),
        "description": clean_text(data.get("desc")),
        "tag": "",
        "pubdate": readable_time(data.get("pubdate")),
        "duration": duration_to_seconds(data.get("duration")),
        "category": clean_text(data.get("tname") or data.get("tname_v2")),
        "pic_url": normalize_url(data.get("pic") or ""),
        "author": clean_text(owner.get("name")),
        "mid": owner.get("mid") or "",
        "play": stat.get("view") or 0,
        "danmaku": stat.get("danmaku") or 0,
        "review": stat.get("reply") or 0,
        "favorites": stat.get("favorite") or 0,
        "coin": stat.get("coin") or 0,
        "share": stat.get("share") or 0,
        "like": stat.get("like") or 0,
    }


def get_uploader_info(mid, cache):
    if not mid:
        return {"follower": "", "is_official": False, "official_title": ""}
    key = str(mid)
    if key in cache:
        return cache[key]
    payload = request_json(CARD_API, params={"mid": mid})
    if not payload:
        info = {"follower": "", "is_official": False, "official_title": ""}
        cache[key] = info
        return info
    data = payload.get("data", {}) or {}
    card = data.get("card", {}) or {}
    official = card.get("official_verify", {}) or {}
    info = {
        "follower": data.get("follower") or 0,
        "is_official": (official.get("type", -1) != -1),
        "official_title": clean_text(official.get("desc")),
    }
    cache[key] = info
    return info


def download_thumbnail(pic_url, bvid):
    if not pic_url or not bvid:
        return ""
    local_path = THUMBNAIL_DIR / "{}.jpg".format(bvid)
    if local_path.exists() and local_path.stat().st_size > 0:
        return str(local_path)
    content = request_binary(normalize_url(pic_url))
    if not content:
        return ""
    try:
        local_path.write_bytes(content)
        return str(local_path)
    except Exception as exc:
        log("ERROR save thumbnail bvid={} error={}".format(bvid, repr(exc)))
        return ""


def passes_health_heuristic(record):
    text = " ".join(
        [
            clean_text(record.get("title")),
            clean_text(record.get("description")),
            clean_text(record.get("tag")),
            clean_text(record.get("category")),
            clean_text(record.get("query")),
        ]
    )
    return any(term in text for term in HEALTH_TERMS)


def finalize_record(record, uploader_cache):
    if record.get("sample_source") == "search_full_500":
        merged = {column: "" for column in BASE_COLUMNS + EXTRA_COLUMNS}
        merged.update(record)
        merged["passes_health_heuristic"] = "TRUE" if passes_health_heuristic(merged) else "FALSE"
        return merged

    detail = get_video_detail(record["bvid"])
    if not detail:
        return None
    merged = {column: "" for column in BASE_COLUMNS + EXTRA_COLUMNS}
    merged.update(record)
    merged.update({k: v for k, v in detail.items() if v not in ("", None)})
    merged.update(get_uploader_info(merged.get("mid"), uploader_cache))
    play = merged.get("play") or 0
    like = merged.get("like") or 0
    favorites = merged.get("favorites") or 0
    coin = merged.get("coin") or 0
    share = merged.get("share") or 0
    merged["like_to_play_ratio"] = safe_ratio(like, play)
    merged["fav_to_play_ratio"] = safe_ratio(favorites, play)
    merged["engagement_score"] = safe_ratio(float(like or 0) + float(favorites or 0) + float(coin or 0) + float(share or 0), play)
    merged["thumbnail_local_path"] = download_thumbnail(merged.get("pic_url"), merged.get("bvid"))
    merged["passes_health_heuristic"] = "TRUE" if passes_health_heuristic(merged) else "FALSE"
    return merged


def csv_escape(value):
    if value is None:
        text = ""
    elif isinstance(value, bool):
        text = "TRUE" if value else "FALSE"
    else:
        text = str(value)
    text = text.replace("\r", " ").replace("\n", " ")
    if "," in text or '"' in text:
        text = '"' + text.replace('"', '""') + '"'
    return text


def write_csv(records):
    columns = BASE_COLUMNS + EXTRA_COLUMNS
    with open(OUT_CSV, "w", encoding="utf-8-sig") as f:
        f.write(",".join(columns) + "\n")
        for record in records:
            f.write(",".join(csv_escape(record.get(column, "")) for column in columns) + "\n")


def add_candidate(candidates, bvid, sample_source, seed_bvid="", seed_query="", source_depth=0, **fields):
    if not bvid or bvid in candidates:
        return
    record = {column: "" for column in BASE_COLUMNS + EXTRA_COLUMNS}
    record.update(fields)
    record.update(
        {
            "bvid": bvid,
            "sample_source": sample_source,
            "seed_bvid": seed_bvid,
            "seed_query": seed_query,
            "source_depth": source_depth,
        }
    )
    candidates[bvid] = record


def load_candidates():
    candidates = {}
    if BASE_CSV.exists():
        for row in csv.DictReader(open(BASE_CSV, encoding="utf-8-sig")):
            bvid = row.get("bvid")
            fields = dict(row)
            fields.pop("bvid", None)
            add_candidate(candidates, bvid, "search_full_500", **fields)
    if PILOT_CSV.exists():
        for row in csv.DictReader(open(PILOT_CSV, encoding="utf-8-sig")):
            add_candidate(
                candidates,
                row.get("bvid"),
                "search_pilot_local",
                title=clean_text(row.get("title")),
                description=clean_text(row.get("description")),
                tag=clean_text(row.get("tag")),
                pubdate=row.get("pubdate", ""),
                duration=row.get("duration", ""),
                author=clean_text(row.get("author")),
                play=row.get("play", ""),
                favorites=row.get("favorites", ""),
                review=row.get("review", ""),
                danmaku=row.get("danmaku", ""),
                pic_url=normalize_url(row.get("pic")),
                query=row.get("query", ""),
                rank=row.get("rank", ""),
                order=row.get("order", ""),
                order_api=row.get("order", ""),
            )
    for path in RAW_DIR.glob("*.json"):
        if path.name.startswith("._"):
            continue
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for item in ((payload.get("data") or {}).get("result") or []):
            bvid = item.get("bvid")
            add_candidate(
                candidates,
                bvid,
                "search_raw_local",
                title=clean_text(item.get("title")),
                description=clean_text(item.get("description")),
                tag=clean_text(item.get("tag")),
                pubdate=readable_time(item.get("pubdate")),
                duration=duration_to_seconds(item.get("duration")),
                category=clean_text(item.get("typename") or item.get("type")),
                author=clean_text(item.get("author")),
                mid=item.get("mid") or "",
                play=item.get("play") or 0,
                favorites=item.get("favorites") or 0,
                review=item.get("review") or 0,
                danmaku=item.get("video_review") or 0,
                pic_url=normalize_url(item.get("pic") or ""),
                rank=item.get("rank_offset") or "",
                order_api="totalrank",
                order="综合",
            )
    return candidates


def related_items(seed_bvid):
    payload = request_json(RELATED_API, params={"bvid": seed_bvid})
    if not payload:
        return []
    return payload.get("data") or []


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    THUMBNAIL_DIR.mkdir(exist_ok=True)
    candidates = load_candidates()
    uploader_cache = {}
    records = []
    seen = set()
    frontier = deque(candidates.keys())
    expanded = set()

    log("START target={} local_candidates={}".format(TARGET_TOTAL, len(candidates)))

    while frontier and len(records) < TARGET_TOTAL:
        bvid = frontier.popleft()
        if bvid in seen:
            continue
        candidate = candidates.get(bvid, {"bvid": bvid, "sample_source": "related_discovered"})
        record = finalize_record(candidate, uploader_cache)
        if not record:
            continue
        records.append(record)
        seen.add(bvid)

        if len(records) % 25 == 0:
            write_csv(records)
            log("CHECKPOINT records={} csv={}".format(len(records), OUT_CSV))

        if bvid in expanded:
            continue
        expanded.add(bvid)
        seed_query = record.get("query") or record.get("seed_query") or ""
        source_depth = int(record.get("source_depth") or 0)
        for item in related_items(bvid):
            related_bvid = item.get("bvid")
            if not related_bvid or related_bvid in seen or related_bvid in candidates:
                continue
            add_candidate(
                candidates,
                related_bvid,
                "related_depth_{}".format(source_depth + 1),
                seed_bvid=bvid,
                seed_query=seed_query,
                source_depth=source_depth + 1,
                title=clean_text(item.get("title")),
                description=clean_text(item.get("desc")),
                pubdate=readable_time(item.get("pubdate")),
                duration=duration_to_seconds(item.get("duration")),
                category=clean_text(item.get("tname") or item.get("tname_v2")),
                author=clean_text((item.get("owner") or {}).get("name")),
                mid=(item.get("owner") or {}).get("mid") or "",
                pic_url=normalize_url(item.get("pic") or ""),
            )
            frontier.append(related_bvid)

    write_csv(records)
    summary = {
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "target_total": TARGET_TOTAL,
        "records": len(records),
        "unique_bvid": len(seen),
        "local_candidates_initial": len(load_candidates()),
        "sample_definition": "500 full search records plus local search/raw seeds, expanded through Bilibili public related-video endpoint.",
        "csv_path": str(OUT_CSV),
        "thumbnail_dir": str(THUMBNAIL_DIR),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    log("FINISH records={} csv={}".format(len(records), OUT_CSV))


if __name__ == "__main__":
    main()
