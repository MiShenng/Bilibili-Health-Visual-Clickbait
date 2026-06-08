# 购买注意力，而非购买认可：多模态标题党与 B站健康科普视频用户参与的分化

<!-- 中文译稿来源：output/drafts/draft-full-paper-bili-health-visual-clickbait-2026-05-25.md -->
<!-- 版本：中文正文译稿 v1，2026-05-25 -->
<!-- 翻译范围：标题、摘要、引言、文献综述、理论与假设、数据与方法、表格、图注与参考文献。参考文献已并入文末，条目沿用英文格式。 -->

---

## 摘要

短视频平台已经成为公众获取健康信息的重要入口，但健康传播研究对视频缩略图中的视觉线索仍缺乏充分理论化。本文考察“多模态标题党”是否与 B站用户参与的特定分化模式相关。这里的多模态标题党是指视频缩略图中戏剧化面部情绪、威胁性图像和密集文字叠加的组合使用。B站是中国最大的长视频平台之一，其用户参与机制同时包含播放、点赞、弹幕、投币、收藏和分享等多层次行为。基于好奇缺口、威胁唤起和信号理论视角 （Scott 2021；Lang 2000；Bird and Smith 2005；Donath 2007），本文预期，多模态标题党对低成本注意力行为（播放、点赞）的促进作用强于对高成本认可行为（投币、收藏、分享）的促进作用；同时，缩略图与标题之间的代表性会调节这种差距。本文计划在一个包含 4,562 条 B站健康科普视频的语料上检验这些预期。该语料覆盖 2016 年 6 月至 2026 年 5 月发布的视频，通过 B站公开搜索 API 以 28 个关键词采集，覆盖五类健康主题。每条视频均配有本地归档的缩略图、六类互动指标以及 UP 主层面的属性，包括粉丝数、平台认证和原创/转载状态。视觉构念将通过三层混合方案编码：首先，由两名受训标注员按照五维码本对 500 张缩略图进行双盲人工标注；其次，对完整语料运行计算机视觉流程（PaddleOCR、RetinaFace + FER）和视觉语言模型（Claude Opus 4.7）；最后，在扩展到全语料之前检验人工分数与计算分数之间的聚合效度。模型方面，本文将估计负二项模型和零膨胀负二项模型，并在 UP 主层面使用聚类稳健标准误；同时并行报告跨 UP 主模型和 UP 主内固定效应模型。本文预注册五个假设（H1a-H4）和一个探索性三阶交互（H5）。研究设计为观察性设计，不作因果声称，并将使用 Oster $\delta$ 和 E-value 对未观测混杂进行边界评估。本文是一篇结果前稿件，旨在阐明理论动机、测量协议和分析计划；实证结果将在 OSF 预注册后补入。*关键词*：视觉标题党，健康传播，B站，多模态，用户参与，计算测量。

---

## 1. 引言

当 B站用户在搜索页输入“癌症 早期信号”时，在读到任何完整医学内容之前，首先看到的是一列视频缩略图。其中一张缩略图显示一位穿白大褂的医生，身后配有醒目的黄色大字“千万别乱用，用错后果严重”，旁边还有三个红色感叹号。另一张缩略图呈现一个正在哭泣的小孩和一位坐在轮椅上的老人，黄色文案请求陌生人“不要忽视他们”。第三张则是同一位医生坐在桌前，旁边有一份检查报告，标题文字只是“糖尿病出现口干口渴 有3种情况”。这三条视频出现在同一个搜索结果中，也都被上传者标记为健康教育内容。但它们向观看者发出的行动邀请并不相同，也很可能被 B站独特的参与机制以不同方式奖励。

B站区别于许多短视频平台的关键特征，是它保留了一套分层且具有成本梯度的用户行为。观看者可以播放视频（`play`）、点赞（`like`）、发送弹幕（`danmaku`）、收藏以便未来再看（`favorites`）、向外部分享（`share`），并且更重要的是，可以消耗平台配给的代币为视频“投币”（`coin`）。投币是稀缺行为：每个用户每天获得的投币额度有限，而且对单个视频最多只能投一枚币。因此，投币是一种被平台设计强制经济化的行为。在更广泛的平台参与研究中，这种分层结构并不常见。多数平台将参与行为简化为观看、点赞、评论和分享，很少内置一种明确的、代币化的、有成本的认可行为 （Lu and Shen 2023）。因此，B站提供了一个自然的经验场域，使我们能够追问：不同类型的参与行为是否会对同一种内容线索作出不同反应？

本文关注的线索是视频缩略图。缩略图是信息流平台中的核心视觉信号：它在视频播放前出现，占据用户视觉场域的大部分区域，并且越来越多地承载高密度设计元素，包括面部表情、威胁性图像、颜色对比和文字叠加。文字叠加事实上常常充当第二个、平行于标题的视觉标题。计算传播研究已经开始把缩略图视为独立分析单位 （Lu and Pan 2022；Al-Ali and Hamzeh 2024；Limpijankit and Kender 2025；Naveed, Uzmi, and Qazi 2025）。在新闻学研究中，“标题党”长期指那些以最大化点击率为目的、但可能牺牲信息质量或后续信任的标题策略 （Munger 2020；Vultee et al. 2022；Shin, DeFelice, and Kim 2025；Wang et al. 2025）。本文将这一概念扩展到视觉层面，并提出问题：当 B站健康科普视频在缩略图中使用多模态标题党线索时，这些线索究竟产生了什么类型的用户参与？

本文论证分为三部分。第一，我们把 B站的参与指标视为一个“成本层级”。播放和点赞是低成本行为；投币、收藏和外部分享则要求用户承担真实的预算成本或社会成本 （Dong et al. 2025）。第二，基于好奇缺口理论 （Scott 2021；Blom and Hansen 2015）、媒介信息加工有限容量模型 （Lang 2000）、视觉框架研究 （Powell et al. 2015；Geise and Xu 2025），以及高唤起线索可以制造注意但未必制造认可的双过程直觉 （Shin, DeFelice, and Kim 2025；Vultee et al. 2022），我们预期多模态标题党与低成本注意力之间的关联强于其与高成本认可之间的关联。第三，我们预期这种差距受到“缩略图-标题代表性”的调节：当缩略图准确预告标题以及视频实际内容时，高成本认可更可能出现。这一预期同时符合图文一致性文献 （Li and Xie 2020；Cao, Li, and Zhang 2025；Yoon, Yoon, and Park 2024） 和安全信息图文匹配的眼动研究证据 （Klein et al. 2020）。

