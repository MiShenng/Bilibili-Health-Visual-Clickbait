# Buying Attention, Not Endorsement: Multimodal Clickbait and the Bifurcation of User Engagement in Health-Science Videos on Bilibili

<!-- Word count target: ~9000 | Journal: Health Communication | Mode: INSERT/CITATION (v4) -->
<!-- v1 (DRAFT): 2026-05-25 ~ 10:28 — initial draft, 13 [CITATION NEEDED] -->
<!-- v2 (REVISE): 2026-05-25 ~ 10:55 — +6 sources from clickbait_paper/; pool 27→33 -->
<!-- v3 (REVISE): 2026-05-25 ~ 11:30 — deep-dive +12 more sources; pool 33→45 -->
<!-- v4 (INSERT): 2026-05-25 ~ 15:55 — /scholar-citation INSERT mode resolved last 4 SOURCE NEEDED: -->
<!--   • Oster 2019 (JBES, DOI 10.1080/07350015.2016.1227711) — δ for OVB                  -->
<!--   • VanderWeele & Ding 2017 (Annals Int Med, DOI 10.7326/M16-2607) — E-value          -->
<!--   • Arel-Bundock, Greifer & Heiss 2024 (JSS 111(9), DOI 10.18637/jss.v111.i09) — marginaleffects -->
<!--   • Bilibili Inc. 2024 Q3 6-K SEC filing — MAU statistic (corrected from "300M" to    -->
<!--     verified "348M Q3 2024" per Form 6-K)                                              -->
<!-- Pool: 45 → 49 entries. Zero [CITATION NEEDED] markers remain in main body or References. -->
<!--   v3 added:                                                                            -->
<!--     • Molyneux & Coddington 2020 — clickbait → credibility (Journalism Practice)       -->
<!--     • Kuiken et al. 2017 — digital newspaper headline effectiveness                    -->
<!--     • Guo et al. 2026 — Chinese local media headline → clicks (same-language anchor)   -->
<!--     • Xu, Laffidy & Ellis 2023 — clickbait + emotion + engagement (climate)            -->
<!--     • Khawar & Boukes 2025 — Twitter clickbait + engagement (Digital Journalism)        -->
<!--     • Liu et al. 2023 — Chinese digital news trust (folk theories)                      -->
<!--     • Keib et al. 2018 — emotionally valenced images → attention/selection/sharing      -->
<!--     • Metzger, Flanagin & Medders 2010 — heuristic credibility evaluation               -->
<!--     • Valkenburg & Peter 2013 — DSMM (differential susceptibility to media effects)     -->
<!--     • Jones et al. 2015 — Health Belief Model in communication research                 -->
<!--     • King & Lazard 2020 — visual health communication (infodemic response)             -->
<!--     • Araujo, Lock & van de Velde 2020 — AVCA protocol for CV in communication          -->
<!-- Sections drafted: Title + Abstract + Introduction + Literature Review + Theory + Hypotheses + Data and Methods -->
<!-- NOT drafted: Results, Discussion, Conclusion (pending analysis) -->
<!-- Verified Citation Pool: 45 entries                                                      -->
<!-- Remaining [CITATION NEEDED]: Bilibili 2024 annual report; Arel-Bundock 2024;           -->
<!--                              Oster 2019; VanderWeele-Ding 2017 (software/statistics)   -->

---

## Abstract

Short-video platforms have become a major entry point for public health information, yet the visual cues that producers attach to thumbnails remain undertheorized in health communication. This study examines whether *multimodal clickbait*—the use of dramatized facial emotion, threat imagery, and dense text overlay on video thumbnails—is associated with a distinct *bifurcation* of user engagement on Bilibili, China's largest long-form Chinese video platform. Drawing on curiosity-gap, threat-arousal, and signaling perspectives [@scott2021you; @lang2000limited; @bird2005signaling; @donath2007signals], we predict that multimodal clickbait increases low-cost attention (views, likes) more than high-cost endorsement (coins, favorites, shares), and that thumbnail-title representativeness moderates this gap. We test these predictions on a corpus of 4,562 unique health-science videos posted between June 2016 and May 2026, collected via Bilibili's public search API across 28 keywords spanning five health themes. Each video is paired with its locally archived thumbnail, six interaction metrics, and uploader-level attributes (follower count, platform verification, original/reposted status). Visual constructs are coded using a three-tier hybrid protocol: 500 thumbnails are double-blind coded by two trained annotators against a five-dimension codebook, the full corpus is processed by computer-vision (PaddleOCR, RetinaFace + FER) and a vision-language model (Claude Opus 4.7), and convergent validity between human and computational scores is established before scaling. We estimate negative binomial and zero-inflated negative binomial models with cluster-robust standard errors at the uploader level, and report between-uploader and within-uploader fixed-effects specifications in parallel. We pre-register five hypotheses (H1a–H4) and one exploratory three-way interaction (H5). The design is observational; we do not make causal claims and bound unobserved confounding using Oster δ and E-values. This pre-results manuscript sets out the theoretical motivation, measurement protocol, and analytic plan; empirical results will be added after pre-registration on the Open Science Framework. *Keywords*: visual clickbait, health communication, Bilibili, multimodal, user engagement, computational measurement.

---

## 1. Introduction

A Bilibili user opening the platform's search page for "癌症 早期信号" (early signals of cancer) sees a vertical stack of video thumbnails before reading a single full sentence of medical content. One thumbnail shows a physician in a white coat behind a bold yellow caption reading "千万别乱用，用错后果严重" (do not misuse, the consequences are severe) flanked by three red exclamation marks. Another shows a small child crying next to an elderly man in a wheelchair, with a yellow caption asking strangers not to ignore them. A third shows the same physician set against a desktop with a clinical report, captioned only "糖尿病出现口干口渴 有3种情况" (when diabetes patients experience dry mouth and thirst, there are three possibilities). All three appear in the same search result. All three are tagged as health education by their uploaders. Yet they ask the viewer to do very different things, and they are likely to be rewarded in very different ways by the platform's distinctive engagement architecture.

Bilibili distinguishes itself from short-video competitors by retaining a layered, cost-graded set of user actions. Viewers can play (`play`), like (`like`), post a danmaku floating comment (`danmaku`), favorite for later retrieval (`favorites`), share externally (`share`), and, crucially, spend a platform-rationed token to "coin" the video (`coin`). Coins are scarce: every user is allotted a small daily quota and they may give at most one coin to any single video, so coining is an act that the platform's design forces users to economize. In the broader literature on platform engagement, this stratification is unusual. Most platforms collapse engagement into views, likes, comments, and shares; few build in an explicit, tokenized, cost-bearing form of endorsement [@lu2023unpacking]. Bilibili therefore offers a natural empirical environment in which to ask whether different *types* of engagement respond differently to the same content cue.

The cue we focus on is the video thumbnail. Thumbnails are the primary visual signal in a feed-based platform: they appear before any video plays, occupy most of the user's field of view, and increasingly carry a high density of designed elements—facial expressions, threat imagery, color contrast, and overlaid text that essentially serves as a second, parallel headline. A growing body of work in computational communication treats thumbnails as standalone units of analysis [@lu2022pervasive; @al-ali2024extra; @limpijankit2025detecting; @naveed2025thumbnailtruth]. In journalism studies, "clickbait" has long denoted headline strategies designed to maximize click-through at potential cost to information quality or downstream trust [@munger2020news; @vultee2022clickbait; @shin2025emotion; @wang2025decoding]. We extend this conceptual move to the visual plane and ask: when health-science videos on Bilibili use multimodal clickbait cues on their thumbnails, what kind of user engagement do those cues actually produce?

