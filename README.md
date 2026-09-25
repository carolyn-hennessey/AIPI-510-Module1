# UN Global Happiness Survey Analysis

## Overview

This analysis examines relationships among national economic prosperity (GDP), happiness (composite score), social support, healthy life expectancy, freedom, generosity, and perceptions of corruption.

The analysis combines World Happiness Report data from 2015 through 2019. It evaluates differences across annual GDP-per-capita quartiles and identifies countries whose happiness scores consistently exceed those of countries in comparable GDP groups.


## Research Questions

1. How do social support and healthy life expectancy differ across GDP-per-capita quartiles?
2. Which countries consistently report greater happiness than countries in the same GDP quartile?
3. Which reported metrics drive the happiness overperformers?


## Dataset

The project uses five annual CSV files covering the World Happiness Reports from 2015 through 2019 as present in the source Kaggle dataset.

Each country-year observation *may* contain:

- Country
- Region
- Happiness rank and score
- GDP-per-capita contribution
- Social-support contribution
- Healthy-life-expectancy contribution
- Freedom contribution
- Generosity contribution
- Perceptions-of-corruption contribution
- Confidence or standard-error measures, where available
- Dystopia residual, where available

Column names and availability differ between annual files. Preprocessing maps these variations to a consistent schema.

### Source

The CSV files were downloaded from:

Kaggle dataset:
https://www.kaggle.com/datasets/unsdsn/world-happiness

Original reports, appendices, and official citations are available at:

https://www.worldhappiness.report/data-sharing/


### Important Measurement Note

The happiness score is based on survey respondents' evaluations of
their lives. Several other columns in these CSV files represent modeled
contributions used by the World Happiness Report to explain differences
in life evaluations.

## Repository Structure

- `data`: original yearly CSV files and a generated aggregated file with normalized header names from the original files
- `utils.py`: helper functions used in pre-processing, feature engineering and normalization
- `world-happiness-analysis.ipynb`: final exploratory presentation

## Final `happiness_top10_outliers.csv` Data Feature Transformations and Documentation

### Header Standardization
Across years of the survey, subtle variation in column headers was detected. This was the first sign that some data collection inconsistency may be observed throughout the rest of the analysis. A simple regex + string mapping transformation was applied to be able to aggregate all values into a single dataframe. The initial goal was to be able to explore the dataset as a timeseries to detect changes year to year.

| Original header examples                                     | Standardized column         |
| ------------------------------------------------------------ | --------------------------- |
| `Country`, `Country or region`                               | `country`                   |
| `Region`                                                     | `region`                    |
| `Happiness Rank`, `Overall rank`                             | `happiness_rank`            |
| `Happiness Score`, `Score`                                   | `happiness_score`           |
| `Economy (GDP per Capita)`, `GDP per capita`                 | `gdp_per_capita`            |
| `Family`, `Social support`                                   | `social_support`            |
| `Health (Life Expectancy)`, `Healthy life expectancy`        | `healthy_life_expectancy`   |
| `Freedom`, `Freedom to make life choices`                    | `freedom`                   |
| `Trust (Government Corruption)`, `Perceptions of corruption` | `perceptions_of_corruption` |
| `Generosity`                                                 | `generosity`                |
| `Dystopia Residual`                                          | `dystopia_residual`         |
| `Standard Error`                                             | `standard_error`            |
| `Lower Confidence Interval`, `Whisker.low`                   | `lower_confidence_interval` |
| `Upper Confidence Interval`, `Whisker.high`                  | `upper_confidence_interval` |

### Lagged Feature Creation
With the initial interest of a time-based analysis, lag features were generated for each of the subjective survey fields that were used to calculate the composite happiness score.

Subjective survey fields (metric) are the following:
```python
[
    "happiness_score",
    "gdp_per_capita",
    "social_support",
    "healthy_life_expectancy",
    "freedom",
    "perceptions_of_corruption",
    "generosity",
]
```

And the pattern of generate fields is applied as follows:

| Column or pattern         | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| `previous_survey_year`    | Previous available report year for the same country    |
| `{metric}_lag1`           | Value of the metric in the preceding consecutive year  |
| `{metric}_yoy_change`     | Current value minus preceding-year value               |
| `{metric}_yoy_pct_change` | Percentage change relative to the preceding-year value |

*** For 2015 a `NaN` value represents a missing comparison due to no prior data being available in the context of this dataset. 

### GDP Quartiles and Feature Engineering for Happiness Outlier Analysis

| Column           | Description                                            | Transformation                                           |
| ---------------- | ------------------------------------------------------ | -------------------------------------------------------- |
| `gdp_percentile` | Country’s relative GDP position within its survey year | Percentile rank of `gdp_per_capita`, ranging from 0 to 1 |
| `gdp_quartile`   | Within-year GDP group                                  | GDP percentile divided into four ordered buckets         |

Once the quartile buckets were established, peer comparisons were calculated across all Subjective survey fields representing the quartile's annual median value and the target country's difference relative to this median. For example:

```
social_support_peer_median
social_support_peer_gap
healthy_life_expectancy_peer_median
healthy_life_expectancy_peer_gap
```

## Reproducing the Analysis

### 1. Clone the repository

```bash
git clone https://github.com/carolyn-hennessey/AIPI-510-Module1
cd AIPI-510-Module1
```

### 2. Create Virtual Environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Repeat analysis

With all source datafiles hardcoded in the `utils.py` file, you sould be able to activate the Python kernel associated with your newly configured Python environment and run each code block.

## AI Use Disclaimer
A ChatGPT session associated with a Duke EDU account and driven by GPT-5.6 Sol on Medium effort was consulted to review logic, locate and triage bugs in individual code blocks incrementally.