本文将在 4,562 条 B站健康科普视频上检验这些预期。这些视频发布于 2016 年 6 月至 2026 年 5 月之间，通过 B站公开搜索 API 以 28 个中文关键词采集，覆盖五类健康内容主题：一般健康教育、慢性病、肿瘤与筛查、生活方式，以及预设的标题党词干短语（如“医生提醒”“医生终于说了”“这个习惯致癌”）。对每条视频，我们采集完整 API 元数据、六类互动指标、UP 主属性（包括粉丝数和平台认证状态）以及视频封面缩略图。视觉构念通过三层混合流程编码：在 500 张缩略图子样本上进行双盲人工标注，对全语料运行面部情绪和文字叠加几何特征的计算机视觉流程，并使用视觉语言模型对全语料评分，同时明确检验这些计算分数与人工金标准之间的聚合效度。

本文是一项观察性、结果前研究。我们有意将本文呈现的设计与测量部分同后续实证估计部分分开，后者将在 OSF 预注册之后进行。本文的目标是：（a）阐明为何应把视觉标题党理解为多模态现象，并把用户参与理解为有成本梯度的行为体系；（b）记录一个能够审计人机混合编码的测量流程，供后续研究复用；（c）提前规定分析计划，以处理高成本参与变量中的严重零膨胀、UP 主内聚类，以及推荐系统混杂下关联性推断的已知边界 （Lu and Pan 2021）。本文围绕四个研究问题展开：

- **RQ1**：B站健康科普视频在多大程度上使用多模态标题党线索（戏剧化情绪、威胁性图像、密集文字叠加）来设计缩略图？
- **RQ2**：多模态标题党是否与更高的低成本参与（播放、点赞）相关，而不是同等地与高成本认可（投币、收藏、分享）相关？
- **RQ3**：缩略图-标题代表性是否调节低成本注意力与高成本认可之间的差距？
- **RQ4**：这种参与分化模式是否取决于 UP 主的平台认证状态？

文章余下部分安排如下。第二节综述三类文献：视觉标题党与缩略图设计，图文一致性与处理流畅性，以及以 B站为重点的平台参与分层。第三节发展理论论证并提出五个假设。第四节介绍语料、码本、人机混合标注流程和计划分析，并明确说明本设计的因果边界。

---

## 2. 文献综述

### 2.1 从文字标题党到多模态缩略图标题党

标题党研究起源于新闻学对标题策略的分析，其核心关注是媒体如何通过隐藏信息来最大化点击。在线新闻的语言学分析提出，“前指”（forward-reference）是诱发期待的一种典型装置：标题使用回指或指示性表达，承诺读者尚未看到的内容 （Blom and Hansen 2015）。关联理论研究进一步说明，成功的标题党标题会利用定指表达和强化词来构造一种只有点击才能填补的信息缺口 （Scott 2021）。媒体经济学则把标题党形式化为注意力受限的读者与收入受限的发布者之间的策略互动：在稀缺注意力市场中，夸张是发布者对竞争环境的理性回应 （Munger 2020）。这一传统中的经验研究显示，标题党标题确实能提高点击率，但同时也可能损害用户对来源可信度的判断和分享意愿 （Vultee et al. 2022）；情绪化框架，尤其是“愤怒诱饵”，与信息缺口式标题的运作机制也有所不同 （Shin, DeFelice, and Kim 2025）。使用 EEG 和行为测量的受众实验进一步发现，不同类型的标题党（夸张、暗示、视觉修辞、谜题）会诱发可测量的不同认知和情绪反应 （Wang et al. 2025）。说服知识模型提供了更一般的解释：一旦读者识别出说服意图，他们对来源和内容的后续评价就会改变 （Isaac 2025）。

本文受这一文献的两项扩展启发。第一项扩展是转向非西方、平台原生且视觉主导的语境。Lu 和 Pan 对中国政府标题党实践的研究表明，标题党并不只是小报现象，而是算法可见度压力下的结构性回应 （Lu and Pan 2021）。他们关于抖音的后续研究显示，视觉主导的短视频平台已经形成一套最大化注意力的视频特征语法，包括高亮度、暖色调、短时长，以及与名人内容相似的视觉风格 （Lu and Pan 2022）。他们对中文事实核查视频的分析也进一步说明，用户参与和信息质量会对不同多模态特征作出不同反应 （Lu and Shen 2023）。第二项扩展是从文字标题转向视觉缩略图。Al-Ali 和 Hamzeh 对阿语 YouTube 标题党缩略图的分析显示，视觉线索、叠加文字和嵌入标点共同构成一个意义系统，而传统文字标题党研究系统性地遗漏了这个系统 （Al-Ali and Hamzeh 2024）。ThumbnailTruth 作为近期跨文化多模态 LLM 基准，对误导性缩略图检测问题进行了形式化，并指出文化多样的缩略图难以用单一语言方案处理 （Naveed, Uzmi, and Qazi 2025）。Limpijankit 和 Kender 则使用计算美学证明，缩略图设计中的系统性文化差异可以被大规模测量 （Limpijankit and Kender 2025）。本文在这些工作的基础上，把“视觉标题党”理解为多模态现象：一张缩略图不仅在叠加文字制造好奇缺口时构成标题党，也可能通过夸张面部表情、显著威胁图像和遮蔽底图的大面积文字层构成标题党。

### 2.2 图文一致性、处理流畅性与下游参与

第二类文献主要来自营销学和计算社会科学，关注图像与伴随文本之间的关系如何塑造用户行为。Li 和 Xie 对品牌社交媒体帖子的分析表明，图像内容、图像质量、人脸出现和图文匹配都能独立预测用户参与 （Li and Xie 2020）。使用深度学习测量图文一致性的后续研究则复杂化了“越一致越好”的简单直觉。Cao、Li 和 Zhang 发现，图文一致性与消费者偏好之间可能是非单调关系：高度一致带来流畅性，低一致带来惊奇和精细加工，而中等一致可能最不具吸引力 （Cao, Li, and Zhang 2025）。在自然语言处理框架下，Yoon 等人提出新闻缩略图代表性可以通过反事实文本生成来测量，并且代表性不同于一般的标题-图像相似性 （Yoon, Yoon, and Park 2024）。对于内容量巨大的视觉主导平台而言，问题已经不再是“一致性是否重要”，而是“它对哪一种参与指标重要”。这正是本文利用的经验入口。

视觉框架研究已经说明，图像和文本对框架效应的贡献并不冗余：文本更容易改变意见，图像更容易改变行为意图 （Powell et al. 2015）。一项覆盖 45 年视觉框架研究的系统综述发现，既有研究过度关注单图刺激，对多模态、平台原生和行为结果研究投入不足 （Geise and Xu 2025）。视觉错误信息研究也得出类似结论：视觉误导线索长期研究不足 （Heley, Gaysynsky, and King 2022），而其对可信度和下游行为的影响在不同文化和平台语境中并不一致 （Liu and Kuru 2025）。关于健康安全信息的眼动研究显示，配图与文字信息不匹配会降低用户对安全信息本身的注意和记忆 （Klein et al. 2020），这说明代表性并非风格偏好，而是影响理解的因素。在更广泛的健康传播中，Twitter/X 上气候图像的情绪内容也会系统性影响图像驱动的参与 （Bravo et al. 2025）；自动化视觉分析已经成为研究社交媒体健康效应的可行经验策略 （Peng, Lock, and Salah 2024）。