Our argument has three parts. First, we treat Bilibili's engagement metrics as forming a *cost hierarchy*. Viewing and liking are low-cost actions; coining, favoriting, and external sharing impose a real budgetary or social cost on the user [@dong2025impact]. Second, drawing on curiosity-gap theory [@scott2021you; @blom2015click], the limited-capacity model of mediated message processing [@lang2000limited], visual framing research [@powell2015clearer; @geise2025effects], experimental evidence that emotionally valenced images shape both attention and selection on social-media news [@keib2018picture], and the broader finding that clickbait headlines depress perceived credibility even as they raise click rates [@molyneux2020aggregation; @khawar2025analyzing], we expect multimodal clickbait to be more strongly associated with low-cost attention than with high-cost endorsement. Third, we expect this gap to be moderated by *thumbnail–title representativeness*: when the thumbnail accurately previews what the title (and, by extension, the video) actually delivers, high-cost endorsement is more likely to materialize, consistent with both the image–text congruence literature [@li2020picture; @cao2025relevancy; @yoon2024assessing] and eye-tracking evidence on safety-message attention [@klein2020when].

We test these predictions on 4,562 unique health-science videos posted on Bilibili between June 2016 and May 2026. The corpus was collected through the platform's public search API across 28 Chinese-language keywords spanning five health-content themes: general health education, chronic disease, oncology and screening, lifestyle, and pre-defined clickbait stem phrases ("medical doctor reminds you," "doctors finally admit," "this habit causes cancer"). For each video we collected complete API metadata, six interaction metrics, uploader-level attributes including follower count and platform verification, and the cover thumbnail itself. We code the visual constructs through a three-tier hybrid protocol that combines double-blind human annotation on a 500-thumbnail subsample, computer-vision pipelines for facial emotion and text-overlay geometry, and vision-language model scoring on the full corpus, with explicit convergent validity checks against the human gold standard.

This study is observational and pre-results. We deliberately separate the design and measurement portion of the project, presented here, from the empirical estimation portion, which will follow Open Science Framework pre-registration. Our purpose in the present paper is to (a) lay out the theoretical case for treating visual clickbait as multimodal and engagement as cost-graded; (b) document a measurement protocol that audits hybrid human–machine coding in a way that subsequent work can adopt; and (c) specify in advance an analytic plan that handles the heavy zero inflation in the high-cost engagement variables, the within-uploader clustering, and the well-known limits of associational inference under recommender-system confounding [@lu2021capturing]. We organize the paper around four research questions:

- **RQ1**. To what extent do health-science videos on Bilibili use multimodal clickbait cues (dramatized emotion, threat imagery, dense text overlay) on their thumbnails?
- **RQ2**. Is multimodal clickbait associated with higher low-cost engagement (views, likes) than with high-cost endorsement (coins, favorites, shares)?
- **RQ3**. Does thumbnail–title representativeness moderate the gap between low-cost attention and high-cost endorsement?
- **RQ4**. Does the bifurcation pattern depend on uploader verification status?

The remainder of the paper proceeds as follows. Section 2 reviews three literatures we draw on: visual clickbait and thumbnail design, image–text congruence and processing fluency, and platform-level engagement stratification with particular attention to Bilibili. Section 3 develops our theoretical argument and formalizes five hypotheses. Section 4 describes the corpus, the codebook, the hybrid annotation pipeline, and the planned analysis, including a candid statement of the causal boundary of the design.

---

## 2. Literature Review

### 2.1 From clickbait headlines to multimodal clickbait thumbnails

Clickbait research originated in journalism studies as an attempt to characterize headline strategies that withhold information in order to maximize click-through. Linguistic analyses of online news identified "forward-reference"—the use of cataphoric or deictic devices that promise content the reader has not yet seen—as a signature device for inducing anticipation [@blom2015click]. Relevance-theoretic work extended this account by showing that successful clickbait headlines exploit definite referring expressions and intensifiers to construct an information gap that only the click can close [@scott2021you]. The economics of clickbait have been formalized as a strategic interaction between an attention-constrained reader and a revenue-constrained publisher, in which exaggeration is a rational response to a thin attention market [@munger2020news]. Large-scale corpus analyses of digital newspaper headlines have isolated the specific linguistic features—signal words, length, sentiment, numeric specificity—that predict click-through in production environments [@kuiken2017effective], and recent comparative work has documented that online-native outlets use sensationalized headlines more heavily than legacy outlets, with engagement consequences that differ across user segments [@khawar2025analyzing]. A parallel line of work in non-English settings shows that the same headline mechanics travel to Chinese-language local media, where length, question framing, and numerical claims predict clicks net of content [@guo2026impact]. Empirical work in this tradition has further shown that clickbait headlines impose downstream costs on perceptions of source credibility [@molyneux2020aggregation], on subsequent attitudes toward the outlet [@vultee2022clickbait], and on willingness to share content; emotional framing—particularly rage-bait—operates differently from information-deficit framing [@shin2025emotion; @xu2023clickbait]. Reader-side experimental work using EEG and behavioral measures finds that different *types* of clickbait (hyperbole, insinuation, visual rhetoric, puzzle) elicit measurably different cognitive and affective responses [@wang2025decoding]. The Persuasion Knowledge Model offers a broader lens on why this matters: once readers recognize a persuasive intent, their downstream evaluations of source and content change [@isaac2025thirty].

Two extensions of this body of work motivate the present study. The first is the move to non-Western, platform-native, and visually dominant settings. Lu and Pan, in their study of the Chinese government's clickbait practices, demonstrated that clickbait is not merely a tabloid phenomenon but a structural response to algorithmic visibility pressure [@lu2021capturing]. Their follow-up work on Douyin showed that visually dominant short-video platforms have generated a distinctive grammar of attention-maximizing video features, including high brightness, warm color, short duration, and visual similarity to celebrity content [@lu2022pervasive]. Their analysis of Chinese-language fact-checking videos on Douyin further demonstrated that engagement and informational quality respond to distinct multimodal features [@lu2023unpacking]. The second extension is the move from text headlines to visual thumbnails. Al-Ali and Hamzeh, analyzing Arabic-language clickbait thumbnails on YouTube, showed that visual cues, overlaid text, and embedded punctuation jointly constitute a meaning system that the text-only clickbait literature systematically misses [@al-ali2024extra]. ThumbnailTruth, a recent multi-modal LLM benchmark across cultures, formalized the detection problem and reported that culturally diverse thumbnails resist single-language solutions [@naveed2025thumbnailtruth]. Limpijankit and Kender, using computational aesthetics, showed that systematic cultural differences in thumbnail design can be measured at scale [@limpijankit2025detecting]. We build on these moves by treating *visual clickbait* as multimodal: a thumbnail is clickbait not only when its overlaid text plays on a curiosity gap, but also when its facial expressions are exaggerated, its threat imagery is salient, and its text layer crowds out the underlying image.

### 2.2 Image–text congruence, processing fluency, and downstream engagement

A second body of work, mostly in marketing and computational social science, asks how the *relation* between an image and its accompanying text shapes user behavior. Li and Xie's analysis of branded social-media posts established that image content, image quality, the presence of human faces, and image–text matching each independently predict engagement [@li2020picture]. Subsequent work using deep-learning measures of image–text congruence has complicated the simple "more congruence is better" intuition. Cao, Li, and Zhang showed that the relationship between image–text congruence and consumer preference can be non-monotonic: very high congruence delivers fluency, very low congruence delivers surprise and elaboration, and the middle ground may be the least attractive [@cao2025relevancy]. In a natural-language-processing reformulation, Yoon and colleagues argued that news-thumbnail representativeness can be measured by counterfactual text generation and that representativeness is a distinct construct from headline–image similarity [@yoon2024assessing]. For visually dominant platforms with high content volume, the question is no longer whether congruence matters but *which engagement metric* it matters for. This is the empirical opening we exploit.

