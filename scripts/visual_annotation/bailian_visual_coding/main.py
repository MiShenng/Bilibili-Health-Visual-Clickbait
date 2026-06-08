from __future__ import annotations

import argparse
import base64
import concurrent.futures
import csv
import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")
TRUTHY = {"1", "true", "yes", "y", "on", "是", "真"}


@dataclass(frozen=True)
class Config:
    root_dir: Path
    api_key: str
    api_url: str
    visual_model: str
    request_timeout_seconds: int
    max_retries: int
    retry_backoff_seconds: float
    visual_concurrency: int
    visual_batch_size: int
    visual_max_image_side: int
    visual_jpeg_quality: int
    enable_thinking: bool | None
    max_completion_tokens: int | None
    master_csv: Path
    thumbnail_roots: list[Path]
    sample_size: int
    sample_strategy: str
    random_seed: int
    filter_column: str
    filter_truthy: bool
    manifest_path: Path
    output_dir: Path
    raw_dir: Path
    normalized_dir: Path
    table_dir: Path
    log_dir: Path
    visual_system_prompt: str
    overwrite_existing: bool


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    require_api_key = args.stage in {"all", "visual"}
    config = load_config(config_path, require_api_key=require_api_key)
    logger = setup_logger(config.log_dir)

    if args.stage in {"all", "prepare"}:
        prepare_manifest(config, logger)
    if args.stage in {"all", "visual"}:
        run_visual(config, logger)
    if args.stage in {"all", "export"}:
        export_table(config, logger)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="B站健康视频封面视觉点击诱饵编码")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument(
        "--stage",
        default="all",
        choices=["all", "prepare", "visual", "export"],
        help="运行阶段：prepare / visual / export / all",
    )
    return parser.parse_args()


def load_config(config_path: Path, require_api_key: bool) -> Config:
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    root_dir = config_path.parent
    load_env_file(root_dir / ".env")
    data = _expand_env(yaml.safe_load(config_path.read_text(encoding="utf-8")) or {})

    api = data.get("api", {})
    input_data = data.get("input", {})
    output_data = data.get("output", {})
    coding = data.get("coding", {})
    pipeline = data.get("pipeline", {})

    api_key = str(api.get("api_key", "")).strip()
    if not api_key or api_key.startswith("${"):
        api_key = os.getenv("DASHSCOPE_API_KEY", "").strip() or os.getenv("QWEN_API_KEY", "").strip()
    if require_api_key and not api_key:
        raise ValueError("未配置 DASHSCOPE_API_KEY。请在 .env 或环境变量中配置。")

    output_dir = _resolve_path(str(output_data.get("output_dir", "output")), root_dir)
    prompt_path = _resolve_path(str(coding.get("visual_system_prompt_path", "prompts/visual_system_prompt.txt")), root_dir)
    if not prompt_path.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompt_path}")

    cfg = Config(
        root_dir=root_dir,
        api_key=api_key,
        api_url=str(api.get("api_url", "")).strip(),
        visual_model=str(api.get("visual_model", "")).strip(),
        request_timeout_seconds=int(api.get("request_timeout_seconds", 180)),
        max_retries=int(api.get("max_retries", 4)),
        retry_backoff_seconds=float(api.get("retry_backoff_seconds", 3)),
        visual_concurrency=int(api.get("visual_concurrency", 3)),
        visual_batch_size=int(api.get("visual_batch_size", 10)),
        visual_max_image_side=int(api.get("visual_max_image_side", 960)),
        visual_jpeg_quality=int(api.get("visual_jpeg_quality", 85)),
        enable_thinking=_optional_bool(api.get("enable_thinking", False)),
        max_completion_tokens=_optional_int(api.get("max_completion_tokens")),
        master_csv=_resolve_path(str(input_data.get("master_csv")), root_dir),
        thumbnail_roots=[
            _resolve_path(str(p), root_dir)
            for p in input_data.get("thumbnail_roots", [])
        ],
        sample_size=int(input_data.get("sample_size", 5000)),
        sample_strategy=str(input_data.get("sample_strategy", "top_quality") or "top_quality").strip(),
        random_seed=int(input_data.get("random_seed", 20260527)),
        filter_column=str(input_data.get("filter_column", "") or "").strip(),
        filter_truthy=bool(input_data.get("filter_truthy", True)),
        manifest_path=_resolve_path(str(input_data.get("manifest_path", output_dir / "tables" / "bailian_sample_5000.csv")), root_dir),
        output_dir=output_dir,
        raw_dir=output_dir / "raw_api" / "visual",
        normalized_dir=output_dir / "normalized" / "visual",
        table_dir=output_dir / "tables",
        log_dir=output_dir / "logs",
        visual_system_prompt=prompt_path.read_text(encoding="utf-8").strip(),
        overwrite_existing=bool(pipeline.get("overwrite_existing", False)),
    )
    for path in [cfg.output_dir, cfg.raw_dir, cfg.normalized_dir, cfg.table_dir, cfg.log_dir]:
        path.mkdir(parents=True, exist_ok=True)
    return cfg


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return ENV_PATTERN.sub(lambda m: os.getenv(m.group(1), m.group(0)), value)
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _resolve_path(path_text: str, base_dir: Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else (base_dir / path).resolve()


def _optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y", "on"}:
        return True
    if text in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"布尔配置非法: {value}")


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    number = int(value)
    return number if number > 0 else None


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("bailian_visual_clickbait")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    log_path = log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    logger.info("日志文件: %s", log_path)
    return logger


