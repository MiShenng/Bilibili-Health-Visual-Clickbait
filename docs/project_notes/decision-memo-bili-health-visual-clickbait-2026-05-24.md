# 决策备忘录：B站健康科普视频视觉标题党研究

*日期：2026-05-24*  
*用途：在进入 `/scholar-design` 前，集中列出需要拍板的关键问题、取舍理由和推荐路径。*

---

## 0. 当前状态

你现在已经完成了三个前置工作：

| 已完成内容 | 文件 |
|---|---|
| 选题 brainstorm | `output/bilibili-health-visual-clickbait/scholar-brainstorm-bilibili-health-visual-clickbait-2026-05-24.md` |
| 假设检验式中文综述 | `output/lit-review/scholar-lit-review-bili-health-visual-clickbait-hypothesis-style-CHINESE-2026-05-24.md` |
| scholar-idea 深化 | `output/scholar-idea-bili-health-visual-clickbait-engagement.md` |

已有共识非常明确：

> 主线应收束到：B站健康科普视频中的视觉标题党是否提高低成本注意力，但不能同等转化为高成本认可；缩略图-标题代表性是否调节这种分化。

英文主问题：

> Among health-science videos on Bilibili, do visual clickbait cues produce divergent engagement signatures — boosting low-cost attention but yielding diminishing returns for high-cost endorsement — and does thumbnail-title representativeness moderate this bifurcation?

中文主问题：

> B站健康科普视频中，视觉标题党是否会提高低成本注意力（播放、点赞），但不能同等转化为高成本认可（投币、收藏、分享）；缩略图-标题代表性是否会调节这种分化？

---

## 1. 现在真正要决策的事情

你现在不是在决定“这个选题能不能做”。这个问题已经基本回答：**能做，而且有明确缺口**。

你现在需要决策的是：

1. 第一篇论文的主线到底是什么。
2. 是否把医学权威线索作为主线，还是作为调节/扩展。
3. 是否现在纳入弹幕 NLP。
4. 当前 500 条 pilot 是否够用，还是先扩样本。
5. 视觉标题党和图文代表性到底先用人工标注，还是先用自动特征。
6. 论文应定位在健康传播、平台研究，还是多模态传播。
7. 下一步是否进入 `/scholar-design`。

---

## 2. 决策一：第一篇论文主线

### 选项 A：视觉标题党导致低成本/高成本参与分化

核心问题：

> 视觉标题党是否提高 `play/like`，但不提高甚至削弱 `coin/favorites/share`？

优点：

- 和 B站平台机制高度匹配。
- 能充分利用现有 500 条数据中的多个 DV。
- 理论贡献清楚：不是所有 engagement 都一样。
- 和 Deng et al. (2025) 健康 clickbait 研究形成直接对话，但扩展到视觉缩略图和 B站参与层级。
- scholar-idea 面板中 4/5 个评审都把它排第一。

风险：

- 观察性数据不能证明视觉标题党“导致”参与变化，只能说“关联”。
- B站算法推荐是重要混淆因素。
- 视觉标题党 index 需要可靠验证，不能随便相加。

推荐：

> **选 A 作为第一篇论文主线。**

### 选项 B：缩略图-标题代表性作为核心

核心问题：

> 图文代表性是否更能预测高成本参与？

优点：

- 理论干净，容易接处理流畅性、图文一致性和健康信息可信度。
- 可用 CLIP 相似度 + 人工标注双轨测量。
- 和 Yoon et al. (2024)、Li & Xie (2020)、Cao et al. (2025) 对话清晰。

风险：

- 如果只做图文代表性，视觉标题党的独特性会弱化。
- CLIP 相似度未必等于健康语境下的“代表性”。

推荐：

> 不单独作为第一篇主线，而是作为 A 的关键调节变量。

### 选项 C：医学权威视觉线索

核心问题：

> 白大褂、医院、报告、图表等视觉权威线索是否带来投币/收藏？