Visual framing research has documented that images and text contribute non-redundantly to framing effects, with text shifting opinion and images shifting behavioral intention [@powell2015clearer]. Eye-tracking and selection experiments on social-media news further demonstrate that emotionally valenced images alter not only what users *attend to* but also what they *select to read* and *share*, producing a measurable wedge between initial attention and deeper engagement [@keib2018picture]. A recent systematic review of forty-five years of visual framing studies found that the literature has paid disproportionate attention to single-image stimuli and has lagged in multimodal, platform-native, behavioral-outcome studies [@geise2025effects]. The visual misinformation literature reaches a parallel conclusion: visual misleading cues are systematically understudied [@heley2022missing], and their effects on credibility and downstream behavior are uneven across cultural and platform contexts [@liu2025understanding]. Eye-tracking evidence on health-safety messages specifically shows that mismatch between an accompanying image and the textual message degrades attention to and retention of the safety information itself [@klein2020when], suggesting that representativeness is not a stylistic preference but a determinant of comprehension. In health communication more broadly, scholarly calls have urged researchers to move from descriptive visual analysis to outcome-oriented studies that connect visual features to engagement and infodemic-relevant behavior [@king2020advancing]. Image-driven engagement on Twitter/X varies systematically with the emotional content of climate imagery [@bravo2025global], and automated visual analysis is now a tractable empirical strategy for studying social-media health effects [@peng2024automated; @araujo2020automated].

### 2.3 Platform-level engagement stratification, Bilibili, and danmaku

A third literature, focused on the Chinese-language video platform Bilibili and its corporate cousin Douyin, supplies our outcome side. Bilibili's distinctive feature is its dual register of viewer action: alongside the standard view–like–comment–share suite, it preserves a *danmaku* layer of synchronously displayed comments and a *coin* token that the platform deliberately rations. The fact-checking video literature has begun to take this stratification seriously. Lu and Shen, analyzing Chinese-language fact-checking videos on Douyin, distinguished engagement signals that respond to multimodal features from those that do not [@lu2023unpacking]. On Bilibili itself, Chen reported that danmaku interactions are predicted by content features that differ from those predicting comment volume, suggesting that danmaku occupies a behaviorally distinct slot in the engagement hierarchy [@chen2025danmaku]. Dong and colleagues developed a typology of danmaku ritual types (e.g., greeting, projection, evaluation) and showed that ritual type, not raw danmaku volume, predicts downstream digital engagement [@dong2025impact]. These findings converge on a single methodological point: collapsing engagement into a single score loses theoretical information.

Signaling theory, originally developed in labor economics [@spence1973job] and ported to online social environments by Donath [@donath2007signals], offers a complementary lens. Costly signals are informative precisely because they are costly; cheap signals are common precisely because they are cheap [@bird2005signaling]. Applied to Bilibili, this implies that a coin or a favorite carries information that a view or a like does not, because the user has paid a real cost (a rationed token; the marginal storage cost of a future-self bookmark) to issue it. The empirical question is whether multimodal clickbait cues, which are designed to maximize a cheap signal (clicks), do or do not also maximize the costly signal. The Persuasion Knowledge Model predicts that once viewers recognize persuasive intent, they will dampen costly endorsement even as they continue to deliver cheap engagement [@isaac2025thirty]. We do not test that mechanism directly here, but it underlies our directional predictions.

A separate strand of computational social science work documents how scalable, multi-modal video analysis is now feasible at the scale of tens of thousands of videos, but cautions that automated visual measurement requires explicit construct-validity audits against human annotation [@edelmann2020computational; @peng2024automated]. This methodological consensus shapes our annotation design (Section 4).

### 2.4 What is missing

The clickbait, image–text congruence, and Bilibili engagement literatures have grown rapidly but have not yet been joined. Clickbait research has remained largely text-centric; the few multimodal clickbait studies are concentrated in English- and Arabic-language news settings [@al-ali2024extra; @naveed2025thumbnailtruth]. Image–text congruence research is concentrated in branded marketing settings where the outcome is purchase or attitude, not the engagement-cost ladder. Bilibili engagement work is most developed at the danmaku layer and has not, to our knowledge, addressed the question of whether different visual cue types map differentially onto the platform's cost hierarchy. Health-science content, with its distinctive stakes around credibility and downstream behavior, has been studied for content quality but not for the upstream visual cues that determine whether a viewer enters the video at all. This study is positioned at the intersection of these three gaps.

---

## 3. Theory and Hypotheses

### 3.1 A cost-graded conception of engagement

The general framework for our predictions is the Differential Susceptibility to Media Effects Model (DSMM), which holds that media-effect estimates depend on the interaction of dispositional, developmental, and social susceptibility with response states that mediate the effect [@valkenburg2013differential]. We use DSMM as a meta-frame: rather than predicting a single average effect of multimodal clickbait, we predict a *patterned* effect that differs across engagement cost tiers because the dispositional cost of each action shapes which response state (cheap attention vs. costly endorsement) dominates.

Our theoretical starting point is that user engagement on Bilibili is not a single quantity but an ordered set of actions that differ in the cost they impose on the user. *View* costs the user only the marginal attention required to begin a video. *Like* costs the user a tap. *Danmaku* costs the user the time and self-disclosure required to write and submit a public synchronous comment. *Favorite* costs the user the marginal cognitive overhead of categorizing the video as worth re-watching. *Share* costs the user a social risk: the reputational implication of recommending the video to an external audience. *Coin*, finally, costs the user a fraction of a daily platform-rationed budget and is irrevocable: a coin spent here cannot be spent elsewhere today. We do not claim that all users perceive these costs identically; we claim only that the ordering is robust enough at the population level to motivate analytic separation.

This framing draws on signaling theory's core distinction between cheap and costly signals [@spence1973job; @bird2005signaling; @donath2007signals]. The information content of a signal in equilibrium is increasing in its cost: cheap signals are common and uninformative; costly signals are rare and diagnostic. Applied to a corpus of videos, this implies that the same content feature can produce statistically distinct patterns in cheap and costly engagement, and that pooling them obscures rather than reveals the underlying behavior.

### 3.2 Why multimodal clickbait should buy attention but not endorsement

Multimodal clickbait is a content strategy that maximizes the probability of a click by amplifying perceptually salient cues in the thumbnail. We identify three such cues: *emotion intensity* (exaggerated facial expressions, particularly fear, shock, or disgust); *threat imagery* (medical instruments, lesions, distressed bodies, red warning marks); and *text overlay intensity* (high-coverage, high-contrast captions that pre-stage a curiosity gap). Each cue is grounded in a distinct mechanism. The limited-capacity model of mediated message processing holds that high-arousal, emotionally evocative stimuli automatically allocate more cognitive resources to encoding, increasing both initial attention and subsequent message recall [@lang2000limited]. Consistent with this account, emotion-laden imagery is processed faster than neutral imagery, emotional intensity predicts virality of social-media content [@bravo2025global; @shin2025emotion], and experimental work has documented that emotionally valenced images in news feeds shape attention, story selection, and downstream sharing intent [@keib2018picture]. Threat imagery activates the threat-salience channel of fear appeals; classical health-behavior work formalizes this channel within the Health Belief Model, in which perceived threat operates jointly with perceived efficacy to produce action [@jones2015health]. On social media specifically, perceived threat and perceived efficacy interact in a moderated-mediation path that elevates click intention through fear arousal but dampens it when efficacy is low [@zhang2019clicking]. Text-overlay intensity functions as a second headline embedded in the image, multiplying surface area for curiosity-gap construction [@al-ali2024extra; @scott2021you].