def prepare_manifest(config: Config, logger: logging.Logger) -> None:
    rows = list(csv.DictReader(config.master_csv.open("r", encoding="utf-8-sig", newline="")))
    candidates: list[dict[str, Any]] = []
    for row in rows:
        if config.filter_column:
            value = str(row.get(config.filter_column, "")).strip().lower()
            passed = value in TRUTHY
            if config.filter_truthy and not passed:
                continue
            if not config.filter_truthy and passed:
                continue
        image_path = resolve_thumbnail(row, config)
        if not image_path:
            continue
        bvid = str(row.get("bvid", "")).strip()
        if not bvid:
            continue
        candidates.append(
            {
                "video_id": bvid,
                "title": str(row.get("title", "") or "").strip(),
                "image_path": str(image_path),
                "pic_url": str(row.get("pic_url", "") or "").strip(),
                "query": str(row.get("query", "") or "").strip(),
                "order": str(row.get("order", "") or "").strip(),
                "category": str(row.get("category", "") or row.get("tname", "") or "").strip(),
                "author": str(row.get("author", "") or "").strip(),
                "mid": str(row.get("mid", "") or "").strip(),
                "rule_keep": str(row.get("rule_keep", "") or "").strip(),
                "rule_health_score": numeric(row.get("rule_health_score")),
                "rule_white_hits": numeric(row.get("rule_white_hits")),
                "rule_black_hits": numeric(row.get("rule_black_hits")),
                "rule_cat_boost": numeric(row.get("rule_cat_boost")),
                "is_official": str(row.get("is_official", "") or "").strip(),
                "play": numeric(row.get("play")),
                "like": numeric(row.get("like")),
                "coin": numeric(row.get("coin")),
                "favorites": numeric(row.get("favorites")),
                "share": numeric(row.get("share")),
                "video_age_days": numeric(row.get("video_age_days")),
            }
        )

    if config.sample_strategy == "random":
        rng = random.Random(config.random_seed)
        rng.shuffle(candidates)
    elif config.sample_strategy == "top_quality":
        candidates.sort(key=quality_sort_key)
    else:
        raise ValueError(f"未知 sample_strategy: {config.sample_strategy}")
    sample = candidates[: config.sample_size]
    config.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(sample).to_csv(config.manifest_path, index=False, encoding="utf-8-sig")
    batch_dir = config.table_dir / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    for old in batch_dir.glob("batch_*.json"):
        old.unlink()
    for idx, batch in enumerate(chunked(sample, config.visual_batch_size), start=1):
        (batch_dir / f"batch_{idx:04d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    logger.info(
        "候选 %s 条，策略=%s，抽样 %s 条，manifest=%s，批次数=%s",
        len(candidates),
        config.sample_strategy,
        len(sample),
        config.manifest_path,
        len(list(batch_dir.glob("batch_*.json"))),
    )


def quality_sort_key(row: dict[str, Any]) -> tuple:
    # Deterministic "best first": health relevance first, then platform signal.
    official = 1 if str(row.get("is_official", "")).strip().lower() in TRUTHY else 0
    return (
        -numeric(row.get("rule_health_score")),
        -numeric(row.get("rule_white_hits")),
        numeric(row.get("rule_black_hits")),
        -numeric(row.get("rule_cat_boost")),
        -official,
        -numeric(row.get("play")),
        -numeric(row.get("like")),
        -numeric(row.get("favorites")),
        -numeric(row.get("coin")),
        str(row.get("video_id", "")),
    )


