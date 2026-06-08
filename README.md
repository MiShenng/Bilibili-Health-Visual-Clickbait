# Overview

This repository contains code and materials for a research project on visual clickbait and stratified user engagement in health-related videos on China’s Bilibili.

This project examines how visual design strategies in video thumbnails shape user engagement with online health information. Using Bilibili as a representative long-form video platform, the study constructs a dataset of health-related videos and analyzes how visual clickbait cues are associated with different types of platform-native user behavior.

Unlike studies that treat engagement as a single metric, this project distinguishes between low-cost and high-cost forms of engagement. Views and likes are treated as relatively low-cost attention signals, while coin donation and favorites are treated as higher-cost endorsement behaviors. This distinction allows the project to examine whether visual clickbait can attract attention without necessarily earning stronger forms of user approval.

## Research Focus

The project focuses on three main questions:

1. Are visual clickbait cues in health-related video thumbnails positively associated with shallow attention but less strongly associated with high-cost engagement?
2. Which dimensions of visual clickbait best distinguish between low-cost and high-cost user engagement?
3. Does the semantic congruence between a video thumbnail and its title moderate the relationship between visual clickbait and user engagement?

## Data

The project uses data collected from Bilibili’s public search results.

The dataset includes:

- Video metadata for health-related videos retrieved through 28 Chinese health-related keywords.
- Cover thumbnails associated with each video.
- Platform-native engagement metrics, including views, likes, coins, favorites, and other interaction indicators.
- Processed visual and textual features used for computational analysis.

After deduplication and topical relevance screening, the final sample contains 22,323 valid video entries.

Due to platform policies, copyright restrictions, and ethical considerations, raw platform data, original thumbnail images, and row-level metadata containing identifiable platform information are not publicly released in this repository. The repository includes processed feature tables, aggregate result tables, analysis scripts, and figures for academic documentation and methodological transparency.

## Method

The project combines computational visual analysis, multimodal content analysis, and regression modeling.

First, a dataset of health-related videos was constructed from Bilibili’s public search results. The project collected video metadata, cover thumbnails, and engagement indicators using a keyword-based retrieval strategy.

Second, visual clickbait was conceptualized as a set of image design strategies aimed at attracting user clicks before the full video content is viewed. Building on prior clickbait research and visual communication studies, the project measures visual clickbait through several dimensions, including emotional valence, health threat symbols, visual pressure, and information gaps.

Third, the project uses a human–machine hybrid annotation workflow. An existing clickbait codebook is adapted for the visual context, and large language models are used to assist with preliminary classification. Manual annotation and semi-supervised machine learning are then combined to produce more fine-grained measures of thumbnail-level visual features.

Fourth, the project measures image–text semantic congruence between thumbnails and titles using Chinese-CLIP image–text similarity. This measure is used to examine whether thumbnail-title congruence moderates the relationship between visual clickbait and user engagement.

Finally, the project conducts regression analysis after standardizing key variables. The analysis compares the effects of visual clickbait across low-cost and high-cost engagement outcomes, allowing the study to distinguish between “buying attention” and “earning endorsement.”

## Repository Structure

、、、

├── README.md
├── data/
│   ├── raw/
│   ├── processed/
│   └── annotations/
├── scripts/
│   ├── crawler/
│   ├── preprocessing/
│   ├── visual_analysis/
│   ├── text_image_similarity/
│   └── regression_analysis/
├── results/
│   ├── tables/
│   └── figures/
└── docs/
    └── manuscript/
        ├── main.tex
        ├── body.tex
        ├── references.bib
        ├── charts/
        └── media/
、、、

## Notes

The project is currently a research-in-progress manuscript. The repository structure may be updated as data cleaning, annotation validation, and regression analysis continue.