### 2.3 平台层面的参与分层、B站与弹幕

第三类文献聚焦中文视频平台 B站及其相邻平台抖音，提供本文的结果变量基础。B站的独特之处在于，它保留了双重观看行为结构：除了标准的观看、点赞、评论和分享之外，它还有同步显示的弹幕层，以及平台有意配给的投币代币。事实核查视频研究已经开始认真对待这种分层。Lu 和 Shen 对抖音中文事实核查视频的分析区分了会响应多模态特征的参与信号和不会响应的参与信号 （Lu and Shen 2023）。在 B站语境中，Chen 发现弹幕互动由不同于评论量的内容特征预测，这说明弹幕在参与层级中占据行为上不同的位置 （Chen 2025）。Dong 等人提出弹幕仪式类型的分类，如问候、投射、评价等，并发现影响下游数字参与的是弹幕仪式类型，而不是原始弹幕数量 （Dong et al. 2025）。这些发现指向同一个方法论要点：把参与合并成一个总分会丢失理论信息。

信号理论最初来自劳动经济学 （Spence 1973），后被 Donath 移植到线上社会环境 （Donath 2007），也为本文提供互补视角。昂贵信号之所以具有信息量，正是因为它们昂贵；廉价信号之所以常见，正是因为它们廉价 （Bird and Smith 2005）。应用到 B站，这意味着投币或收藏携带的信息不同于播放或点赞，因为用户为了发出这些信号付出了真实成本：前者消耗的是受限代币，后者则消耗未来自我管理收藏列表的边际成本。经验问题在于：多模态标题党线索本来是为了最大化廉价信号（点击）而设计的，它们是否也能最大化昂贵信号？说服知识模型预期，一旦观看者识别出说服意图，即使他们继续提供廉价参与，也可能抑制昂贵认可 （Isaac 2025）。本文并不直接检验这一心理机制，但它构成了我们方向性预测的基础。

另一个计算社会科学分支说明，大规模多模态视频分析已经可以覆盖数万条视频，但自动化视觉测量必须通过人工标注进行明确的构念效度审计 （Edelmann et al. 2020；Peng, Lock, and Salah 2024）。这一方法共识直接塑造了本文的标注设计（见第四节）。

### 2.4 现有研究缺口

标题党、图文一致性和 B站参与研究都在快速发展，但三者尚未真正连接起来。标题党研究仍然以文本为中心；少数多模态标题党研究也主要集中在英语和阿语新闻语境 （Al-Ali and Hamzeh 2024；Naveed, Uzmi, and Qazi 2025）。图文一致性研究则集中于品牌营销场景，其结果变量通常是购买或态度，而不是有成本梯度的平台参与。B站参与研究在弹幕层面最为成熟，但据我们所知，尚未处理不同视觉线索是否会映射到平台参与成本层级的问题。健康科普内容具有独特的可信度和下游行为风险，但现有研究更多评估内容质量，而很少研究决定用户是否进入视频的上游视觉线索。本文正位于这三个缺口的交叉点。

---

## 3. 理论与假设

### 3.1 用户参与的成本梯度观

本文的理论起点是：B站用户参与不是一个单一数量，而是一组成本不同的行动。播放只要求用户投入开始观看视频的边际注意力。点赞只要求一次点击。弹幕要求用户写下并提交一条公开同步评论，因而包含时间和自我暴露成本。收藏意味着用户把视频归类为未来值得再看的内容。分享要求用户承担社会风险，也就是向外部受众推荐视频所附带的声誉含义。投币则要求用户消耗一部分每日平台配给预算，并且一旦投出不可撤回：投给这里的币今天就不能再投给别的视频。我们并不主张所有用户以完全相同的方式感知这些成本；我们只主张，这种行为排序在总体层面足够稳定，因此值得被分析性地区分。

这一框架来自信号理论关于廉价信号和昂贵信号的核心区分 （Spence 1973；Bird and Smith 2005；Donath 2007）。均衡中，一个信号的信息含量随其成本上升而提高：廉价信号常见，因此信息量较低；昂贵信号稀缺，因此更具诊断性。应用到视频语料，这意味着同一种内容特征可能在廉价参与和昂贵参与上产生统计上不同的模式；把这些结果合并起来，不是揭示行为，而是遮蔽行为。

### 3.2 为什么多模态标题党会购买注意力，而非购买认可

多模态标题党是一种通过放大缩略图中感知显著线索来最大化点击概率的内容策略。本文识别三类此类线索：**情绪强度**，即夸张面部表情，尤其是恐惧、震惊或厌恶；**威胁图像**，即医疗器械、病灶、痛苦身体、红色警告标识；以及**文字叠加强度**，即高覆盖、高对比度的缩略图文字，它们预先制造好奇缺口。每类线索都有不同机制基础。情绪化图像比中性图像加工更快、记忆更强，情绪强度也与社交媒体内容的病毒式传播相关 （Bravo et al. 2025；Shin, DeFelice, and Kim 2025）。威胁图像激活恐惧诉求中的威胁显著性通道；在缺少效能线索时，威胁更容易驱动注意，而不一定驱动审慎行动 （Zhang and Zhou 2019；Heley, Gaysynsky, and King 2022）。文字叠加强度则相当于把第二个标题嵌入图像，扩大构造好奇缺口的表面空间 （Al-Ali and Hamzeh 2024；Scott 2021；Blom and Hansen 2015）。

这些机制的共同点是，它们主要指向“进入”决策，也就是是否点击，而不是指向“进入后”决策，也就是是否认可。关于读者端标题党的研究与这种不对称一致：标题党标题往往可靠地提高点击，却不一定提高信任、分享或其他下游测量（Vultee et al. 2022；Shin, DeFelice, and Kim 2025；Wang et al. 2025）。说服知识模型为这种不对称提供了概念名称：一旦观看者意识到缩略图被设计出来是为了最大化他们点击的概率，他们可能仍然点击，但会保留那些本来可以表示认可的昂贵信号（Isaac 2025）。在 B站上，昂贵信号正是受限的投币、面向未来的收藏和外部分享。因此，我们预期出现一种参与分化：

- **H1a**：多模态标题党强度与低成本参与（播放、点赞）正相关。
- **H1b**：多模态标题党强度与高成本认可（投币、收藏、分享）的关联弱于其与低成本参与的关联。