def numeric(value: Any) -> float:
    try:
        text = str(value if value is not None else "").strip()
        if not text:
            return 0.0
        return float(text)
    except Exception:
        return 0.0


def resolve_thumbnail(row: dict[str, Any], config: Config) -> Path | None:
    raw = str(row.get("thumbnail_local_path", "") or "").strip()
    probes: list[Path] = []
    if raw:
        path = Path(raw)
        probes.append(path)
        if not path.is_absolute():
            probes.append((Path.cwd() / path).resolve())
        name = path.name
        if name:
            probes.extend(root / name for root in config.thumbnail_roots)
    bvid = str(row.get("bvid", "") or "").strip()
    if bvid:
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            probes.extend(root / f"{bvid}{ext}" for root in config.thumbnail_roots)
    for probe in probes:
        if probe.exists() and probe.is_file() and not probe.name.startswith("._"):
            return probe.resolve()
    return None


def run_visual(config: Config, logger: logging.Logger) -> None:
    if not config.manifest_path.exists():
        prepare_manifest(config, logger)
    records = list(csv.DictReader(config.manifest_path.open("r", encoding="utf-8-sig", newline="")))
    pending = []
    for record in records:
        out_path = config.normalized_dir / f"{record['video_id']}.json"
        if out_path.exists() and not config.overwrite_existing:
            try:
                existing = json.loads(out_path.read_text(encoding="utf-8"))
                if existing.get("status") == "success":
                    continue
            except Exception:
                pass
        pending.append(record)
    batches = chunked(pending, config.visual_batch_size)
    logger.info(
        "待编码 %s 条，分 %s 批，batch_size=%s，concurrency=%s",
        len(pending),
        len(batches),
        config.visual_batch_size,
        config.visual_concurrency,
    )
    client = BailianClient(config, logger)
    done = 0
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.visual_concurrency) as executor:
        future_map = {executor.submit(code_batch, client, config, logger, batch): batch for batch in batches}
        for future in concurrent.futures.as_completed(future_map):
            batch = future_map[future]
            try:
                future.result()
            except Exception as exc:
                logger.error("批次失败: %s | %s", batch_desc(batch), exc)
            done += len(batch)
            render_progress(done, len(pending), started)
    if pending:
        print()
    export_table(config, logger)