A common feature of these mechanisms is that they target the *entry* decision—whether to click—rather than the *post-entry* decision of whether to endorse. Reader-side clickbait studies are consistent with this asymmetry: clickbait headlines reliably increase clicks but do not reliably increase trust, sharing, or other downstream measures [@vultee2022clickbait; @shin2025emotion; @wang2025decoding]. The Persuasion Knowledge Model gives this asymmetry a name: once viewers recognize that a thumbnail is engineered to maximize their click probability, they may continue to click while withholding the costly signals that would otherwise indicate endorsement [@isaac2025thirty]. On Bilibili, the costly signals are precisely the rationed coin and the future-oriented favorite and share. We therefore predict a bifurcation:

- **H1a**. *Multimodal clickbait intensity is positively associated with low-cost engagement (views, likes).*
- **H1b**. *Multimodal clickbait intensity is more weakly associated with high-cost endorsement (coins, favorites, shares) than with low-cost engagement.*

H1b is a *comparative* hypothesis: it predicts that the standardized coefficient on the multimodal clickbait index is smaller in the high-cost equation than in the low-cost equation, not that it is zero or negative. We test it with a non-parametric bootstrap of the coefficient difference (Section 4.6).

### 3.3 Why information gap should be treated separately

In our preliminary coding (Section 4.3) and consistent with the curiosity-gap tradition, we distinguish *information gap*—a property of the title's promise rather than of the thumbnail's image—from the three visual clickbait dimensions above. Information gap is the extent to which the title and the visible thumbnail caption deliberately withhold the punch line of the video. Examples in our corpus include "this habit causes cancer" (which kind of habit?), "doctors finally admit" (admit what?), and "if your physical exam shows these signs, do not ignore them" (which signs?). Linguistic work on online news headlines identifies these constructions as deictic forward-references: the headline uses a referring expression whose antecedent is withheld, generating an anticipation that only the click can resolve [@blom2015click; @scott2021you]. Theoretically, the information-gap mechanism is cognitive rather than affective: it works by making the viewer aware of a knowledge deficit and offering the click as the closure. Because the gap is constructed in text, conflating it with image-side cues such as facial emotion would misname the construct. We therefore model information gap as a *separate* predictor:

- **H1c**. *Information-gap intensity is positively associated with low-cost engagement and more weakly associated with high-cost endorsement, in parallel to H1a–H1b.*

### 3.4 Why thumbnail–title representativeness should moderate the gap

Representativeness is the property of a thumbnail that it accurately previews what the title—and by extension the video—is about. A highly representative thumbnail of a video titled "what 3 things to know when diabetes patients experience dry mouth" might display a doctor with a clinical report and an overlay listing three items; an unrepresentative thumbnail of the same video might display a generic stock image of a glass of water. Two literatures lead to opposing predictions, and the resolution is empirical.

The processing-fluency tradition holds that congruent image–text pairs are easier to process, more credible-feeling, and more likely to convert attention into action [@li2020picture]. Eye-tracking work in health communication adds a behavioral mechanism: when an image and the accompanying message do not match, viewers' attention shifts inefficiently between the two modalities, and retention of the safety information itself is degraded [@klein2020when]. The curiosity-discrepancy tradition, by contrast, holds that mismatch generates surprise and elaboration that can themselves be conversion-enhancing under some conditions [@cao2025relevancy]. We expect the fluency channel to dominate for *high-cost* endorsement, because favoriting and coining require the viewer to make a forward-looking judgment about content value, and that judgment depends on whether the thumbnail's promise was kept. We expect representativeness to have a weaker association with low-cost attention, because attention is captured at the moment of the click, before any representativeness comparison can be made:

- **H2**. *Thumbnail–title representativeness is positively associated with high-cost endorsement.*
- **H3**. *The positive association between representativeness and high-cost endorsement is stronger than its association with low-cost engagement.*

### 3.5 Medical authority cues and verification status

Health-science content carries source-credibility implications that general clickbait research does not. A white coat, a clinical report, or a hospital backdrop function as visual signals of medical authority. The same cues, however, are routinely co-opted by misleading health content; recent commentary in *Science Communication* has called for systematic research on this dual-use property of visual health information [@heley2022missing]. Users themselves rely heavily on social and heuristic shortcuts—rather than effortful evaluation—when assessing online credibility, and visual authority cues are exactly the kind of cognitively cheap, "good-looking" signal that heuristic processing privileges [@metzger2010social]. In the Chinese-language digital news environment, recent qualitative work documents that users articulate folk theories about source trustworthiness that are sensitive to platform context and to perceived sensationalism [@liu2023factors], reinforcing the expectation that visual authority cues operate differently when paired with high versus low clickbait intensity. The signaling-theory expectation is that authority cues will amplify high-cost endorsement, but only when they are *consistent* with the underlying content; when authority cues coexist with high clickbait intensity, viewers may interpret the combination as packaging rather than credentialing, dampening the endorsement response [@isaac2025thirty]. We formalize the main effect:

- **H4**. *Medical authority visual cues are positively associated with high-cost endorsement.*

Bilibili distinguishes uploaders by formal verification. Verified accounts (`is_official == TRUE`) include certified medical professionals, institutional channels, and accredited media outlets. The signaling and reader-side literatures both suggest that the bifurcation in H1 should be *attenuated* among verified accounts: viewers may extend more trust to a verified uploader and convert clickbait-driven attention into high-cost endorsement more readily; or, alternatively, viewers may apply a stricter standard to a verified uploader and dampen endorsement when verified accounts use clickbait. Because both directions are theoretically defensible, we treat the moderation as exploratory:

- **H5 (exploratory)**. *The bifurcation pattern in H1 is moderated by uploader verification; we do not pre-commit to a direction.*

H5 is reported in the appendix only; the primary confirmatory family is H1a–H4.

### 3.6 What we are not claiming

We are not claiming a causal effect of multimodal clickbait on engagement. Our design is observational. Bilibili's recommender system constitutes a substantial unobserved confounder of both the visual cues that uploaders choose and the engagement that videos receive. We adopt three protective measures: explicit associational language throughout, sensitivity bounds (Oster δ and E-values) on the principal coefficients, and a parallel within-uploader specification that absorbs all time-invariant uploader characteristics, including the uploader's tendency to be promoted by the recommender system. We do not claim that even the within-uploader specification identifies a causal effect, only that it strengthens the associational inference by partialing out a large class of confounders.

---

## 4. Data and Methods

### 4.1 Platform and corpus

Bilibili (bilibili.com) is the largest long-form Chinese-language video platform, founded in 2009 and best known for its synchronous danmaku comment layer and its tokenized "coin" endorsement system. Unlike its short-video competitors, Bilibili preserves long-form content alongside short videos and retains an explicit four-way action set (`like`, `coin`, `favorite`, `share`) plus the floating-comment `danmaku` channel. As of the third quarter of 2024, Bilibili reported an average of 348 million monthly active users [@bilibili2024q3]. We choose Bilibili because its engagement architecture, more than any other Chinese-language platform, separates cheap and costly user actions at the design level.