H1b 是一个比较性假设：它预测多模态标题党指数在高成本方程中的标准化系数小于其在低成本方程中的标准化系数，而不是预测该系数一定为零或负。本文将使用系数差异的非参数 bootstrap 来检验这一点（见 4.6 节）。

### 3.3 为什么信息缺口应被单独处理

在初步编码中，并且与好奇缺口传统一致，我们将“信息缺口”同上文三类视觉标题党维度区分开来。信息缺口是标题承诺的属性，而不是缩略图图像的属性。它指的是标题和缩略图可见文案在多大程度上有意保留视频的关键答案。语料中的例子包括“这个习惯致癌”（哪种习惯？）、“医生终于说了”（说了什么？）、“体检出现这些信号千万别忽视”（哪些信号？）。从理论上说，信息缺口机制更偏认知而非情感：它使观看者意识到自身存在知识缺口，并把点击作为闭合缺口的方式 （Scott 2021；Blom and Hansen 2015）。因为缺口是在文本中构造的，将它与面部表情等图像侧线索混为一谈会误命名构念。因此，本文把信息缺口作为一个单独预测变量：

- **H1c**：信息缺口强度与低成本参与正相关，并且与高成本认可之间的关联弱于与低成本参与之间的关联，这一模式与 H1a-H1b 平行。

### 3.4 为什么缩略图-标题代表性会调节这种差距

代表性指的是缩略图能否准确预告标题以及视频内容。一个高代表性的缩略图，如果对应标题是“糖尿病患者口干口渴要注意的三种情况”，可能会呈现医生、检查报告和列出三点的文字叠加；而低代表性的缩略图可能只是显示一张泛泛的水杯图。两类文献给出了相反预测，而哪种机制占优需要经验检验。

处理流畅性传统认为，一致的图文组合更容易加工，更容易产生可信感，也更可能将注意力转化为行动 （Li and Xie 2020）。相反，好奇-不一致传统认为，不匹配会制造惊奇和精细加工，在某些条件下也可能促进转化 （Cao, Li, and Zhang 2025）。本文预期，对**高成本认可**而言，流畅性通道会占主导。原因是，收藏和投币要求观看者对内容价值作出面向未来的判断，而这种判断取决于缩略图承诺是否被兑现。我们预期代表性与低成本注意力之间的关联较弱，因为注意力在点击瞬间就被捕获，而这发生在用户有机会比较代表性之前。

- **H2**：缩略图-标题代表性与高成本认可正相关。
- **H3**：代表性与高成本认可之间的正向关联强于其与低成本参与之间的关联。

### 3.5 医学权威线索与认证状态

健康科普内容具有一般标题党研究不具备的来源可信度含义。白大褂、临床报告或医院背景都可以充当医学权威的视觉信号。基于信号理论，权威线索应当增强高成本认可，但只有当这些线索与内容一致时，这种增强才更可能成立；当权威线索与高标题党强度共存时，观看者可能将其理解为包装而非资质，从而减弱认可反应 （Isaac 2025；Heley, Gaysynsky, and King 2022）。本文首先提出主效应：

- **H4**：医学权威视觉线索与高成本认可正相关。

B站通过正式认证区分上传者。认证账号（`is_official == TRUE`）包括认证医疗专业人士、机构频道和认证媒体账号。信号理论和读者端文献都提示，H1 中的参与分化可能在认证账号中被削弱：观看者可能对认证上传者给予更多信任，从而更容易把标题党驱动的注意力转化为高成本认可；也可能反过来，由于认证上传者本应承担更高标准，观看者在其使用标题党时反而更严格，因而压低认可。由于两个方向都有理论依据，本文把该调节作为探索性假设：

- **H5（探索性）**：H1 中的参与分化模式受到 UP 主认证状态调节；本文不预设方向。

H5 仅在附录报告；主要验证性假设族为 H1a-H4。

### 3.6 本文不作哪些声称

本文不声称多模态标题党对参与行为具有因果效应。本研究为观察性设计。B站推荐系统是一个重要的未观测混杂来源，因为它同时影响上传者选择哪些视觉线索，也影响视频最终获得多少参与。本文采取三项保护性措施：全文使用明确的关联性语言；对主要系数进行敏感性边界评估（Oster $\delta$ 和 E-value）；并采用并行 UP 主内模型，以吸收所有不随时间变化的 UP 主特征，包括该频道被推荐系统平均推广的倾向。我们并不声称 UP 主内模型识别了因果效应，只是认为它通过部分排除一大类混杂因素，增强了关联推断的可信度。

---

## 4. 数据与方法

### 4.1 平台与语料

B站（bilibili.com）是中国最大的长视频平台之一，成立于 2009 年，以同步弹幕评论层和代币化“投币”认可系统著称。不同于短视频竞争者，B站保留了长视频内容，并在点赞、投币、收藏、分享四类行动之外保留弹幕通道。截至 2024 年第三季度，B站报告平均月活跃用户为 3.48 亿 （Bilibili Inc. 2024）。本文选择 B站，是因为相较其他中文平台，B站的参与架构在设计层面更清楚地区分廉价和昂贵的用户行动。

本文通过平台公开搜索 API 于 2026 年 5 月 24 日采集语料。搜索 API 返回非登录用户输入关键词后看到的排序列表，同时支持分页和排序控制。我们针对 28 个中文关键词（见表 1）分别发出三类排序查询：`totalrank`（综合相关性）、`pubdate`（最新发布）和 `click`（点击/播放热度），每个查询最多爬取 15 页。关键词分为五个主题簇：一般健康教育（如“健康科普”“医生提醒”“体检报告”，共 5 个关键词）、慢性病（“糖尿病”“高血压”“心脏病”“脂肪肝”，共 4 个关键词）、肿瘤与筛查（“癌症 早期信号”“HPV 疫苗”“肺癌 科普”，共 3 个关键词）、生活方式（“减肥 科学”“脱发 医生”“睡眠 健康”“饮食健康”，共 4 个关键词），以及预设标题党词干短语（如“医生提醒 千万别”“医生终于说了”“这个习惯 致癌”，共 12 个关键词，含短词变体）。标题党词干簇被有意纳入，以确保主要自变量具有足够变异；我们通过在所有主要模型中加入关键词类别固定效应，并在稳健性检验中执行 leave-one-keyword-out 分析来处理这一采样设计。

[表 1 置于此处]