def code_batch(client: "BailianClient", config: Config, logger: logging.Logger, batch: list[dict[str, Any]]) -> None:
    prepared = []
    for item in batch:
        image_path = Path(item["image_path"])
        payload = base_payload(item)
        out_path = config.normalized_dir / f"{item['video_id']}.json"
        if not image_path.exists():
            payload.update({"status": "skipped", "error": "missing_image"})
            write_json(payload, out_path)
            continue
        prepared.append((item, payload, out_path))
    if not prepared:
        return
    try:
        results, meta = client.code([item for item, _, _ in prepared])
        result_map = {str(item.get("video_id", "")).strip(): item for item in results}
        for item, payload, out_path in prepared:
            video_id = item["video_id"]
            result = result_map.get(video_id)
            if not result:
                raise ValueError(f"批量返回缺少 video_id: {video_id}")
            normalized = normalize_result(result)
            payload.update(normalized)
            payload.update(
                {
                    "status": "success",
                    "error": "",
                    "request_id": meta.get("request_id", ""),
                    "api_model": config.visual_model,
                    "response_content": meta.get("content", ""),
                    "api_raw_json_path": meta.get("raw_json_path", ""),
                    "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
            )
            write_json(payload, out_path)
        logger.info("批次成功: %s", batch_desc([item for item, _, _ in prepared]))
    except Exception as exc:
        raw_path = latest_raw_path(config.raw_dir, batch_item_id([item for item, _, _ in prepared]))
        for item, payload, out_path in prepared:
            payload.update({"status": "failed", "error": str(exc), "api_raw_json_path": str(raw_path)})
            write_json(payload, out_path)
        logger.error("批次失败: %s | %s", batch_desc([item for item, _, _ in prepared]), exc)


class BailianClient:
    def __init__(self, config: Config, logger: logging.Logger) -> None:
        try:
            import httpx
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("调用百炼前请先安装依赖：pip install -r requirements.txt") from exc
        self.config = config
        self.logger = logger
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_url,
            max_retries=0,
            http_client=httpx.Client(
                timeout=config.request_timeout_seconds,
                trust_env=False,
                follow_redirects=True,
            ),
        )

    def code(self, items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
        content: list[dict[str, Any]] = [{"type": "text", "text": build_user_prompt(items)}]
        for index, item in enumerate(items, start=1):
            content.append(
                {
                    "type": "text",
                    "text": f"第{index}张图\nvideo_id: {item['video_id']}\ntitle: {item.get('title', '')}",
                }
            )
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_to_data_url(
                            Path(item["image_path"]),
                            self.config.visual_max_image_side,
                            self.config.visual_jpeg_quality,
                        )
                    },
                }
            )
        messages = [
            {"role": "system", "content": self.config.visual_system_prompt},
            {"role": "user", "content": content},
        ]
        return self.request_json(messages, items)

    def request_json(self, messages: list[dict[str, Any]], items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
        item_id = batch_item_id(items)
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            response_json: dict[str, Any] | None = None
            try:
                kwargs: dict[str, Any] = {
                    "model": self.config.visual_model,
                    "messages": messages,
                    "temperature": 0,
                    "top_p": 0.1,
                }
                if self.config.max_completion_tokens:
                    kwargs["max_tokens"] = self.config.max_completion_tokens
                extra_body: dict[str, Any] = {}
                if self.config.enable_thinking is not None:
                    extra_body["enable_thinking"] = self.config.enable_thinking
                if extra_body:
                    kwargs["extra_body"] = extra_body
                completion = self.client.with_options(timeout=self.config.request_timeout_seconds).chat.completions.create(**kwargs)
                response_json = completion.model_dump(mode="json")
                content = extract_content(response_json)
                raw_path = save_attempt(
                    self.config.raw_dir,
                    item_id,
                    attempt,
                    {"batch_size": len(items), "video_ids": [item["video_id"] for item in items]},
                    response_json,
                    content,
                    None,
                )
                parsed = parse_json_text(content)
                return coerce_items(parsed), {
                    "request_id": str(response_json.get("id", "")),
                    "content": content,
                    "raw_json_path": str(raw_path),
                }
            except Exception as exc:
                last_error = exc
                raw_path = save_attempt(
                    self.config.raw_dir,
                    item_id,
                    attempt,
                    {"batch_size": len(items), "video_ids": [item["video_id"] for item in items]},
                    response_json,
                    extract_content(response_json) if response_json else "",
                    str(exc),
                )
                self.logger.warning(
                    "API 请求失败 | batch=%s | attempt=%s/%s | raw=%s | %s",
                    item_id,
                    attempt,
                    self.config.max_retries,
                    raw_path,
                    exc,
                )
                time.sleep(self.config.retry_backoff_seconds * attempt)
        raise RuntimeError(f"多次重试后仍失败: {item_id}") from last_error


def build_user_prompt(items: list[dict[str, Any]]) -> str:
    lines = [
        "请对下面这些 B 站视频封面逐一做视觉点击诱饵编码。",
        "请严格按输入顺序返回 JSON 数组，不要返回 markdown 代码块。",
        "数组中每个对象必须包含：video_id, topic_relevance, emotion_intensity, fear_appeal, text_overlay_intensity, visual_suspense, info_gap, thumbnail_title_representativeness, medical_authority_cue, llm_clickbait_direct, llm_clickbait_type_direct, emotion_high, fear_high, text_high, suspense_high, visual_clickbait_binary, visual_clickbait_type, confidence, note。",
        "取值范围：topic_relevance 0/1；emotion_intensity 0-3；fear_appeal 0-2；text_overlay_intensity 0-3；visual_suspense 0-2；info_gap 0-2；thumbnail_title_representativeness 0-3；medical_authority_cue 0-2；llm_clickbait_direct 0/1；llm_clickbait_type_direct 0-6；visual_clickbait_binary 0/1；visual_clickbait_type 0-5；confidence 0-1。",
        f"本批次共 {len(items)} 张图。每张图的 video_id 和 title 会紧跟在对应图片前提供。",
        "请只返回 JSON 数组。",
    ]
    return "\n".join(lines)


def normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "video_id": str(result.get("video_id", "")).strip(),
        "topic_relevance": clamp_int(result.get("topic_relevance"), 0, 1),
        "emotion_intensity": clamp_int(result.get("emotion_intensity"), 0, 3),
        "fear_appeal": clamp_int(result.get("fear_appeal"), 0, 2),
        "text_overlay_intensity": clamp_int(result.get("text_overlay_intensity"), 0, 3),
        "visual_suspense": clamp_int(result.get("visual_suspense"), 0, 2),
        "info_gap": clamp_int(result.get("info_gap"), 0, 2),
        "thumbnail_title_representativeness": clamp_int(result.get("thumbnail_title_representativeness"), 0, 3),
        "medical_authority_cue": clamp_int(result.get("medical_authority_cue"), 0, 2),
        "llm_clickbait_direct": clamp_int(result.get("llm_clickbait_direct"), 0, 1),
        "llm_clickbait_type_direct": clamp_int(result.get("llm_clickbait_type_direct"), 0, 6),
        "confidence": clamp_float(result.get("confidence"), 0.0, 1.0),
        "note": str(result.get("note", "") or "").strip()[:80],
    }
    if normalized["llm_clickbait_direct"] == 0:
        normalized["llm_clickbait_type_direct"] = 0
    elif normalized["llm_clickbait_type_direct"] == 0:
        normalized["llm_clickbait_type_direct"] = 6
    derived = derive_clickbait(
        normalized["emotion_intensity"],
        normalized["fear_appeal"],
        normalized["text_overlay_intensity"],
        normalized["visual_suspense"],
    )
    normalized.update(derived)
    return normalized