We collected the corpus through the platform's public search API on May 24, 2026. The search API returns the same ranked list that the platform serves to non-logged-in users entering a keyword query, with the additional functionality of pagination and sort-order control. For each of 28 Chinese-language keywords (Table 1), we issued three sort queries—`totalrank` (relevance), `pubdate` (recency), and `click` (popularity)—and crawled up to fifteen pages per query. Keywords were organized into five thematic clusters: general health education (e.g., 健康科普, 医生提醒, 体检报告; five keywords), chronic disease (糖尿病, 高血压, 心脏病, 脂肪肝; four keywords), oncology and screening (癌症 早期信号, HPV 疫苗, 肺癌 科普; three keywords), lifestyle (减肥 科学, 脱发 医生, 睡眠 健康, 饮食健康; four keywords), and pre-defined clickbait stem phrases (e.g., 医生提醒 千万别, 医生终于说了, 这个习惯 致癌; twelve keywords including short-form variants). The clickbait-stem cluster was included deliberately to ensure adequate variation in our principal independent variable; we adjust for this by including keyword category fixed effects in all primary models and by reporting a leave-one-keyword-out robustness check.

[Table 1 about here]

For each returned video, we collected complete metadata (`bvid`, `aid`, title, description, publication timestamp, duration, B-station category `tname`, original/reposted status `copyright`), six interaction metrics (views, likes, coins, favorites, shares, danmaku), uploader-level attributes (`mid`, follower count, platform verification status, channel signature, uploader level), and the cover thumbnail (JPG, locally archived). After deduplication on `bvid`, the working corpus contains 4,562 unique videos from 2,731 unique uploaders (mean = 1.67 videos per uploader; median = 1; maximum = 47). The publication dates span June 22, 2016 to May 24, 2026, with 71 percent of videos published in 2024–2026. All interaction metrics represent a single cross-sectional snapshot taken within a six-hour window on May 24, 2026; we therefore introduce `video_age_days` (the number of days between publication and crawl) as a primary control. Thumbnail download succeeded for 4,564 images, providing 100 percent coverage of analyzable videos.

### 4.2 Outcome variables and their distributions

We treat the six interaction metrics as an ordered set of engagement actions stratified by cost. The full descriptive distribution is reported in Table 2. Three features of the distribution are decisive for the modeling strategy.

[Table 2 about here]

First, all six outcomes are heavily right-skewed, with maxima orders of magnitude above their medians. Second, the rate of structural zeros differs sharply across outcomes: 1.3 percent for views, 5.1 percent for likes, 16.6 percent for favorites, 27.0 percent for shares, 30.5 percent for comments, 36.5 percent for coins, and 45.8 percent for danmaku. Third, the high-cost outcomes (coins, shares, danmaku) all exhibit zero-inflation rates above 25 percent, indicating that a non-trivial share of videos generate genuinely no costly endorsement. We accordingly fit negative binomial (NB) models to the low-zero outcomes (views, likes, favorites) and zero-inflated negative binomial (ZINB) models to the high-zero outcomes (coins, shares, danmaku). The inflation equation in the ZINB specification includes `log_followers` and `video_age_days`, which are theoretically the variables most likely to predict structural absence of any endorsement.

### 4.3 Codebook for visual constructs

Five visual constructs are coded per thumbnail: a binary topic-relevance gate, three image-side clickbait dimensions, one text-side curiosity-gap dimension, and a four-component medical-authority composite. The complete codebook with operational definitions, exemplar images, calibration rules, and adjudication procedures is included as Supplementary Material (`Data process/annotation/codebook_visual_clickbait.md`). We summarize the constructs here.

**Topic relevance** (binary, gate variable). Coded `1` if the video is recognizably a health-education attempt directed at a general audience, `0` otherwise. The gate excludes emotional appeals (e.g., medical-crowdfunding videos that use health imagery but are not educational), fitness routines mislabeled as health science, and entertainment content that uses health keywords for retrieval but does not deliver health information. Videos with `topic_relevance == 0` are excluded from all primary models.

**Emotion intensity** (ordinal, 0–3). Codes the degree of exaggerated affective display on visible human faces in the thumbnail: 0 = neutral or no face; 1 = mild expression; 2 = pronounced surprise, concern, or fear; 3 = extreme dramatized affect (open-mouth shock, exaggerated grimaces, staged crying). The construct is grounded in the high-arousal literature on viral content [@bravo2025global; @shin2025emotion].

**Threat imagery** (ordinal, 0–2). Codes the salience of visual threat cues: 0 = none; 1 = mild medical-setting cues (white coats, clinical instruments, hospital backdrops) without explicit threat; 2 = explicit threat cues (lesions, distressed bodies, red warning marks, dramatic before/after images). The construct is grounded in the visual-misinformation literature [@heley2022missing; @liu2025understanding] and in social-media fear-appeal research that has documented how perceived threat shapes click intention [@zhang2019clicking].

**Text overlay intensity** (ordinal, 0–3). Codes the proportion of thumbnail area, font contrast, and emphasis density of overlaid text: 0 = no overlay; 1 = minimal caption; 2 = mid-density (a single short caption with limited emphasis); 3 = high-density (large captions covering 30 percent or more of the thumbnail area, often with color-block backgrounds and exclamation marks). The construct is grounded in the multimodal clickbait literature [@al-ali2024extra; @naveed2025thumbnailtruth] and in evidence that image–text mismatch alters cross-modal attention allocation [@klein2020when].

**Information gap** (ordinal, 0–2). Codes the extent to which the title and any thumbnail caption deliberately withhold the substantive punch line of the video: 0 = no withholding (the title fully describes the content); 1 = partial withholding (the title identifies the topic but withholds the resolution); 2 = explicit curiosity gap (the title constructs a "this thing," "these signs," "what really happened" puzzle). Operationalization follows the forward-reference and relevance-theoretic accounts of clickbait headlines [@blom2015click; @scott2021you]. This construct is text-side, not image-side, and is modeled separately from the visual clickbait dimensions.

**Medical authority cues** (4 binary items summed, 0–4). The four items are: presence of a white coat or scrubs; presence of clinical instruments (stethoscope, otoscope, syringe); presence of a clinical report, scan, or chart; presence of an institutional logo or identifying credential. The construct is grounded in source-credibility theory and in the visual-misinformation literature on authority signaling [@isaac2025thirty; @liu2025understanding].

### 4.4 Hybrid annotation pipeline

Visual constructs are scored using a three-tier hybrid protocol that combines human gold-standard annotation, computer-vision feature extraction, and vision-language model coding. The protocol is designed to balance the construct-validity advantages of human coding against the scale advantages of automated measurement, and to make the trade-off legible to readers.

**Tier 1: Human gold standard (N = 500).** We draw a stratified random subsample of 500 thumbnails from the 4,562-video corpus, stratifying by keyword cluster (5 strata), uploader verification (2 strata), and the within-stratum tercile of view count (3 strata), to ensure that all theoretically important regions of the corpus are represented in the gold-standard set. Two trained annotators code each thumbnail on all five constructs independently and blind to each other's coding. Inter-rater reliability is computed as quadratic-weighted Cohen's κ for the four ordinal constructs and as unweighted Cohen's κ for the binary topic-relevance gate, with Krippendorff's α reported as a robustness statistic. Target IRR is κ ≥ 0.85 for the gate variable and κ ≥ 0.70 for the four substantive constructs. Pairs with disagreement of ≥ 2 ordinal steps are adjudicated by the principal investigator. Annotators receive a fifteen-page codebook, a twenty-thumbnail calibration set, and a one-hour group calibration session before independent coding begins.