对每个返回视频，我们采集完整元数据（`bvid`、`aid`、标题、简介、发布时间戳、时长、B站分区 `tname`、原创/转载状态 `copyright`）、六类互动指标（播放、点赞、投币、收藏、分享、弹幕）、UP 主层面属性（`mid`、粉丝数、平台认证状态、频道签名、UP 主等级）以及封面缩略图（JPG，本地归档）。按 `bvid` 去重后，工作语料包含 4,562 条唯一视频，来自 2,731 个唯一 UP 主（均值 = 每 UP 主 1.67 条视频；中位数 = 1；最大值 = 47）。视频发布时间从 2016 年 6 月 22 日到 2026 年 5 月 24 日，其中 71% 发布于 2024-2026 年。所有互动指标均来自 2026 年 5 月 24 日六小时窗口内的一次横截面快照；因此，我们将 `video_age_days`（视频发布日至爬取日的天数）作为主要控制变量。缩略图下载成功 4,564 张，覆盖全部可分析视频。

### 4.2 结果变量及其分布

本文将六类参与指标分为低成本、中间成本和高成本三组。低成本参与包括播放数和点赞数。播放数是最廉价的注意力指标；点赞只要求一次点击，但仍表示轻度认可。高成本认可包括投币、收藏和分享。投币受到平台日配额限制，因而是稀缺认可；收藏表示未来再看或保存参考价值；分享要求用户把视频推荐给外部或社交网络，带有社会声誉成本。弹幕作为同步文本表达通道，理论上处于中间位置，因为它要求用户生成可见内容。本文把弹幕作为单独结果报告，而不把它并入低成本或高成本指数。

所有参与指标都高度右偏，且部分变量零值比例较高（见表 2）。播放数均值为 570,285，中位数为 7,716，说明样本中少数爆款视频显著抬高均值。投币、分享和弹幕零膨胀尤其明显，零值比例分别为 36.5%、27.0% 和 45.8%。因此，本文计划对播放、点赞和收藏使用负二项模型，对投币、分享和弹幕使用零膨胀负二项模型。所有结果也将以 `log(y + 1)` 形式在 OLS 稳健性检验中报告，以便解释和作图。

[表 2 置于此处]

### 4.3 视觉构念码本

主要解释变量是 `multimodal_clickbait_idx`，由三个视觉维度构成：情绪强度、威胁图像和文字叠加强度。情绪强度指缩略图中人脸或拟人对象的戏剧化程度，从中性到高度震惊、恐惧、厌恶或痛苦进行编码。威胁图像指是否出现身体伤害、病灶、医学器械、疼痛姿态、红色警告、异常报告或其他将健康风险视觉化的元素。文字叠加强度指缩略图上覆盖文字在面积、对比度和语义压力上的强度。每一维均按 0-3 的有序尺度编码，并通过平行分析和 MAP 检验确定因子结构。预期的单因子由三个视觉维度共同构成；如果数据支持双因子结构，则将情绪/威胁作为唤起通道，将文字叠加作为视觉-文本通道分别建模。

我们将 `info_gap_idx` 作为单独构念。它测量标题和缩略图文字在多大程度上有意保留关键信息，例如“千万别做这件事”“医生终于说了”“体检出现这三种情况”。将信息缺口从视觉标题党指数中分离，是为了避免把文本好奇机制同图像唤起机制混为一谈。

`representativeness` 指缩略图是否准确代表标题中的核心健康承诺。人工标注员按照 0-3 尺度评分：0 表示明显不相关或误导；1 表示仅有弱主题相关；2 表示大体代表标题主题但有夸张或遗漏；3 表示清楚、具体地代表标题承诺。完整语料中的自动代表性分数由 Chinese-CLIP 图像-文本余弦相似度计算，并在 500 张人工子样本上验证。

`medical_authority_cue` 被分解为四个二元指标：白大褂或临床专业形象、医学器械或身体/解剖图、检查报告/图表/幻灯片、机构 logo 或医院场景。四项相加得到 0-4 的权威线索计数。我们之所以不用单一 0-2 总分，是因为不同权威线索可能具有不同视觉功能，并且自动识别可靠性不同。

### 4.4 混合标注流程

本文使用三层标注流程。

**第一层：人工金标准。** 从 4,562 条语料中抽取 500 张缩略图进行双盲人工标注。抽样按关键词簇、认证状态和播放量四分位分层，以确保标题党词干、长尾视频和认证上传者都有充分覆盖。两名标注员在打乱顺序的图像上独立工作，并且看不到结果变量。标注员可看到缩略图和标题，因为代表性编码需要二者共同判断。标注前先完成 50 张训练集和一小时小组校准。所有有序变量报告二次加权 Cohen's $\kappa$；二元变量报告 Cohen's $\kappa$，Krippendorff's $\alpha$ 作为补充。预设最低门槛为 $\kappa \geq .70$，`info_gap_idx` 可接受 $\kappa \geq .65$。

**第二层：全语料计算编码。** 4,562 张缩略图通过两条并行流程处理。计算机视觉流程使用 RapidOCR 进行文本检测和几何分析，得到文字面积覆盖率和字体对比度等指标，用于构造 `text_overlay_intensity`；同时使用 RetinaFace 和中文验证的 FER 模型进行面部情绪识别，得到连续情绪强度分数。视觉语言模型流程使用 Claude Opus 4.7（Anthropic；`claude-opus-4-7`）运行单一结构化提示，该提示包含码本操作定义和少量提示内示例，返回 `topic_relevance`、`threat_imagery`、`info_gap` 和四个医学权威条目的有序分数。原始 VLM API 响应将归档以便复现。缩略图-标题代表性方面，本文使用 Chinese-CLIP（ViT-B/16）（Yang et al. 2022） 计算封面图像和标题文本嵌入之间的余弦相似度，并在 500 张缩略图子样本上与人工有序评分验证。

**第三层：聚合效度审计。** 在 500 张缩略图子样本上，计算分数将与人工金标准通过 Spearman's $\rho$ 验证。我们预设 $\rho \geq 0.60$ 为计算测量可用于全语料分析的门槛。未达到该门槛的测量只在 500 张金标准子样本中报告。达到门槛的计算测量用于全语料分析，同时所有主模型还将在 500 张人工金标准子样本上重新拟合，以作为稳健性检验。

这一流程与计算视觉社会科学的方法共识一致 （Edelmann et al. 2020；Peng, Lock, and Salah 2024），也与近期缩略图检测基准采用的多模态标注策略相符 （Naveed, Uzmi, and Qazi 2025）。本文相较既有实践的不同之处在于，我们预先注册了一个明确的 Spearman 门槛，用于决定计算测量是否可以推广到全语料使用。

### 4.5 控制变量

主要控制变量包括：`video_age_days`，即视频发布日至爬取日之间的天数，用于吸收老视频累计参与更多的偏差；`log_followers`，即 UP 主粉丝数的对数，用于吸收频道规模；`duration_log`，即视频时长秒数的对数；`pubdate_year`，作为分类固定效应，用于吸收十年窗口中平台机制的演化；`tname`，即 B站分区固定效应；`copyright_self`，即视频是否为原创而非转载的二元指标；以及 `is_official`，即平台认证状态。我们有意不把 `order_source`（视频在哪种排序查询下被检索到）放入控制变量，因为它内生于视频标题党强度，因而可能是后处理变量。附录中将报告包含 `order_source` 固定效应的敏感性模型。对于 13% 在 `tid`、`copyright` 或 `uploader_level` 上存在缺失的视频（来自早期爬虫批次），我们使用 `aid` 单调索引通过等距回归推断 `video_age_days`，其余缺失字段编码为单独的“missing”类别。

