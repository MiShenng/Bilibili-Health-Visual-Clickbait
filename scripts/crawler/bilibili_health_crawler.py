import requests
import time
import random
import os
import json


SEARCH_API = "https://api.bilibili.com/x/web-interface/search/type"
DETAIL_API = "https://api.bilibili.com/x/web-interface/view"
CARD_API = "https://api.bilibili.com/x/web-interface/card"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

KEYWORDS = [
    "健康科普",
    "医学科普",
    "医生提醒",
    "体检报告",
    "糖尿病",
    "减肥",
    "脱发",
    "HPV",
    "高血压",
    "癌症",
    "养生",
    "中医养生",
    "饮食健康",
]

ORDER_LABELS = {
    "totalrank": "综合",
    "pubdate": "最新",
    "click": "最多播放",
}

# 扩展预实验目标：采集 1000 条唯一公开视频。
# 大规模抓取时：
# 1. 提高 TARGET_TOTAL，例如 5000；
# 2. 提高 MAX_PAGES_PER_QUERY_ORDER；
# 3. 保留 ORDERS 的分层，不要只用单一排序，否则样本过度偏向一种平台排序逻辑。
TARGET_TOTAL = 1000
TARGET_PER_KEYWORD = 80
ORDERS = ["totalrank", "pubdate", "click"]
PAGE_SIZE = 20
MAX_PAGES_PER_QUERY_ORDER = 5

REQUEST_MIN_SLEEP = 1.5
REQUEST_MAX_SLEEP = 3.5
RETRY_TIMES = 3
RETRY_SLEEP = 5
TIMEOUT = 20

OUTPUT_DIR = "output"
THUMBNAIL_DIR = os.path.join(OUTPUT_DIR, "thumbnails")
CSV_PATH = os.path.join(OUTPUT_DIR, "bilibili_health_1000.csv")
LOG_PATH = os.path.join(OUTPUT_DIR, "crawl_log.txt")

COLUMNS = [
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


session = requests.Session()
session.headers.update(HEADERS)


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def log_message(message):
    line = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + message
    print(line)
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


def safe_ratio(numerator, denominator):
    try:
        numerator = float(numerator or 0)
        denominator = float(denominator or 0)
        if denominator <= 0:
            return 0
        return numerator / denominator
    except (TypeError, ValueError):
        return 0


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
    parts = text.split(":")
    try:
        total = 0
        for part in parts:
            total = total * 60 + int(part)
        return total
    except ValueError:
        return 0


def request_json(url, params=None):
    last_error = None
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            polite_sleep()
            response = session.get(url, params=params, timeout=TIMEOUT)
            if response.status_code == 412:
                warm_up_session()
                response = session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") not in (0, None):
                raise RuntimeError("API code={} message={}".format(payload.get("code"), payload.get("message")))
            return payload
        except Exception as exc:
            last_error = exc
            log_message("WARN request failed attempt={}/{} url={} error={}".format(attempt, RETRY_TIMES, url, repr(exc)))
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    log_message("ERROR request failed url={} error={}".format(url, repr(last_error)))
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
            log_message("WARN image failed attempt={}/{} url={} error={}".format(attempt, RETRY_TIMES, url, repr(exc)))
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP)
    log_message("ERROR image failed url={} error={}".format(url, repr(last_error)))
    return None


def warm_up_session():
    try:
        session.get("https://search.bilibili.com/video?keyword=健康科普", timeout=TIMEOUT)
    except Exception as exc:
        log_message("WARN warm_up_session failed error={}".format(repr(exc)))


def search_videos(keyword, order="totalrank", target_count=25):
    """Search Bilibili public video results for one keyword and one order mode."""
    results = []
    seen_in_query = set()

    for page in range(1, MAX_PAGES_PER_QUERY_ORDER + 1):
        if len(results) >= target_count:
            break

        params = {
            "search_type": "video",
            "keyword": keyword,
            "order": order,
            "page": page,
            "page_size": PAGE_SIZE,
        }
        payload = request_json(SEARCH_API, params=params)
        if not payload:
            log_message("ERROR search failed query={} order={} page={}".format(keyword, order, page))
            continue

        items = payload.get("data", {}).get("result", []) or []
        if not items:
            log_message("WARN empty search result query={} order={} page={}".format(keyword, order, page))
            break

        for index, item in enumerate(items, start=1):
            bvid = item.get("bvid") or ""
            aid = item.get("aid") or ""
            key = bvid or str(aid)
            if not key or key in seen_in_query:
                continue

            seen_in_query.add(key)
            rank = (page - 1) * PAGE_SIZE + index
            results.append(
                {
                    "bvid": bvid,
                    "aid": aid,
                    "title": clean_text(item.get("title")),
                    "description": clean_text(item.get("description")),
                    "tag": clean_text(item.get("tag")),
                    "pubdate": readable_time(item.get("pubdate")),
                    "duration": duration_to_seconds(item.get("duration")),
                    "category": clean_text(item.get("typename") or item.get("type")),
                    "author": clean_text(item.get("author")),
                    "mid": item.get("mid") or "",
                    "play": item.get("play") or 0,
                    "danmaku": item.get("video_review") or 0,
                    "review": item.get("review") or 0,
                    "favorites": item.get("favorites") or 0,
                    "pic_url": normalize_url(item.get("pic") or ""),
                    "query": keyword,
                    "rank": rank,
                    "order": ORDER_LABELS.get(order, order),
                    "order_api": order,
                }
            )

            if len(results) >= target_count:
                break

        log_message("OK search query={} order={} page={} collected={}".format(keyword, order, page, len(results)))

    return results