优点：

- 健康传播特色最强。
- 可以对接视觉健康误导和 source credibility。
- 很适合做第二篇或主文扩展。

风险：

- 自动识别医学权威线索不可靠。
- 必须人工标注。
- 如果作为第一主线，模型会更复杂。

推荐：

> 暂时作为扩展假设或调节项，不作为第一篇主线。

### 选项 D：弹幕作为机制窗口

核心问题：

> 视觉标题党是否带来更多怀疑、纠错、求证型弹幕？

优点：

- B站特色强。
- 机制解释力高。
- 如果做出来，会很有亮点。

风险：

- 需要额外抓弹幕。
- 需要 NLP 或人工分类。
- 当前 500 条 pilot 未必足够。
- 容易拖慢第一篇论文。

推荐：

> 不作为第一阶段主线。保留为第二阶段机制分析。

---

## 3. 推荐主线

第一篇论文应采用整合主线：

> 视觉标题党强度 → 低成本参与 / 高成本参与分化；图文代表性调节这种分化。

具体模型逻辑：

```text
视觉标题党强度
    → play / like 上升
    → coin / favorites / share 不一定上升

缩略图-标题代表性
    → 缩小或改变上述分化
    → 更强预测 coin / favorites / share
```

论文贡献一句话：

> 本研究表明，B站健康科普视频中的视觉标题党可能购买注意力，但图文代表性决定这种注意力是否转化为高成本认可和保存行为。

---

## 4. 决策二：样本策略

### 当前数据

已有文件：

`Web crawler/output/bilibili_health_500.csv`

当前样本：

| 项目 | 状态 |
|---|---|
| 视频数 | 500 |
| 唯一 UP 主 | 401 |
| 本地缩略图 | 500/500 |
| 官方认证 UP 主 | 167/500 |
| 参与变量 | play, like, danmaku, coin, favorites, share |
| 查询来源 | 健康科普、医学科普、医生提醒、体检报告、糖尿病、减肥、脱发、HPV、高血压等 |

### 选择 A：先用 500 条 pilot 做研究设计和测量验证

优点：

- 快。
- 足够做人工标注试验。
- 足够测试变量是否可操作。
- 可以先判断主假设方向是否有信号。

风险：

- 样本量对交互项和分组分析偏小。
- 主题噪音较大，尤其是减肥、健康科普、体检报告。
- 来源类型三分类可能 cell size 不够。

推荐：

> **先用 500 条做设计和测量验证。**

### 选择 B：先扩样本到 2000-10000 条

优点：

- 模型更稳。
- 交互项和分主题分析更可行。
- 更适合正式论文。

风险：

- 如果变量定义还没清楚，扩样本只是扩大噪音。
- 自动化特征未验证前，全量提取可能浪费时间。
- 数据清洗成本增加。

推荐：

> 不要现在扩。先验证码本和变量，再决定是否扩样本。

---

## 5. 决策三：人工标注 vs 自动特征

### 选择 A：先人工标注 200 张缩略图

推荐标注字段：

| 字段 | 说明 |
|---|---|
| `topic_relevance` | 是否是真健康科普 |
| `visual_clickbait_intensity` | 视觉标题党强度 |
| `thumbnail_title_representativeness` | 缩略图是否代表标题承诺 |
| `medical_authority_cue` | 医生、白大褂、医院、报告、图表、机构 logo |
| `threat_fear_visual` | 病灶、疼痛表情、红色警告、身体损伤、异常报告 |
| `text_overlay_intensity` | 缩略图文字叠加强度 |
| `misleading_risk` | 是否有误导或过度承诺风险 |

优点：

- 能验证核心概念是否可测量。
- 可作为自动特征的 gold standard。
- 能避免“AI 特征看起来高级但理论无效”的问题。

风险：

- 需要人工时间。
- 需要至少两名 coder 才能算一致性。

推荐：

> **必须先做人工标注。**