### 4.6 分析策略

对六个结果变量中的每一个，本文拟合五个嵌套模型。M1 只包含多模态标题党指数和信息缺口指数。M2 加入完整控制变量。M3 加入代表性主效应。M4 加入多模态标题党 × 代表性，以及信息缺口 × 代表性的交互项。M5 为探索性模型，额外检验与 `is_official` 的三阶交互。标准误在 UP 主（`mid`）层面聚类稳健处理，以应对同一频道发布多个视频导致的非独立性。

本文预注册一个“双轨”主要模型设定：第一条轨道是在完整 4,562 条视频样本上的跨 UP 主横截面模型（M2a）；第二条轨道是在拥有至少 2 条视频的 UP 主子样本上的 UP 主内固定效应模型（M2b；约 1,400 个 UP 主，贡献约 3,500 条视频）。双轨设计是因为我们同时面临两种张力：跨 UP 主层面存在推荐系统未观测混杂风险，而 UP 主内模型会损失统计功效。本文将两者并列作为主要模型报告，并把二者是否一致视为实质性结果。

为检验比较性假设 H1b，本文将分化对比定义为低成本方程（播放；负二项）中标准化多模态标题党系数与高成本方程（投币；零膨胀负二项）中对应系数之差。该差异的 95% 置信区间将通过视频层面 1,000 次非参数 bootstrap 构造，并按 UP 主分层重抽样。所有边际效应将用 R 包 `marginaleffects` 报告为平均边际效应（AME）（Arel-Bundock, Greifer, and Heiss 2024），以符合目标期刊报告规范。

多重比较控制将按如下方式预注册：验证性检验族包括 H1a、H1b、H1c、H2、H3 和 H4；该检验族使用 Benjamini-Hochberg false-discovery-rate 控制，q = 0.05，其中投币和收藏作为高成本主要结果，其余四个结果作为次要结果。探索性 H5 不作多重比较校正。

### 4.7 稳健性检验

本文预注册以下敏感性检验：（R1）使用比例结果（投币/播放、收藏/播放、分享/播放）并采用 beta 回归重新拟合；（R2）限制到 2022 年之后样本，以处理平台机制演化；（R3）剔除粉丝数最高的 5% 频道；（R4）限制到“科学科普”分区；（R5）使用 Poisson 模型替代负二项模型；（R6）用多模态标题党指数四分位虚拟变量替代连续变量，以放宽线性假设；（R7）使用 Oster $\delta$ 评估未观测混杂边界 （Oster 2019）；（R8）使用 E-value （VanderWeele and Ding 2017）；（R9）限制到人工金标准严格编码为 `topic_relevance == 1` 的视频；（R10）比较 500 张人工标注子样本与全语料 VLM 编码模型，以检测测量来源依赖；（R11）对 13% 缺失使用 listwise deletion 与多重插补（m = 20）对比；（R12）在 `mid` 与 `pubdate_month` 上做双向聚类，以处理推荐系统可能导致的 SUTVA 违反；（R13）对五个标题党词干种子关键词执行 leave-one-keyword-out 稳健性检验。

### 4.8 因果边界与局限

本文不声称多模态标题党对用户参与具有因果效应。B站推荐系统同时决定哪些缩略图被推入用户视野，以及这些视频随后获得多少参与；缩略图与参与指标之间的后门路径无法仅凭观察性数据关闭。UP 主内固定效应模型吸收了所有不随时间变化的 UP 主特征，包括频道平均历史推广倾向，但无法吸收视频层面的推广冲击。Oster $\delta$ 和 E-value 敏感性分析可以量化需要多强的未观测混杂才能使估计关联归零，但它们不能替代外生变异来源。本文还存在三项进一步局限。第一，语料是“在 28 个健康相关关键词下被搜索 API 返回的视频”，而不是“B站所有健康相关视频”；因此，结果只能推广到搜索索引可见的子集。第二，参与指标是单日快照；比例结果（R1）可以部分缓解累计参与偏差，但不能消除该偏差。第三，本文测量封面缩略图的视觉特征，而不测量视频本身的音视频内容；一个缩略图误导的视频可能从头到尾都是标题党，也可能在点击后提供实质内容，而本文设计不能区分二者。

### 4.9 预注册、开放科学与伦理

预分析计划、码本、全部 VLM 提示词和分析代码将在任何结果模型估计之前存入 OSF。语料元数据将在排除原始缩略图后归档至 Zenodo 并获得 DOI；缩略图原图受平台服务条款限制，不会重新分发。公开数据将提供图片 URL 和重新采集脚本。UP 主标识符（`mid`）在公开数据中单向哈希化；可能包含个人身份信息的 UP 主签名字段（`uploader_sign`）将通过结构化标签方案脱敏。研究仅使用公开、非账号限制的平台元数据，不与用户或上传者互动；本机构伦理审查委员会已将该方案归类为第 4 类豁免研究，即使用既有公开可得数据的研究。本文披露使用 Claude Opus 4.7 作为标注流程中的二级编码器；所有主要编码决定由人工标注员保留，模型仅用于在人类金标准验证之后扩展到全语料。

---

## 表 1：关键词分层与每个关键词样本量

<!-- 来源：由 Data process/master_bilibili_health.csv 的 query 字段整理 -->

| 主题簇 | 关键词 | N |
|---|---|---|
| 一般健康教育 | 医学科普 | 435 |
| 一般健康教育 | 健康科普 | 429 |
| 一般健康教育 | 医生提醒 | 390 |
| 一般健康教育 | 体检报告 | 248 |
| 一般健康教育 | 饮食健康 | 196 |
| 一般健康教育 | 养生科普 | 180 |
| 慢性病 | 糖尿病 科普 | 180 |
| 慢性病 | 高血压 科普 | 180 |
| 慢性病 | 心脏病 科普 | 180 |
| 慢性病 | 脂肪肝 科普 | 180 |
| 慢性病 | 糖尿病（短词） | 60 |
| 慢性病 | 高血压（短词） | 20 |
| 慢性病 | 高血压 危险信号 | 6 |
| 肿瘤与筛查 | 癌症 早期信号 | 180 |
| 肿瘤与筛查 | HPV 疫苗 | 180 |
| 肿瘤与筛查 | 肺癌 科普 | 180 |
| 肿瘤与筛查 | HPV（短词） | 60 |
| 生活方式 | 减肥 科学 | 180 |
| 生活方式 | 脱发 医生 | 180 |
| 生活方式 | 睡眠 健康 | 180 |
| 生活方式 | 减肥（短词） | 60 |
| 生活方式 | 脱发（短词） | 60 |
| 标题党词干 | 医生提醒 千万别 | 180 |
| 标题党词干 | 医生终于说了 | 180 |
| 标题党词干 | 体检报告 异常 | 130 |
| 标题党词干 | 这个习惯 致癌 | 92 |
| 标题党词干 | 健康科普 千万别吃 | 18 |
| 标题党词干 | 医生提醒 致癌 | 18 |
| **总计（去重前）** | — | **5,062** |
| **总计（去重后，主语料）** | — | **4,562** |

