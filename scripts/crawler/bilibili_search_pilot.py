#!/usr/bin/env python3
"""Bilibili public-search pilot collector.

This script collects public search-result metadata only. It does not log in,
does not bypass CAPTCHA or access controls, and does not download videos.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import http.cookiejar
import json
import random
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, HTTPSHandler, Request, build_opener


API_URL = "https://api.bilibili.com/x/web-interface/search/type"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


def create_ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = create_ssl_context()
COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = build_opener(HTTPCookieProcessor(COOKIE_JAR), HTTPSHandler(context=SSL_CONTEXT))

CSV_FIELDS = [
    "collected_at",
    "query",
    "order",
    "page",
    "rank",
    "video_id_hash",
    "bvid",
    "aid",
    "title",
    "author",
    "mid_hash",
    "pubdate",
    "duration",
    "play",
    "favorites",
    "review",
    "danmaku",
    "tag",
    "description",
    "pic",
    "arcurl",
]


def stable_hash(value: Any) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def clean_html(text: Any) -> str:
    if text is None:
        return ""
    return (
        str(text)
        .replace("<em class=\"keyword\">", "")
        .replace("</em>", "")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def read_queries(path: Path) -> list[str]:
    queries: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        queries.append(item)
    if not queries:
        raise ValueError(f"No queries found in {path}")
    return queries


def fetch_search(keyword: str, page: int, order: str, timeout: int) -> dict[str, Any]:
    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "order": order,
    }
    url = f"{API_URL}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Referer": "https://search.bilibili.com/",
            "Origin": "https://search.bilibili.com",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with OPENER.open(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    payload = json.loads(body)
    if payload.get("code") != 0:
        raise RuntimeError(f"Bilibili returned code={payload.get('code')}: {payload.get('message')}")
    return payload


def warm_up_session(keyword: str, timeout: int) -> None:
    params = urlencode({"keyword": keyword})
    url = f"https://search.bilibili.com/video?{params}"
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with OPENER.open(request, timeout=timeout) as response:
        response.read(1024)


def normalize_result(
    item: dict[str, Any],
    *,
    collected_at: str,
    query: str,
    order: str,
    page: int,
    rank: int,
) -> dict[str, Any]:
    bvid = item.get("bvid") or ""
    aid = item.get("aid") or ""
    mid = item.get("mid") or item.get("upic") or item.get("author") or ""
    pubdate = item.get("pubdate")
    if isinstance(pubdate, int) and pubdate > 0:
        pubdate_text = datetime.fromtimestamp(pubdate, timezone.utc).isoformat()
    else:
        pubdate_text = ""

    return {
        "collected_at": collected_at,
        "query": query,
        "order": order,
        "page": page,
        "rank": rank,
        "video_id_hash": stable_hash(bvid or aid),
        "bvid": bvid,
        "aid": aid,
        "title": clean_html(item.get("title")),
        "author": clean_html(item.get("author")),
        "mid_hash": stable_hash(mid),
        "pubdate": pubdate_text,
        "duration": item.get("duration", ""),
        "play": item.get("play", ""),
        "favorites": item.get("favorites", ""),
        "review": item.get("review", ""),
        "danmaku": item.get("video_review", ""),
        "tag": clean_html(item.get("tag")),
        "description": clean_html(item.get("description")),
        "pic": item.get("pic", ""),
        "arcurl": item.get("arcurl", ""),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def load_existing_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = row.get("bvid") or row.get("aid") or row.get("arcurl")
            if key:
                keys.add(key)
    return keys


def run(args: argparse.Namespace) -> int:
    queries = read_queries(args.queries_file)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "bilibili_search_results.csv"
    jsonl_path = out_dir / "bilibili_search_results.jsonl"
    run_log_path = out_dir / "run_log.jsonl"
    seen = load_existing_keys(csv_path)
    total_written = 0

    try:
        warm_up_session(queries[0], args.timeout)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"[warn] session warm-up failed: {exc}", file=sys.stderr)

    for query in queries:
        for order in args.orders:
            for page in range(1, args.pages + 1):
                collected_at = datetime.now(timezone.utc).isoformat()
                log_row: dict[str, Any] = {
                    "collected_at": collected_at,
                    "query": query,
                    "order": order,
                    "page": page,
                    "status": "started",
                }
                try:
                    payload = fetch_search(query, page, order, args.timeout)
                    raw_path = raw_dir / f"{stable_hash(query)}_{order}_p{page}.json"
                    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                    results = payload.get("data", {}).get("result") or []
                    rows: list[dict[str, Any]] = []
                    for rank, item in enumerate(results, start=1):
                        row = normalize_result(
                            item,
                            collected_at=collected_at,
                            query=query,
                            order=order,
                            page=page,
                            rank=rank,
                        )
                        key = row["bvid"] or row["aid"] or row["arcurl"]
                        if not key or key in seen:
                            continue
                        seen.add(key)
                        rows.append(row)

                    append_csv(csv_path, rows)
                    write_jsonl(jsonl_path, rows)
                    total_written += len(rows)
                    log_row.update({"status": "ok", "result_count": len(results), "new_rows": len(rows)})
                except (HTTPError, URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
                    log_row.update({"status": "error", "error": repr(exc)})
                    print(f"[warn] {query} order={order} page={page}: {exc}", file=sys.stderr)
                finally:
                    write_jsonl(run_log_path, [log_row])
                    sleep_for = args.sleep + random.uniform(0, args.jitter)
                    time.sleep(sleep_for)

    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "queries": len(queries),
        "orders": args.orders,
        "pages": args.pages,
        "total_unique_rows_written": total_written,
        "csv": str(csv_path),
        "jsonl": str(jsonl_path),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect public Bilibili video search metadata for a pilot sample.")
    parser.add_argument("--queries-file", type=Path, default=Path("queries_seed.txt"))
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    parser.add_argument("--pages", type=int, default=1, help="Pages per query/order.")
    parser.add_argument(
        "--orders",
        nargs="+",
        default=["totalrank"],
        choices=["totalrank", "click", "pubdate", "dm", "stow"],
        help="Bilibili search order modes.",
    )
    parser.add_argument("--sleep", type=float, default=2.0, help="Base delay between requests.")
    parser.add_argument("--jitter", type=float, default=1.0, help="Random extra delay between requests.")
    parser.add_argument("--timeout", type=int, default=20)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(run(parse_args(sys.argv[1:])))