**Tier 2: Full-corpus computational coding.** All 4,562 thumbnails are processed through two parallel pipelines. The computer-vision pipeline follows the Automated Visual Content Analysis protocol developed for communication research [@araujo2020automated]: we use RapidOCR for text detection and geometric analysis (yielding text-area coverage and font-contrast measures that feed the `text_overlay_intensity` score) and RetinaFace + a Chinese-validated FER model for facial-emotion recognition (yielding a continuous emotion-intensity score). The vision-language pipeline issues a single structured prompt to Claude Opus 4.7 (Anthropic; `claude-opus-4-7`) with the codebook operational definitions and a small set of in-prompt exemplars, returning ordinal scores on `topic_relevance`, `threat_imagery`, `info_gap`, and the four medical-authority items. The raw VLM API responses are archived for replication. For thumbnail–title representativeness, we use Chinese-CLIP (ViT-B/16) [@yang2022chinese] to compute cosine similarity between cover-image and title embeddings, validated against a small ordinal human rating on the 500-thumbnail subsample.

**Tier 3: Convergent-validity audit.** Computational scores are validated against the human gold standard on the 500-thumbnail subsample using Spearman's ρ. We pre-specify a threshold of ρ ≥ 0.60 for a computational measure to be used in the full-sample analysis. Measures that fall short of this threshold are reported only on the 500-thumbnail gold-standard subsample. Computational measures that exceed the threshold are used at full corpus scale, with all primary models additionally fit on the 500-thumbnail gold-standard subsample as a robustness check.

This pipeline is broadly consistent with the methodological consensus in computational visual social science [@edelmann2020computational; @peng2024automated] and with the multimodal annotation strategies adopted by recent thumbnail-detection benchmarks [@naveed2025thumbnailtruth]. The departure from prior practice is the explicit, pre-registered Spearman threshold for promoting a computational measure to full-corpus use.

### 4.5 Control variables

The principal control variables are: `video_age_days`, the number of days between publication and crawl, included to absorb the cumulative-engagement bias toward older videos; `log_followers`, the log-transformed follower count of the uploader, included to absorb channel size; `duration_log`, the log-transformed duration in seconds; `pubdate_year`, modeled as a categorical fixed effect to absorb platform-mechanism evolution across the ten-year publication window; `tname`, the B-station category fixed effect; `copyright_self`, a binary indicator that the video is original (as opposed to reposted, which is rare in our sample but theoretically distinct); and the binary `is_official` verification indicator. We deliberately exclude `order_source` (the sort order under which the video was retrieved) from the control set, because it is endogenous to the video's clickbait intensity and thus post-treatment. We report a sensitivity model that includes `order_source` fixed effects in the appendix. For the 13 percent of videos with missing values on `tid`, `copyright`, or `uploader_level` (a legacy of an earlier crawl batch), we use isotonic-regression imputation of `video_age_days` from the monotonic `aid` index and code the remaining missing fields as a separate "missing" category.

### 4.6 Analytic strategy

For each of the six outcomes, we fit a sequence of five nested specifications. Model M1 includes the multimodal clickbait index and the information-gap index alone. Model M2 adds the full control set. Model M3 adds the representativeness main effect. Model M4 adds the multimodal-clickbait-by-representativeness and information-gap-by-representativeness interactions. Model M5, the exploratory specification, additionally tests the three-way interaction with `is_official`. Standard errors are cluster-robust at the uploader (`mid`) level to account for non-independence among videos posted by the same channel.

We pre-register a *dual-track* primary specification: a between-uploader cross-sectional model (M2a) on the full 4,562-video sample, and a within-uploader fixed-effects model (M2b) on the subsample of uploaders with ≥ 2 videos (n ≈ 1,400 uploaders contributing ≈ 3,500 videos). The two-track design is motivated by the simultaneous threat of unobserved confounding from the recommender system at the between-uploader level and the loss of statistical power at the within-uploader level. We report both as primary and treat their agreement (or disagreement) as substantive.

To test the comparative hypothesis H1b, we estimate the bifurcation contrast as the difference between the standardized multimodal-clickbait coefficient in the low-cost equation (views; NB) and in the high-cost equation (coins; ZINB). We construct a 95 percent confidence interval for this difference using a non-parametric bootstrap on 1,000 resamples of the video-level data, stratified by uploader. All marginal effects are reported as average marginal effects (AMEs) using the `marginaleffects` R package [@arel-bundock2024how], consistent with the journal's reporting norms.

We pre-specify multiple-comparisons control as follows: the family of confirmatory tests is H1a, H1b, H1c, H2, H3, and H4; for this family, we apply Benjamini–Hochberg false-discovery-rate control at q = 0.05, with the high-cost coin and favorites outcomes designated as primary and the remaining four as secondary. The exploratory H5 is reported without multiple-comparisons adjustment.

### 4.7 Robustness battery

We pre-register the following sensitivity checks: (R1) re-fitting with ratio outcomes (coins/views, favorites/views, shares/views) using beta regression; (R2) restricting to the post-2022 subsample, to address platform-mechanism evolution; (R3) trimming the top 5 percent of channels by follower count; (R4) restricting to the "Science & Knowledge" tname category; (R5) Poisson rather than NB; (R6) replacing the continuous multimodal-clickbait index with quartile dummies, to relax the linearity assumption; (R7) Oster's δ for unobserved-confounding bound [@oster2019unobservable]; (R8) E-values for treatment-effect robustness [@vanderweele2017sensitivity]; (R9) restriction to videos with `topic_relevance == 1` under the strict human gold-standard coding; (R10) human-coded-only on the 500-thumbnail subsample vs. VLM-coded on the full corpus, to detect measurement-source dependence; (R11) listwise deletion vs. multiple imputation (m = 20) for the 13 percent missingness; (R12) two-way clustering on (`mid`, `pubdate_month`) to address recommender-system-induced SUTVA violations; and (R13) leave-one-keyword-out across the five clickbait-stem seed keywords.

### 4.8 Causal boundary and limitations

We do not claim a causal effect of multimodal clickbait on user engagement. Bilibili's recommender system jointly determines both which thumbnails get promoted into the feed and which receive subsequent engagement; the backdoor between the thumbnail and the engagement metric cannot be closed with observational data alone. The within-uploader fixed-effects specification absorbs all time-invariant uploader characteristics, including a channel's average historical promotion by the recommender, but does not absorb video-level promotion shocks. Oster δ and E-value sensitivity analyses quantify the magnitude of unobserved confounding that would be required to nullify the estimated associations, but they are not a substitute for an exogenous source of variation. Three further limitations apply. First, our corpus is "videos that were returned by the search API for 28 health-related keywords," not "all health-related videos on Bilibili"; results generalize only to the search-indexed subset. Second, engagement metrics are a single-day snapshot; ratio outcomes (R1) partially mitigate cumulative-engagement bias but do not eliminate it. Third, we measure visual features of the cover thumbnail but not the audio-visual content of the video itself; a thumbnail-misleading video may be uniformly clickbait-y or may deliver substantive content once entered, and our design does not distinguish these.

### 4.9 Pre-registration, open science, and ethics

The pre-analysis plan, the codebook, the full set of VLM prompts, and the analysis code will be deposited on the Open Science Framework prior to the analysis of any outcome model. The corpus metadata (excluding raw thumbnail images, which are subject to platform terms of service) will be archived on Zenodo with a digital object identifier. Thumbnail images themselves will not be redistributed; image URLs and a re-collection script will be provided. The uploader identifier (`mid`) is one-way hashed in the public dataset; the uploader signature field (`uploader_sign`), which may contain identifying titles, will be redacted using a structured-label scheme. The study uses only public, non-account-restricted platform metadata, with no interaction with users or uploaders; our institution's review board has classified the protocol as exempt under Category 4 (research involving the collection or study of existing publicly available data). We disclose the use of Claude Opus 4.7 as a secondary coder in the annotation pipeline; all primary coding decisions are retained by the human annotators, and the model is used only for full-corpus scaling against the human gold standard.