def derive_clickbait(emotion: int, fear: int, text: int, suspense: int) -> dict[str, Any]:
    emotion_high = emotion >= 2
    fear_high = fear == 2
    text_high = text >= 2
    suspense_high = suspense == 2
    highs = [emotion_high, fear_high, text_high, suspense_high]
    high_count = sum(highs)
    if high_count == 0:
        clickbait_type = 0
    elif high_count >= 2:
        clickbait_type = 5
    elif emotion_high:
        clickbait_type = 1
    elif fear_high:
        clickbait_type = 2
    elif text_high:
        clickbait_type = 3
    else:
        clickbait_type = 4
    return {
        "emotion_high": emotion_high,
        "fear_high": fear_high,
        "text_high": text_high,
        "suspense_high": suspense_high,
        "visual_clickbait_binary": 1 if high_count else 0,
        "visual_clickbait_type": clickbait_type,
    }


def export_table(config: Config, logger: logging.Logger) -> None:
    if not config.manifest_path.exists():
        logger.warning("manifest 不存在，跳过导出: %s", config.manifest_path)
        return
    records = list(csv.DictReader(config.manifest_path.open("r", encoding="utf-8-sig", newline="")))
    rows: list[dict[str, Any]] = []
    for record in records:
        norm_path = config.normalized_dir / f"{record['video_id']}.json"
        normalized = json.loads(norm_path.read_text(encoding="utf-8")) if norm_path.exists() else {}
        row = {
            **record,
            "status": normalized.get("status", "not_run"),
            "error": normalized.get("error", ""),
            "topic_relevance": normalized.get("topic_relevance", ""),
            "emotion_intensity": normalized.get("emotion_intensity", ""),
            "fear_appeal": normalized.get("fear_appeal", ""),
            "text_overlay_intensity": normalized.get("text_overlay_intensity", ""),
            "visual_suspense": normalized.get("visual_suspense", ""),
            "info_gap": normalized.get("info_gap", ""),
            "thumbnail_title_representativeness": normalized.get("thumbnail_title_representativeness", ""),
            "medical_authority_cue": normalized.get("medical_authority_cue", ""),
            "llm_clickbait_direct": normalized.get("llm_clickbait_direct", ""),
            "llm_clickbait_type_direct": normalized.get("llm_clickbait_type_direct", ""),
            "emotion_high": normalized.get("emotion_high", ""),
            "fear_high": normalized.get("fear_high", ""),
            "text_high": normalized.get("text_high", ""),
            "suspense_high": normalized.get("suspense_high", ""),
            "visual_clickbait_binary": normalized.get("visual_clickbait_binary", ""),
            "visual_clickbait_type": normalized.get("visual_clickbait_type", ""),
            "confidence": normalized.get("confidence", ""),
            "note": normalized.get("note", ""),
            "request_id": normalized.get("request_id", ""),
            "api_model": normalized.get("api_model", ""),
            "api_raw_json_path": normalized.get("api_raw_json_path", ""),
            "created_at": normalized.get("created_at", ""),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    csv_path = config.table_dir / "visual_clickbait_codes.csv"
    parquet_path = config.table_dir / "visual_clickbait_codes.parquet"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as exc:
        logger.warning("Parquet 写出失败，已保留 CSV: %s", exc)
    logger.info("编码表已导出: %s", csv_path)


def base_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "video_id": item.get("video_id", ""),
        "title": item.get("title", ""),
        "image_path": item.get("image_path", ""),
        "pic_url": item.get("pic_url", ""),
        "query": item.get("query", ""),
        "order": item.get("order", ""),
        "category": item.get("category", ""),
        "author": item.get("author", ""),
        "mid": item.get("mid", ""),
        "rule_keep": item.get("rule_keep", ""),
    }