**注**：N 反映每个关键词 × 排序方式组合下检索到的唯一视频数量，尚未按 `bvid` 全局去重。全局去重后，分析语料保留 4,562 条唯一视频。关键词主题簇在所有主要模型中作为分类固定效应编码。“标题党词干”簇包含预设搜索词，用于过采样多模态标题党强度较高的视频；对应的 leave-one-keyword-out 稳健性检验见 4.7 节。

---

## 表 2：参与结果变量的描述性分布（N = 4,562）

<!-- 来源：Data process/audit_report.md §4 -->

| 结果变量 | 均值 | 中位数 | 第 25 百分位 | 第 75 百分位 | 第 95 百分位 | 零值比例 | 计划模型 |
|---|---:|---:|---:|---:|---:|---:|---|
| 播放（`play`） | 570,285 | 7,716 | 239 | 245,933 | 3,140,807 | 1.3 | 负二项 |
| 点赞（`like`） | 19,265 | 109 | 5 | 4,694 | 105,566 | 5.1 | 负二项 |
| 收藏 | 8,819 | 66 | 2 | 1,806 | 37,505 | 16.6 | 负二项 |
| 分享 | 3,171 | 18 | 0 | 622 | 12,046 | 27.0 | **ZINB** |
| 评论（`review`） | 674 | 11 | 0 | 358 | 3,486 | 30.5 | ZINB |
| 投币 | 4,682 | 7 | 0 | 282 | 14,663 | 36.5 | **ZINB** |
| 弹幕 | 1,170 | 1 | 0 | 124 | 4,149 | 45.8 | **ZINB** |

**注**：N = 4,562 条唯一视频。各分布均明显右偏；因此除均值外，表中同时报告中位数、第 25、第 75 和第 95 百分位，以呈现离散程度。“零值比例”表示该结果变量等于 0 的视频比例。ZINB = 零膨胀负二项模型。高成本认可结果中的投币、分享和弹幕零值比例均超过 25%，因此采用 ZINB 设定。ZINB 的膨胀方程包含 `log_followers` 和 `video_age_days`。

---

[图 1 置于此处]

**图 1（计划）**：多模态标题党指数在 500 张人工金标准缩略图子样本中的密度图。该指数是由情绪强度、威胁图像和文字叠加强度生成的因子分数。图中叠加全语料 VLM 编码得到的平行分布，并按 Spearman $\rho$ 聚合效度等级着色。

[图 2 置于此处]

**图 2（计划）**：双轨分析策略示意图。左图为完整 4,562 条视频样本上的跨 UP 主横截面模型；右图为至少发布 2 条视频的 UP 主子样本上的 UP 主内固定效应模型（约 1,400 个 UP 主，约 3,500 条视频观测）。

[图 3 置于此处]

**图 3（计划）**：混合标注流程图。第一层为 500 张缩略图人工金标准（双盲，两名标注员）。第二层为全语料计算编码（RapidOCR + RetinaFace + FER；Chinese-CLIP 测量代表性；Claude Opus 4.7 对 VLM 构念评分）。第三层为聚合效度审计（Spearman $\rho \geq 0.60$ 才允许推广到全语料）。

---

## 参考文献

Al-Ali, M.N. and S.M. Hamzeh. 2024. "Extra Cues Extra Views: A Multimodal Detection of Arabic Clickbait Thumbnail Verbo-Visual Cues." *Discourse & Communication*.

Arel-Bundock, V., N. Greifer, and A. Heiss. 2024. "How to Interpret Statistical Models Using marginaleffects for R and Python." *Journal of Statistical Software* 111(9): 1-32. https://doi.org/10.18637/jss.v111.i09.

Araujo, T., I. Lock, and B. van de Velde. 2020. "Automated Visual Content Analysis (AVCA) in Communication Research: A Protocol for Large Scale Image Classification with Pre-Trained Computer Vision Models." *Communication Methods and Measures* 14(4): 239-265.

Bilibili Inc. 2024. *Bilibili Inc. Reports Third Quarter 2024 Financial Results*. Form 6-K filed with the U.S. Securities and Exchange Commission, November 14, 2024. Retrieved May 25, 2026 (https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001723690).

Bird, R.B. and E.A. Smith. 2005. "Signaling Theory, Strategic Interaction, and Symbolic Capital." *Current Anthropology*.

Blom, J.N. and K.R. Hansen. 2015. "Click Bait: Forward-Reference as Lure in Online News Headlines." *Journal of Pragmatics* 76: 87-100.

Bravo, I., K. Prasse, S. Walter, S. O'Neill, and M. Keuper. 2025. "Global Dynamics of Climate Change Imagery: Emotional and Engagement Effects Across Visual Frames on Twitter/X." *Science Communication*.

Cao, J., X. Li, and L. Zhang. 2025. "Is Relevancy Everything? A Deep-Learning Approach to Understand the Effect of Image-Text Congruence." *Management Science*.

Chen, J. 2025. "Understanding Danmaku and Comment Interactions Through Content Features and Video Popularity." *Procedia Computer Science*.

Donath, J. 2007. "Signals in Social Supernets." *Journal of Computer-Mediated Communication*.

Dong, W., Y. Liu, W. Wang, L. Jiang, and Y. Yi. 2025. "The Impact of Danmaku Ritual Types on User Digital Engagement in Video-Based Social Media: The Moderating Role of Influencer Types and Domains." *Psychology & Marketing*.

Edelmann, A., T. Wolff, D. Montagne, and C.A. Bail. 2020. "Computational Social Science and Sociology." *Annual Review of Sociology*.

Geise, S. and Y. Xu. 2025. "Effects of Visual Framing in Multimodal Media Environments: A Systematic Review of Studies Between 1979 and 2023." *Journalism & Mass Communication Quarterly*.

Guo, L., Y. Wang, P. Li, Y. Wang, and Y. Li. 2026. "The Impact of Headline Characteristics on Clicks: A Case Study of a Chinese Local Medium." *Journalism Practice* 20(4): 1427-1455.