### 选择 B：直接用 CLIP/OCR/YOLO 自动提取

优点：

- 快。
- 可扩展。
- 适合大样本。

风险：

- CLIP 相似度不一定等于健康语境下的代表性。
- OCR 可能受中文缩略图字体影响。
- YOLO/face/emotion 对医学权威线索不可靠。
- 自动特征没有人工验证，审稿风险高。

推荐：

> 自动特征可以做，但必须在人工标注之后。

---

## 6. 决策四：是否纳入弹幕 NLP

### 纳入的价值

弹幕可以解释视觉标题党的机制：

| 弹幕类型 | 理论含义 |
|---|---|
| 求证 | 用户需要证据 |
| 纠错 | 用户识别潜在错误 |
| 怀疑 | 说服知识被激活 |
| 经验分享 | 健康信息触发个人经验 |
| 情绪反应 | 恐惧/惊讶/共鸣 |
| 仪式互动 | 社群参与，不一定和信息质量有关 |

### 不应现在纳入的原因

- 需要额外抓取弹幕。
- 需要人工标注或训练分类器。
- 当前第一篇论文的主模型还没确定。
- 会显著拉长周期。

推荐：

> 第一篇主模型只用弹幕数量；弹幕文本分类放到第二阶段或扩展分析。

---

## 7. 决策五：结果变量如何分组

推荐分组：

| 类型 | 变量 | 理论含义 |
|---|---|---|
| 低成本注意力 | `play`, `like` | 点击、浏览、轻度认可 |
| 互动表达 | `danmaku`, `review` | 讨论、情绪、求证、质疑 |
| 高成本认可/实用价值 | `coin`, `favorites`, `share` | 支持、保存、推荐 |

注意：

- 不要直接把 `coin/favorites/share` 称为“信任”。
- 更严谨说法是：高成本参与、认可代理、实用价值代理。
- 如果要谈“信任”，必须有问卷、实验或弹幕文本证据。

推荐：

> 使用“低成本参与 / 高成本参与”的语言，不直接写“信任”。

---

## 8. 决策六：统计模型方向

第一阶段模型可以这样设计：

### 模型 1：低成本参与

```text
log(play) 或 negative binomial(play)
    ~ visual_clickbait_intensity
    + representativeness
    + visual_clickbait × representativeness
    + controls
```

```text
log(like + 1)
    ~ visual_clickbait_intensity
    + representativeness
    + visual_clickbait × representativeness
    + controls
```

### 模型 2：高成本参与

```text
log(coin + 1)
log(favorites + 1)
log(share + 1)
    ~ visual_clickbait_intensity
    + representativeness
    + visual_clickbait × representativeness
    + controls
```

### 模型 3：系数差异

核心不是只看某个系数显著，而是比较：

```text
visual_clickbait 对 play/like 的系数
vs.
visual_clickbait 对 coin/favorites/share 的系数
```

如果前者更强，支持 engagement bifurcation。

### 控制变量

必须考虑：

| 控制 | 原因 |
|---|---|
| `duration` | 长视频与短视频参与模式不同 |
| `pubdate` / video age | 老视频有更多累计播放 |
| `follower` | 大 UP 主天然更多播放 |
| `is_official` / source type | 来源可信度和平台推荐可能不同 |
| `query` | 采样来源不同 |
| `topic_relevance` | 排除非健康内容 |
| `topic_category` | HPV、减肥、糖尿病等差异大 |
| `order_api` | 综合、最新、点击排序来源不同 |

算法混淆处理：

- 加入视频年龄。
- 加入上传时间。
- 加入粉丝数。
- 若可能，加入账号历史平均播放。
- 对 `play` 与 `coin/favorites` 分别建模，避免把播放既当结果又当控制时逻辑混乱。

---

## 9. 决策七：论文定位

### 定位 A：健康传播

卖点：

- 健康视频质量与参与度脱钩。
- 视觉权威和健康误导。
- 高成本参与作为健康信息有用性/认可代理。