def image_to_data_url(path: Path, max_side: int, jpeg_quality: int) -> str:
    try:
        from PIL import Image
    except Exception as exc:
        raise RuntimeError("调用百炼前请先安装 Pillow：pip install -r requirements.txt") from exc
    with Image.open(path) as image:
        working = image.convert("RGB")
        if max(working.size) > max_side:
            working.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        working.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def extract_content(response_json: dict[str, Any] | None) -> str:
    if not response_json:
        return ""
    choices = response_json.get("choices") or []
    if not choices:
        raise ValueError("API 返回缺少 choices")
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()


def parse_json_text(content: str) -> Any:
    if not content:
        raise ValueError("模型返回空内容")
    candidates = [content]
    start_array = content.find("[")
    end_array = content.rfind("]")
    if start_array != -1 and end_array > start_array:
        candidates.append(content[start_array : end_array + 1])
    start_obj = content.find("{")
    end_obj = content.rfind("}")
    if start_obj != -1 and end_obj > start_obj:
        candidates.append(content[start_obj : end_obj + 1])
    for candidate in candidates:
        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, (list, dict)):
                return loaded
        except Exception:
            pass
    try:
        from json_repair import repair_json
    except Exception as exc:
        raise RuntimeError("模型返回不是严格 JSON，且未安装 json-repair。请运行 pip install -r requirements.txt") from exc
    repaired = repair_json(content, return_objects=True)
    if not isinstance(repaired, (list, dict)):
        raise ValueError(f"无法修复为 JSON: {content[:200]}")
    return repaired


def coerce_items(parsed: Any) -> list[dict[str, Any]]:
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if isinstance(parsed, dict):
        for key in ("items", "results", "data"):
            value = parsed.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise ValueError("批量响应不是 JSON 数组。")


def save_attempt(
    raw_dir: Path,
    item_id: str,
    attempt: int,
    preview: dict[str, Any],
    response_json: dict[str, Any] | None,
    response_content: str,
    error: str | None,
) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{item_id}__attempt_{attempt:02d}.json"
    payload = {
        "item_id": item_id,
        "attempt": attempt,
        "preview": preview,
        "response_json": response_json,
        "response_content": response_content,
        "error": error,
    }
    write_json(payload, path)
    return path


def write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clamp_int(value: Any, low: int, high: int) -> int:
    try:
        number = int(float(value))
    except Exception:
        number = low
    return max(low, min(high, number))


def clamp_float(value: Any, low: float, high: float) -> float:
    try:
        number = float(value)
    except Exception:
        number = low
    return max(low, min(high, number))


def chunked(records: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    if batch_size <= 1:
        return [[record] for record in records]
    return [records[index : index + batch_size] for index in range(0, len(records), batch_size)]


def batch_item_id(items: list[dict[str, Any]]) -> str:
    if len(items) == 1:
        return str(items[0]["video_id"])
    return f"batch__{items[0]['video_id']}__{items[-1]['video_id']}"


def batch_desc(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0]["video_id"])
    return f"{items[0]['video_id']}..{items[-1]['video_id']} ({len(items)})"


def latest_raw_path(raw_dir: Path, item_id: str) -> str:
    matches = sorted(raw_dir.glob(f"{item_id}__attempt_*.json"))
    return str(matches[-1]) if matches else ""


def render_progress(done: int, total: int, started: float) -> None:
    if total <= 0:
        return
    elapsed = max(time.monotonic() - started, 0.001)
    rate = done / elapsed
    remaining = (total - done) / rate if rate > 0 else 0
    percent = done / total * 100
    print(f"\r进度 {done}/{total} ({percent:5.1f}%) | ETA {remaining/60:5.1f} min", end="", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