def get_video_detail(bvid):
    """Get full video detail and engagement stats from view API."""
    if not bvid:
        return {}

    payload = request_json(DETAIL_API, params={"bvid": bvid})
    if not payload:
        return {}

    data = payload.get("data", {}) or {}
    stat = data.get("stat", {}) or {}
    owner = data.get("owner", {}) or {}

    return {
        "aid": data.get("aid") or "",
        "bvid": data.get("bvid") or bvid,
        "description": clean_text(data.get("desc")),
        "pubdate": readable_time(data.get("pubdate")),
        "duration": duration_to_seconds(data.get("duration")),
        "category": clean_text(data.get("tname")),
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


def get_uploader_info(mid):
    """Get uploader follower count and official verification status."""
    if not mid:
        return {
            "follower": "",
            "is_official": False,
            "official_title": "",
        }

    payload = request_json(CARD_API, params={"mid": mid})
    if not payload:
        return {
            "follower": "",
            "is_official": False,
            "official_title": "",
        }

    data = payload.get("data", {}) or {}
    card = data.get("card", {}) or {}
    official = card.get("official_verify", {}) or {}
    official_type = official.get("type", -1)
    official_title = clean_text(official.get("desc"))

    return {
        "follower": data.get("follower") or 0,
        "is_official": official_type != -1,
        "official_title": official_title,
    }


def download_thumbnail(pic_url, bvid):
    if not pic_url or not bvid:
        return ""

    local_path = os.path.join(THUMBNAIL_DIR, "{}.jpg".format(bvid))
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path

    content = request_binary(normalize_url(pic_url))
    if not content:
        return ""

    try:
        with open(local_path, "wb") as f:
            f.write(content)
        return local_path
    except Exception as exc:
        log_message("ERROR save thumbnail bvid={} error={}".format(bvid, repr(exc)))
        return ""


def merge_record(search_item, detail, uploader):
    record = {}
    record.update(search_item)

    for key, value in detail.items():
        if value not in ("", None):
            record[key] = value

    record.update(uploader)

    play = record.get("play") or 0
    like = record.get("like") or 0
    favorites = record.get("favorites") or 0
    coin = record.get("coin") or 0
    share = record.get("share") or 0

    record["like_to_play_ratio"] = safe_ratio(like, play)
    record["fav_to_play_ratio"] = safe_ratio(favorites, play)
    record["engagement_score"] = safe_ratio(float(like or 0) + float(favorites or 0) + float(coin or 0) + float(share or 0), play)
    record["thumbnail_local_path"] = download_thumbnail(record.get("pic_url"), record.get("bvid"))

    return record


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


def write_csv(records, columns, path):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(",".join(columns) + "\n")
        for record in records:
            row = [csv_escape(record.get(column, "")) for column in columns]
            f.write(",".join(row) + "\n")


def is_non_empty(value):
    return value not in ("", None)


def print_completeness_summary(records, columns):
    if not records:
        print("No records collected.")
        return

    total = len(records)
    print("\n字段完整率统计：")
    for column in columns:
        non_empty = 0
        for record in records:
            if is_non_empty(record.get(column)):
                non_empty += 1
        rate = non_empty / total
        print("{}: {:.1%} ({}/{})".format(column, rate, non_empty, total))


def main():
    ensure_dirs()
    warm_up_session()

    records = []
    seen_bvids = set()
    uploader_cache = {}

    for keyword in KEYWORDS:
        if len(records) >= TARGET_TOTAL:
            break

        keyword_count = 0
        for order in ORDERS:
            if len(records) >= TARGET_TOTAL:
                break

            search_items = search_videos(keyword, order=order, target_count=TARGET_PER_KEYWORD)

            for item in search_items:
                if len(records) >= TARGET_TOTAL:
                    break

                bvid = item.get("bvid")
                if not bvid or bvid in seen_bvids:
                    continue

                seen_bvids.add(bvid)
                detail = get_video_detail(bvid)
                mid = detail.get("mid") or item.get("mid")
                mid_key = str(mid)
                if mid_key in uploader_cache:
                    uploader = uploader_cache[mid_key]
                else:
                    uploader = get_uploader_info(mid)
                    uploader_cache[mid_key] = uploader
                record = merge_record(item, detail, uploader)
                records.append(record)
                keyword_count += 1

                log_message(
                    "OK video query={} order={} rank={} bvid={} title={}".format(
                        item.get("query"),
                        item.get("order"),
                        item.get("rank"),
                        bvid,
                        item.get("title"),
                    )
                )

                if len(records) % 25 == 0:
                    write_csv(records, COLUMNS, CSV_PATH)
                    log_message("CHECKPOINT total_records={} csv={}".format(len(records), CSV_PATH))

                if keyword_count >= TARGET_PER_KEYWORD or len(records) >= TARGET_TOTAL:
                    break

            if keyword_count >= TARGET_PER_KEYWORD or len(records) >= TARGET_TOTAL:
                break

        log_message("DONE keyword={} collected={}".format(keyword, keyword_count))

    write_csv(records, COLUMNS, CSV_PATH)

    metadata = {
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "keywords": KEYWORDS,
        "orders": ORDERS,
        "target_total": TARGET_TOTAL,
        "target_per_keyword": TARGET_PER_KEYWORD,
        "records": len(records),
        "csv_path": CSV_PATH,
        "thumbnail_dir": THUMBNAIL_DIR,
    }
    with open(os.path.join(OUTPUT_DIR, "crawl_summary.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    log_message("FINISH total_records={} csv={}".format(len(records), CSV_PATH))
    print_completeness_summary(records, COLUMNS)


if __name__ == "__main__":
    main()
