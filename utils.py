import pandas as pd
from pathlib import Path



## The follwoing Path configurations are used instead of a raw string as preventative measures for ipynb kernel OS Errors
# when the CWD of the notebook does not recognize the presence of the /data directory
BASE_DIR = Path(__file__).resolve().parent

TARGET_DIR = BASE_DIR / "data"

TARGET_DIR.mkdir(parents=True, exist_ok=True)

TARGET_FILE_PATH = TARGET_DIR / "aggregated_report.csv"


import re
from pathlib import Path

import pandas as pd

## The following Column mapping utility functions were sourced from ChatGPT, assuming this particular "transformation" is not under assessment
## Use disclosed incase the instruction team disagrees

COLUMN_ALIASES = {
    # Location
    "country": "country",
    "country region": "country",
    "country or region": "country",
    "region": "region",

    # Rankings and scores
    "happiness rank": "happiness_rank",
    "overall rank": "happiness_rank",
    "rank": "happiness_rank",
    "happiness score": "happiness_score",
    "score": "happiness_score",

    # Model features
    "economy gdp per capita": "gdp_per_capita",
    "gdp per capita": "gdp_per_capita",

    "family": "social_support",
    "social support": "social_support",

    "health life expectancy": "healthy_life_expectancy",
    "healthy life expectancy": "healthy_life_expectancy",

    "freedom": "freedom",
    "freedom to make life choices": "freedom",

    "trust government corruption": "perceptions_of_corruption",
    "perceptions of corruption": "perceptions_of_corruption",

    "generosity": "generosity",
    "dystopia residual": "dystopia_residual",

    # Confidence/error measurements
    "standard error": "standard_error",
    "lower confidence interval": "lower_confidence_interval",
    "upper confidence interval": "upper_confidence_interval",
    "whisker low": "lower_confidence_interval",
    "whisker high": "upper_confidence_interval",
}


def clean_header(header):
    """
    Convert punctuation variations such as:
    'Trust..Government.Corruption.'
    into:
    'trust government corruption'
    """
    header = str(header).strip().lower()
    header = re.sub(r"[^a-z0-9]+", " ", header)
    return re.sub(r"\s+", " ", header).strip()


def normalize_columns(df):
    rename_map = {}

    for original_column in df.columns:
        cleaned = clean_header(original_column)
        rename_map[original_column] = COLUMN_ALIASES.get(
            cleaned,
            cleaned.replace(" ", "_"),
        )

    normalized = df.rename(columns=rename_map)

    duplicated = normalized.columns[
        normalized.columns.duplicated()
    ].tolist()

    if duplicated:
        raise ValueError(
            f"Duplicate columns created during normalization: {duplicated}\n"
            f"Rename mapping: {rename_map}"
        )

    return normalized

def extrapolate_survey_year(file_name):
    pattern = r"data/(.+?)\.csv"
    match = re.search(pattern, file_name)    

    return match.group(1)

def aggregate_yearly_reports(csv_files):
    """
    Receives a list of strings of csv_file paths and returns a string representing the path to the new aggregated file
    """

    all_df = []

    for file in csv_files:
        df = pd.read_csv(file)
        df = normalize_columns(df)

        df["survey_year"] = extrapolate_survey_year(file)

        all_df.append(df)

        combined_df = pd.concat(
            all_df,
            ignore_index=True,
            sort=False,
        )

        combined_df.to_csv(TARGET_FILE_PATH, index=False)

    return TARGET_FILE_PATH

# To vizualize all metrics in a single bar plot, we normal the scale so that happiness's 0-10 scale does not 
# visually dominate other metric's 0-1 scale
def min_max_normalization(data, metrics, reference_df=None):

    # TODO: Decide whether or not to keep this custom code or use SciKitLearn referenced in lecture
    result = data.copy()

    if reference_df is None:
        reference_df = data

    metric_min = reference_df[metrics].min()

    metric_range = (
        reference_df[metrics].max() - metric_min
    ).replace(0, 1)

    result[metrics] = (
        result[metrics] - metric_min
    ) / metric_range

    return result

def create_gdp_quartile_df(df):

    quartile_labels = [
        "Q1: Lowest",
        "Q2: Lower-middle",
        "Q3: Upper-middle",
        "Q4: Highest",
    ]

    # GDP percentile within each survey year
    df["gdp_percentile"] = (
        df.groupby("survey_year")["gdp_per_capita"]
        .rank(method="average", pct=True)
    )

    # TODO: Review the quartile buckets 
    df["gdp_quartile"] = pd.cut(
        df["gdp_percentile"],
        bins=[0, 0.25, 0.50, 0.75, 1.00],
        labels=quartile_labels,
        include_lowest=True,
    )

    df[
        [
            "country",
            "survey_year",
            "gdp_per_capita",
            "gdp_percentile",
            "gdp_quartile",
        ]
    ].sort_values(
        ["survey_year", "gdp_per_capita"]
    )

    return df