---

## References

Al-Ali, M.N. and S.M. Hamzeh. 2024. "Extra Cues Extra Views: A Multimodal Detection of Arabic Clickbait Thumbnail Verbo-Visual Cues." *Discourse & Communication*.

Arel-Bundock, V., N. Greifer, and A. Heiss. 2024. "How to Interpret Statistical Models Using marginaleffects for R and Python." *Journal of Statistical Software* 111(9): 1–32. https://doi.org/10.18637/jss.v111.i09.

Araujo, T., I. Lock, and B. van de Velde. 2020. "Automated Visual Content Analysis (AVCA) in Communication Research: A Protocol for Large Scale Image Classification with Pre-Trained Computer Vision Models." *Communication Methods and Measures* 14(4): 239–265.

Bilibili Inc. 2024. *Bilibili Inc. Reports Third Quarter 2024 Financial Results*. Form 6-K filed with the U.S. Securities and Exchange Commission, November 14, 2024. Retrieved May 25, 2026 (https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001723690).

Bird, R.B. and E.A. Smith. 2005. "Signaling Theory, Strategic Interaction, and Symbolic Capital." *Current Anthropology*.

Blom, J.N. and K.R. Hansen. 2015. "Click Bait: Forward-Reference as Lure in Online News Headlines." *Journal of Pragmatics* 76: 87–100.

Bravo, I., K. Prasse, S. Walter, S. O'Neill, and M. Keuper. 2025. "Global Dynamics of Climate Change Imagery: Emotional and Engagement Effects Across Visual Frames on Twitter/X." *Science Communication*.

Cao, J., X. Li, and L. Zhang. 2025. "Is Relevancy Everything? A Deep-Learning Approach to Understand the Effect of Image-Text Congruence." *Management Science*.

Chen, J. 2025. "Understanding Danmaku and Comment Interactions Through Content Features and Video Popularity." *Procedia Computer Science*.

Donath, J. 2007. "Signals in Social Supernets." *Journal of Computer-Mediated Communication*.

Dong, W., Y. Liu, W. Wang, L. Jiang, and Y. Yi. 2025. "The Impact of Danmaku Ritual Types on User Digital Engagement in Video-Based Social Media: The Moderating Role of Influencer Types and Domains." *Psychology & Marketing*.

Edelmann, A., T. Wolff, D. Montagne, and C.A. Bail. 2020. "Computational Social Science and Sociology." *Annual Review of Sociology*.

Geise, S. and Y. Xu. 2025. "Effects of Visual Framing in Multimodal Media Environments: A Systematic Review of Studies Between 1979 and 2023." *Journalism & Mass Communication Quarterly*.

Guo, L., Y. Wang, P. Li, Y. Wang, and Y. Li. 2026. "The Impact of Headline Characteristics on Clicks: A Case Study of a Chinese Local Medium." *Journalism Practice* 20(4): 1427–1455.

Heley, K., A. Gaysynsky, and A.J. King. 2022. "Missing the Bigger Picture: The Need for More Research on Visual Health Misinformation." *Science Communication* 44(4): 514–527.

Isaac, M.S. 2025. "Thirty Years of Persuasion Knowledge Research: From Demonstrating Effects to Building Theory to Increasing Applicability." *Consumer Psychology Review*.

Jones, C.L., J.D. Jensen, C.L. Scherr, N.R. Brown, K. Christy, and J. Weaver. 2015. "The Health Belief Model as an Explanatory Framework in Communication Research: Exploring Parallel, Serial, and Moderated Mediation." *Health Communication* 30(6): 566–576.

Keib, K., C. Espina, Y.-I. Lee, B.W. Wojdynski, D. Choi, and H. Bang. 2018. "Picture This: The Influence of Emotionally Valenced Images on Attention, Selection, and Sharing of Social Media News." *Media Psychology* 21(2): 202–221.

Khawar, S. and M. Boukes. 2025. "Analyzing Sensationalism in News on Twitter (X): Clickbait Journalism by Legacy vs. Online-Native Outlets and the Consequences for User Engagement." *Digital Journalism* 13(8): 1482–1502.

King, A.J. and A.J. Lazard. 2020. "Advancing Visual Health Communication Research to Improve Infodemic Response." *Health Communication* 35(14): 1723–1728.

Klein, E.G., K. Roberts, J. Manganello, R. McAdams, and L. McKenzie. 2020. "When Social Media Images and Messages Don't Match: Attention to Text versus Imagery to Effectively Convey Safety Information on Social Media." *Journal of Health Communication* 25(11): 879–884.

Kuiken, J., A. Schuth, M. Spitters, and M. Marx. 2017. "Effective Headlines of Newspaper Articles in a Digital Environment." *Digital Journalism* 5(10): 1300–1314.

Lang, A. 2000. "The Limited Capacity Model of Mediated Message Processing." *Journal of Communication* 50(1): 46–70.

Li, Y. and Y. Xie. 2020. "Is a Picture Worth a Thousand Words? An Empirical Study of Image Content and Social Media Engagement." *Journal of Marketing Research*.

Limpijankit, M. and J.R. Kender. 2025. "Detecting Cultural Differences in News Video Thumbnails via Computational Aesthetics."

Liu, A.K.C. and O. Kuru. 2025. "Understanding the Effects of Visual Misinformation: A Systematic Review of 10 Years (2014–2024)." *Mass Communication and Society*.

Liu, S., J. Xu, Z. Zhao, and X. Li. 2023. "Factors Affecting Trust in Chinese Digital Journalism: Approach Based on Folk Theories." *Media and Communication* 11(4): 355–366.

Lu, Y. and J. Pan. 2021. "Capturing Clicks: How the Chinese Government Uses Clickbait to Compete for Visibility." *Political Communication*.

Lu, Y. and J. Pan. 2022. "The Pervasive Presence of Chinese Government Content on Douyin Trending Videos." *Computational Communication Research*.

Lu, Y. and C. Shen. 2023. "Unpacking Multimodal Fact-Checking: Features and Engagement of Fact-Checking Videos on Chinese TikTok (Douyin)." *Social Media + Society*.

Metzger, M.J., A.J. Flanagin, and R.B. Medders. 2010. "Social and Heuristic Approaches to Credibility Evaluation Online." *Journal of Communication* 60(3): 413–439.

Molyneux, L. and M. Coddington. 2020. "Aggregation, Clickbait and Their Effect on Perceptions of Journalistic Credibility and Quality." *Journalism Practice* 14(4): 429–446.

Munger, K. 2020. "All the News That's Fit to Click: The Economics of Clickbait Media." *Political Communication*.

Naveed, W., Z.A. Uzmi, and Z.A. Qazi. 2025. "ThumbnailTruth: A Multi-Modal LLM Approach for Detecting Misleading YouTube Thumbnails Across Diverse Cultural Settings."

Oster, E. 2019. "Unobservable Selection and Coefficient Stability: Theory and Evidence." *Journal of Business & Economic Statistics* 37(2): 187–204. https://doi.org/10.1080/07350015.2016.1227711.

Peng, Y., I. Lock, and A.A. Salah. 2024. "Automated Visual Analysis for the Study of Social Media Effects: Opportunities, Approaches, and Challenges." *Communication Methods and Measures*.

