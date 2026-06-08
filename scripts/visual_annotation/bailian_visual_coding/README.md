# B站健康视频封面视觉编码程序

这个程序按旧项目“程序 - 视觉编码”的方式搭建，但输入单位改为 B 站视频封面图。默认从当前项目主表中按高质量排序选前 5000 条有本地封面的记录，每批 10 张调用阿里云百炼视觉模型，输出结构化视觉点击诱饵编码。

## 目录

```text
bailian_visual_coding/
├── main.py
├── config.yaml
├── .env.example
├── requirements.txt
├── prompts/
│   └── visual_system_prompt.txt
└── output/
    ├── raw_api/visual/
    ├── normalized/visual/
    ├── tables/
    └── logs/
```

## 安装

```bash
cd scripts/visual_annotation/bailian_visual_coding
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API Key

```bash
cp .env.example .env
```

把 `.env` 里的 `DASHSCOPE_API_KEY` 填好。不要把真实 key 写进论文、日志或提交记录。

也可以不建 `.env`，直接在终端设置：

```bash
export DASHSCOPE_API_KEY="sk-..."
```

程序读取 API Key 的位置是 [config.yaml](config.yaml)：

```yaml
api:
  api_key: "${DASHSCOPE_API_KEY}"
```

不要把真实 key 直接写进 `config.yaml`，除非只是本机临时使用且不会同步出去。

## 模型选择

默认模型在 [config.yaml](config.yaml) 里调整：

```yaml
api:
  visual_model: "qwen-vl-plus-latest"
```

当前默认 `qwen-vl-plus-latest`，用于 5000 张批量视觉标注，优先考虑性价比。若小样本复核发现误差较大，可改为：

```yaml
api:
  visual_model: "qwen-vl-max-latest"
```

建议策略：全量 5000 张先用 `qwen-vl-plus-latest`，再抽 200-500 张用人工或 `qwen-vl-max-latest` 复核一致性。

## 样本选择

默认不是随机抽样，而是高质量优先：

```yaml
input:
  sample_strategy: "top_quality"
```

排序逻辑：先保留 `rule_keep=true` 且有本地封面的记录，再按 `rule_health_score`、`rule_white_hits`、`rule_black_hits`、`rule_cat_boost`、认证状态、播放量、点赞、收藏、投币等字段排序，取前 5000 条。

如果要恢复随机抽样，改为：

```yaml
input:
  sample_strategy: "random"
```

## 运行

先抽样并生成 manifest：

```bash
python main.py --config config.yaml --stage prepare
```

调用百炼视觉模型编码：

```bash
python main.py --config config.yaml --stage visual
```

只重建导出表，不请求 API：

```bash
python main.py --config config.yaml --stage export
```

全流程：

```bash
python main.py --config config.yaml --stage all
```

## 断点续跑

默认 `pipeline.overwrite_existing: false`。如果某个视频已经有 `normalized/visual/{video_id}.json` 且 `status=success`，再次运行时会跳过。

## 输出

- `output/tables/bailian_sample_5000.csv`：抽样 manifest
- `output/raw_api/visual/`：每批 API 原始返回
- `output/normalized/visual/`：每个视频的标准化 JSON
- `output/tables/visual_clickbait_codes.csv`：最终编码表
- `output/tables/visual_clickbait_codes.parquet`：Parquet 版本