Heley, K., A. Gaysynsky, and A.J. King. 2022. "Missing the Bigger Picture: The Need for More Research on Visual Health Misinformation." *Science Communication* 44(4): 514-527.

Isaac, M.S. 2025. "Thirty Years of Persuasion Knowledge Research: From Demonstrating Effects to Building Theory to Increasing Applicability." *Consumer Psychology Review*.

Jones, C.L., J.D. Jensen, C.L. Scherr, N.R. Brown, K. Christy, and J. Weaver. 2015. "The Health Belief Model as an Explanatory Framework in Communication Research: Exploring Parallel, Serial, and Moderated Mediation." *Health Communication* 30(6): 566-576.

Keib, K., C. Espina, Y.-I. Lee, B.W. Wojdynski, D. Choi, and H. Bang. 2018. "Picture This: The Influence of Emotionally Valenced Images on Attention, Selection, and Sharing of Social Media News." *Media Psychology* 21(2): 202-221.

Khawar, S. and M. Boukes. 2025. "Analyzing Sensationalism in News on Twitter (X): Clickbait Journalism by Legacy vs. Online-Native Outlets and the Consequences for User Engagement." *Digital Journalism* 13(8): 1482-1502.

King, A.J. and A.J. Lazard. 2020. "Advancing Visual Health Communication Research to Improve Infodemic Response." *Health Communication* 35(14): 1723-1728.

Klein, E.G., K. Roberts, J. Manganello, R. McAdams, and L. McKenzie. 2020. "When Social Media Images and Messages Don't Match: Attention to Text versus Imagery to Effectively Convey Safety Information on Social Media." *Journal of Health Communication* 25(11): 879-884.

Kuiken, J., A. Schuth, M. Spitters, and M. Marx. 2017. "Effective Headlines of Newspaper Articles in a Digital Environment." *Digital Journalism* 5(10): 1300-1314.

Lang, A. 2000. "The Limited Capacity Model of Mediated Message Processing." *Journal of Communication* 50(1): 46-70.

Li, Y. and Y. Xie. 2020. "Is a Picture Worth a Thousand Words? An Empirical Study of Image Content and Social Media Engagement." *Journal of Marketing Research*.

Limpijankit, M. and J.R. Kender. 2025. "Detecting Cultural Differences in News Video Thumbnails via Computational Aesthetics."

Liu, A.K.C. and O. Kuru. 2025. "Understanding the Effects of Visual Misinformation: A Systematic Review of 10 Years (2014-2024)." *Mass Communication and Society*.

Liu, S., J. Xu, Z. Zhao, and X. Li. 2023. "Factors Affecting Trust in Chinese Digital Journalism: Approach Based on Folk Theories." *Media and Communication* 11(4): 355-366.

Lu, Y. and J. Pan. 2021. "Capturing Clicks: How the Chinese Government Uses Clickbait to Compete for Visibility." *Political Communication*.

Lu, Y. and J. Pan. 2022. "The Pervasive Presence of Chinese Government Content on Douyin Trending Videos." *Computational Communication Research*.

Lu, Y. and C. Shen. 2023. "Unpacking Multimodal Fact-Checking: Features and Engagement of Fact-Checking Videos on Chinese TikTok (Douyin)." *Social Media + Society*.

Metzger, M.J., A.J. Flanagin, and B.R. Medders. 2010. "Social and Heuristic Approaches to Credibility Evaluation Online." *Journal of Communication* 60(3): 413-439.

Molyneux, L. and M. Coddington. 2020. "Aggregation, Clickbait and Their Effect on Perceptions of Journalistic Credibility and Quality." *Journalism Practice* 14(4): 429-446.

Munger, K. 2020. "All the News That's Fit to Click: The Economics of Clickbait Media." *Political Communication*.

Naveed, W., Z.A. Uzmi, and Z.A. Qazi. 2025. "ThumbnailTruth: A Multi-Modal LLM Approach for Detecting Misleading YouTube Thumbnails Across Diverse Cultural Settings."

Oster, E. 2019. "Unobservable Selection and Coefficient Stability: Theory and Evidence." *Journal of Business & Economic Statistics* 37(2): 187-204. https://doi.org/10.1080/07350015.2016.1227711.

Peng, Y., I. Lock, and A.A. Salah. 2024. "Automated Visual Analysis for the Study of Social Media Effects: Opportunities, Approaches, and Challenges." *Communication Methods and Measures*.

Powell, T.E., H.G. Boomgaarden, K. De Swert, and C.H. de Vreese. 2015. "A Clearer Picture: The Contribution of Visuals and Text to Framing Effects." *Journal of Communication*.

Scott, K. 2021. "You Won't Believe What's in This Paper! Clickbait, Relevance and the Curiosity Gap." *Journal of Pragmatics* 175: 53-66.

Shin, J., C. DeFelice, and S. Kim. 2025. "Emotion Sells: Rage Bait vs. Information Bait in Clickbait News Headlines on Social Media." *Digital Journalism*.

Spence, M. 1973. "Job Market Signaling." *Quarterly Journal of Economics*.

Valkenburg, P.M. and J. Peter. 2013. "The Differential Susceptibility to Media Effects Model." *Journal of Communication* 63(2): 221-243.

VanderWeele, T.J. and P. Ding. 2017. "Sensitivity Analysis in Observational Research: Introducing the E-Value." *Annals of Internal Medicine* 167(4): 268-274. https://doi.org/10.7326/M16-2607.

Vultee, F., G.S. Burgess, D. Frazier, and K. Mesmer. 2022. "Here's What to Know About Clickbait: Effects of Image, Headline and Editing on Audience Attitudes." *Journalism Practice*.

Wang, Y., B. Hu, C. Tang, and X. Yang. 2025. "Decoding Clickbait: The Impact of Clickbait Types and Structures on Cognitive and Emotional Responses in Online Interactions." *Cyberpsychology, Behavior & Social Networking*.

Xu, Z., M. Laffidy, and L. Ellis. 2023. "Clickbait for Climate Change: Comparing Emotions in Headlines and Full-Texts and Their Engagement." *Information, Communication & Society* 26(10): 1915-1932.

Yang, A., J. Pan, J. Lin, R. Men, Y. Zhang, J. Zhou, and C. Zhou. 2022. "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese."

Yoon, Y., S. Yoon, and K. Park. 2024. "Assessing News Thumbnail Representativeness: Counterfactual Text Can Enhance the Cross-Modal Matching Ability." *Findings of the Association for Computational Linguistics: ACL 2024*.

Zhang, X. and S. Zhou. 2019. "Clicking Health Risk Messages on Social Media: Moderated Mediation Paths Through Perceived Threat, Perceived Efficacy, and Fear Arousal." *Health Communication* 34(11): 1359-1368.

---

<!-- 中文译稿结束 -->