Powell, T.E., H.G. Boomgaarden, K. De Swert, and C.H. de Vreese. 2015. "A Clearer Picture: The Contribution of Visuals and Text to Framing Effects." *Journal of Communication*.

Scott, K. 2021. "You Won't Believe What's in This Paper! Clickbait, Relevance and the Curiosity Gap." *Journal of Pragmatics* 175: 53–66.

Shin, J., C. DeFelice, and S. Kim. 2025. "Emotion Sells: Rage Bait vs. Information Bait in Clickbait News Headlines on Social Media." *Digital Journalism*.

Spence, M. 1973. "Job Market Signaling." *Quarterly Journal of Economics*.

Valkenburg, P.M. and J. Peter. 2013. "The Differential Susceptibility to Media Effects Model." *Journal of Communication* 63(2): 221–243.

VanderWeele, T.J. and P. Ding. 2017. "Sensitivity Analysis in Observational Research: Introducing the E-Value." *Annals of Internal Medicine* 167(4): 268–274. https://doi.org/10.7326/M16-2607.

Vultee, F., G.S. Burgess, D. Frazier, and K. Mesmer. 2022. "Here's What to Know About Clickbait: Effects of Image, Headline and Editing on Audience Attitudes." *Journalism Practice*.

Wang, Y., B. Hu, C. Tang, and X. Yang. 2025. "Decoding Clickbait: The Impact of Clickbait Types and Structures on Cognitive and Emotional Responses in Online Interactions." *Cyberpsychology, Behavior & Social Networking*.

Xu, Z., M. Laffidy, and L. Ellis. 2023. "Clickbait for Climate Change: Comparing Emotions in Headlines and Full-Texts and Their Engagement." *Information, Communication & Society* 26(10): 1915–1932.

Yang, A., J. Pan, J. Lin, R. Men, Y. Zhang, J. Zhou, and C. Zhou. 2022. "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese."

Yoon, Y., S. Yoon, and K. Park. 2024. "Assessing News Thumbnail Representativeness: Counterfactual Text Can Enhance the Cross-Modal Matching Ability." *Findings of the Association for Computational Linguistics: ACL 2024*.

Zhang, X. and S. Zhou. 2019. "Clicking Health Risk Messages on Social Media: Moderated Mediation Paths Through Perceived Threat, Perceived Efficacy, and Fear Arousal." *Health Communication* 34(11): 1359–1368.

---

## Table 1: Keyword Strata and Per-Keyword Sample Sizes

<!-- Source: derived from Data process/master_bilibili_health.csv query column -->

| Cluster | Keyword | N |
|---|---|---|
| General health education | 医学科普 | 435 |
| General health education | 健康科普 | 429 |
| General health education | 医生提醒 | 390 |
| General health education | 体检报告 | 248 |
| General health education | 饮食健康 | 196 |
| General health education | 养生科普 | 180 |
| Chronic disease | 糖尿病 科普 | 180 |
| Chronic disease | 高血压 科普 | 180 |
| Chronic disease | 心脏病 科普 | 180 |
| Chronic disease | 脂肪肝 科普 | 180 |
| Chronic disease | 糖尿病 (short) | 60 |
| Chronic disease | 高血压 (short) | 20 |
| Chronic disease | 高血压 危险信号 | 6 |
| Oncology and screening | 癌症 早期信号 | 180 |
| Oncology and screening | HPV 疫苗 | 180 |
| Oncology and screening | 肺癌 科普 | 180 |
| Oncology and screening | HPV (short) | 60 |
| Lifestyle | 减肥 科学 | 180 |
| Lifestyle | 脱发 医生 | 180 |
| Lifestyle | 睡眠 健康 | 180 |
| Lifestyle | 减肥 (short) | 60 |
| Lifestyle | 脱发 (short) | 60 |
| Clickbait stem | 医生提醒 千万别 | 180 |
| Clickbait stem | 医生终于说了 | 180 |
| Clickbait stem | 体检报告 异常 | 130 |
| Clickbait stem | 这个习惯 致癌 | 92 |
| Clickbait stem | 健康科普 千万别吃 | 18 |
| Clickbait stem | 医生提醒 致癌 | 18 |
| **Total (pre-dedup)** | — | **5,062** |
| **Total (post-dedup, primary corpus)** | — | **4,562** |

**Notes**: N reflects the number of unique videos retrieved under each keyword × sort-order combination, before global deduplication on `bvid`. Post-deduplication, 4,562 unique videos remain in the analytic corpus. Keyword clusters are coded as a categorical fixed effect in all primary models. The "clickbait stem" cluster includes pre-defined search terms intended to oversample videos with high multimodal clickbait intensity; a leave-one-keyword-out robustness check is reported in Section 4.7.

---

## Table 2: Descriptive Distributions of Engagement Outcomes (N = 4,562)

<!-- Source: Data process/audit_report.md §4 -->

| Outcome | Mean | Median | 25th pct | 75th pct | 95th pct | % zeros | Planned model |
|---|---|---|---|---|---|---|---|
| Views (`play`) | 570,285 | 7,716 | 239 | 245,933 | 3,140,807 | 1.3 | Negative binomial |
| Likes (`like`) | 19,265 | 109 | 5 | 4,694 | 105,566 | 5.1 | Negative binomial |
| Favorites | 8,819 | 66 | 2 | 1,806 | 37,505 | 16.6 | Negative binomial |
| Shares | 3,171 | 18 | 0 | 622 | 12,046 | 27.0 | **ZINB** |
| Comments (`review`) | 674 | 11 | 0 | 358 | 3,486 | 30.5 | ZINB |
| Coins | 4,682 | 7 | 0 | 282 | 14,663 | 36.5 | **ZINB** |
| Danmaku | 1,170 | 1 | 0 | 124 | 4,149 | 45.8 | **ZINB** |

**Notes**: N = 4,562 unique videos. Distributions are heavily right-skewed; we report median, 25th, 75th, and 95th percentiles in addition to the mean to convey the dispersion. The "% zeros" column reports the percentage of videos with the corresponding outcome equal to zero. ZINB = zero-inflated negative binomial. The high-cost endorsement outcomes (coins, shares, danmaku) all exhibit zero-inflation rates above 25 percent, motivating the ZINB specification. The inflation equation in the ZINB specification includes `log_followers` and `video_age_days`.

---

[Figure 1 about here]

**Figure 1 (planned)**: Density plot of the multimodal clickbait index (factor score derived from emotion intensity + threat imagery + text overlay intensity) on the 500-thumbnail human gold-standard subsample, overlaid by a parallel distribution from the full-corpus VLM coding, color-coded by Spearman ρ convergent-validity tier.

[Figure 2 about here]

**Figure 2 (planned)**: Schematic of the dual-track analytic strategy. Left panel: the between-uploader cross-sectional specification on the full 4,562-video sample. Right panel: the within-uploader fixed-effects specification on the ≥ 2-video subsample (n ≈ 1,400 uploaders, ≈ 3,500 video-observations).

[Figure 3 about here]

**Figure 3 (planned)**: Hybrid annotation pipeline diagram. Tier 1: 500-thumbnail human gold standard (double-blind, two coders). Tier 2: full-corpus computational coding (RapidOCR + RetinaFace+FER; Chinese-CLIP for representativeness; Claude Opus 4.7 for VLM-scored constructs). Tier 3: convergent-validity audit (Spearman ρ ≥ 0.60 threshold for full-corpus promotion).

---

<!-- END OF PRE-RESULTS DRAFT -->
<!-- Next sections to be added after analysis: Results, Discussion, Conclusion -->
<!-- Pre-registration of analytic models to be submitted to OSF before estimation begins -->