目标期刊：

- *Health Communication*
- *Science Communication*
- *Journal of Health Communication*

风险：

- 如果医学质量评估不够，健康传播审稿人可能问“你如何知道内容质量”。

### 定位 B：平台/社交媒体研究

卖点：

- B站独特 engagement hierarchy。
- 注意力经济与高成本参与分化。
- 平台行为指标的理论化。

目标期刊：

- *New Media & Society*
- *Social Media + Society*
- *Information, Communication & Society*

风险：

- 健康传播贡献可能被弱化。

### 定位 C：多模态传播/计算传播

卖点：

- 缩略图-标题代表性。
- CLIP/OCR/视觉特征。
- 视觉标题党自动测量。

目标期刊：

- *Communication Methods and Measures*
- *Computational Communication Research*

风险：

- 方法要求更高，需要更强验证。

推荐：

> 第一篇定位为“平台化健康传播 / 多模态健康传播”，主投 Health Communication 或 Social Media + Society；不要一开始走纯方法论文。

---

## 10. 当前不建议做的事

| 不建议 | 原因 |
|---|---|
| 直接全量扩样本 | 核心变量未验证 |
| 直接跑 CLIP/OCR/YOLO 全特征 | 没有 gold standard |
| 先做弹幕 NLP | 会拖慢主线 |
| 把 `coin/favorites` 写成“信任” | 概念过度推断 |
| 把 RQ3 来源类型单独成文 | 当前 N 可能不够 |
| 做过多假设 | 第一篇应保持模型短而硬 |
| 把医学权威线索作为唯一主线 | 测量难度更高，适合作扩展 |

---

## 11. 当前建议立即做的事

### 第一步：运行 `/scholar-design`

建议命令：

```text
/scholar-design B站健康科普视频视觉标题党、图文代表性与差异化用户参与；基于 Web crawler/output/bilibili_health_500.csv 和本地缩略图；围绕 refined RQ1 设计变量、人工标注、模型、混淆控制和可行性评估
```

目标产出：

- DAG / 概念模型。
- 变量表。
- 标注抽样方案。
- 模型公式。
- 控制变量策略。
- 500 条 pilot 可做什么、不能做什么。

### 第二步：生成 annotation sample 和 codebook

建议目标：

```text
data/annotation/health_visual_clickbait_sample_200.csv
data/annotation/health_visual_clickbait_codebook.md
```

样本抽取策略：

- 按标题诱饵命中/未命中分层。
- 按 query/topic 分层。
- 按官方/非官方分层。
- 尽量覆盖高播放和普通播放。

### 第三步：人工标注一致性

至少两名 coder。

核心指标：

- Cohen's kappa 或 Krippendorff's alpha。
- 如果关键变量 kappa < .60，不应进入正式模型。
- 如果 kappa >= .75，可以作为主分析变量。

---

## 12. 最终推荐决策

如果现在需要拍板，我建议这样定：

| 决策点 | 推荐 |
|---|---|
| 第一篇主线 | 视觉标题党 → 低成本/高成本参与分化 |
| 核心调节变量 | 缩略图-标题代表性 |
| 医学权威线索 | 作为扩展假设，不作为主线 |
| 弹幕文本 | 第二阶段，不进入第一阶段主模型 |
| 样本 | 先用 500 条 pilot 做测量验证 |
| 标注 | 先人工标注 200 张缩略图 |
| 自动特征 | 人工验证后再扩展 |
| 论文定位 | 平台化健康传播 / 多模态健康传播 |
| 下一步 skill | `/scholar-design` |

---

## 13. 一句话决策

> 现在不要继续发散选题，也不要直接扩样本；应进入研究设计，围绕 RQ1 建立一个可测量、可验证、可建模的最小研究方案：200 张缩略图人工标注 + 500 条 pilot 多结果模型 + 图文代表性调节检验。

