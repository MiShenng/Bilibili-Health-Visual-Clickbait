# B站健康科普视觉标题党 pilot

目标：先构建一个小型、可复核的 B站公开视频检索样本，用于后续判断“封面承诺-标题承诺-正文兑现/错配”是否可稳定编码。

## 当前脚本做什么

- 使用 B站公开视频搜索接口检索视频结果。
- 保存公开搜索结果元数据到 `data/bilibili_search_results.csv` 和 `data/bilibili_search_results.jsonl`。
- 保存每次请求的原始 JSON 到 `data/raw/`，便于复核。
- 记录 `query`、排序方式、页码、结果排名和采集时间戳。
- 对 `bvid` 和 UP 主标识生成短 hash，方便后续匿名化处理。

## 当前脚本不做什么

- 不登录。
- 不绕过验证码、付费、权限或平台访问控制。
- 不下载视频。
- 不采集私信、非公开内容或用户主页详情。
- 不把评论、弹幕、用户身份作为第一步采集对象。

## 快速试跑

在本目录运行：

```bash
python3 bilibili_search_pilot.py --queries-file queries_seed.txt --out-dir data --pages 1 --orders totalrank --sleep 2 --jitter 1
```

如果要扩大一点：

```bash
python3 bilibili_search_pilot.py --queries-file queries_seed.txt --out-dir data --pages 2 --orders totalrank pubdate click --sleep 3 --jitter 2
```

## 建议的 pilot 顺序

1. 先跑 `pages=1`，确认字段可用。
2. 手动检查 CSV 中 30-50 条视频，判断是否真的有视觉承诺错配。
3. 如果现象稳定，再扩展到 500-1500 条。
4. 后续再单独添加封面下载、字幕/ASR、评论/弹幕采集模块。

## 输出字段

- `query`: 检索词。
- `order`: 排序方式。
- `page`: 搜索页码。
- `rank`: 当前页排名。
- `video_id_hash`: 视频 ID 的短 hash。
- `bvid` / `aid`: B站视频标识。
- `title`: 视频标题。
- `author`: UP 主名。
- `mid_hash`: UP 主标识的短 hash。
- `pubdate`: 发布时间。
- `duration`: 时长。
- `play`, `favorites`, `review`, `danmaku`: 搜索结果页返回的互动指标。
- `tag`, `description`, `pic`, `arcurl`: 标签、简介、封面链接、视频链接。

## 研究边界

这个 pilot 只能支持“公开视频搜索样本”的第一步。它不能直接回答视觉标题党是否导致点击，也不能代表全平台分布。后续必须补充人工标注和正文内容兑现判断。
