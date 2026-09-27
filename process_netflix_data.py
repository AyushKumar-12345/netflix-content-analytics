#!/usr/bin/env python3
"""
Netflix Content Analytics - Data ETL & Dimensional Modeling Pipeline
=====================================================================
Processes raw Netflix titles dataset into a star-schema ready model:
  - Fact Table: Titles.csv
  - Dimension / Bridge Table: Genre.csv
  - Dimension / Bridge Table: Country.csv
"""

import sys
import time
import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np

# Configure clean logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NetflixETL")


def load_dataset(file_path: Path) -> pd.DataFrame:
    """Load the raw Netflix CSV file safely."""
    if not file_path.exists():
        logger.error("Dataset not found at path: %s", file_path.resolve())
        sys.exit(1)
        
    logger.info("Reading raw dataset: %s", file_path.name)
    df = pd.read_csv(file_path, encoding="utf-8")
    logger.info("Raw dataset ingested successfully. Initial records: %d | Columns: %d", df.shape[0], df.shape[1])
    return df


def clean_text_and_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize text fields and handle known catalog anomalies."""
    df = df.copy()

    # 1. Deduplicate by unique title identifier
    initial_count = len(df)
    df.drop_duplicates(subset=["show_id"], keep="first", inplace=True)
    deduped_count = initial_count - len(df)
    if deduped_count > 0:
        logger.warning("Removed %d duplicate records based on 'show_id'.", deduped_count)

    # 2. Sanitize line-break characters across all text fields (protects CSV parsers & Power BI engine)
    text_cols = df.select_dtypes(include=["object"]).columns
    logger.info("Normalizing whitespace and sanitizing line breaks across %d text columns...", len(text_cols))
    for col in text_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[\r\n\t]+", " ", regex=True)
            .str.strip()
            .replace({"nan": np.nan, "None": np.nan, "": np.nan})
        )

    # 3. Resolve known schema drift: misplaced duration in rating column (e.g., Louis C.K. stand-ups)
    shift_mask = df["duration"].isna() & df["rating"].str.contains(r"\d+\s*(?:min|Season)", na=False)
    shifted_records = shift_mask.sum()
    if shifted_records > 0:
        logger.info("Resolving rating/duration shift anomaly for %d records...", shifted_records)
        df.loc[shift_mask, "duration"] = df.loc[shift_mask, "rating"]
        df.loc[shift_mask, "rating"] = "Not Rated"

    # 4. Standardize default categorical fallbacks
    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df["cast"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Not Rated")

    return df


def transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """Perform datetime conversions, metric extraction, and feature engineering."""
    df = df.copy()

    # 1. Robust Date Parsing
    logger.info("Standardizing temporal attributes...")
    df["date_added_clean"] = df["date_added"].str.strip()
    df["date_added_parsed"] = pd.to_datetime(
        df["date_added_clean"],
        format="%B %d, %Y",
        errors="coerce"
    )
    
    # Secondary parsing fallback for variant formats
    unparsed_mask = df["date_added_clean"].notna() & df["date_added_parsed"].isna()
    if unparsed_mask.any():
        df.loc[unparsed_mask, "date_added_parsed"] = pd.to_datetime(
            df.loc[unparsed_mask, "date_added_clean"], 
            errors="coerce"
        )

    df["year_added"] = df["date_added_parsed"].dt.year.astype("Int64")
    df["month_added"] = df["date_added_parsed"].dt.month_name()

    # 2. Extract Numeric Duration and Metric Unit
    logger.info("Extracting numeric duration metrics...")
    duration_split = df["duration"].str.extract(r"(?P<val>\d+)\s*(?P<unit>min|Season|Seasons)")
    df["duration_value"] = pd.to_numeric(duration_split["val"], errors="coerce").fillna(0).astype(int)
    df["duration_unit"] = duration_split["unit"].fillna("Unknown")

    return df


def build_dimensional_models(df: pd.DataFrame, output_dir: Path) -> Tuple[Path, Path, Path]:
    """Generate normalized Fact and Bridge/Dimension tables optimized for Power BI."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fact Table: Titles.csv
    fact_cols = [
        "show_id", "type", "title", "director", "cast", "country",
        "date_added_parsed", "year_added", "month_added", "release_year",
        "rating", "duration", "duration_value", "duration_unit", "description"
    ]
    fact_df = df[fact_cols].rename(columns={"date_added_parsed": "date_added"})
    titles_path = output_dir / "Titles.csv"
    fact_df.to_csv(titles_path, index=False, encoding="utf-8")
    logger.info("Fact Table exported: '%s' (%d rows, %d cols)", titles_path.name, fact_df.shape[0], fact_df.shape[1])

    # 2. Bridge Table: Genre.csv
    genre_df = df[["show_id", "listed_in"]].dropna().copy()
    genre_df["genre"] = genre_df["listed_in"].str.split(r"\s*,\s*")
    genre_df = genre_df.explode("genre")
    genre_df["genre"] = genre_df["genre"].str.strip()
    genre_df = genre_df[genre_df["genre"] != ""][["show_id", "genre"]].drop_duplicates()
    genre_path = output_dir / "Genre.csv"
    genre_df.to_csv(genre_path, index=False, encoding="utf-8")
    logger.info("Bridge Table exported: '%s' (%d records)", genre_path.name, len(genre_df))

    # 3. Bridge Table: Country.csv
    country_df = df[["show_id", "country"]].dropna().copy()
    country_df["country"] = country_df["country"].str.split(r"\s*,\s*")
    country_df = country_df.explode("country")
    country_df["country"] = country_df["country"].str.strip()
    # Filter out empty or placeholder records from bridge table for accurate geographic mapping
    country_df = country_df[(country_df["country"] != "") & (country_df["country"] != "Unknown")]
    country_df = country_df[["show_id", "country"]].drop_duplicates()
    country_path = output_dir / "Country.csv"
    country_df.to_csv(country_path, index=False, encoding="utf-8")
    logger.info("Bridge Table exported: '%s' (%d records)", country_path.name, len(country_df))

    return titles_path, genre_path, country_path


def main():
    start_time = time.time()
    base_dir = Path(__file__).resolve().parent
    raw_data_path = base_dir / "netflix_titles.csv"

    # Fallback to local working directory if running in varied IDE environments
    if not raw_data_path.exists():
        raw_data_path = Path("netflix_titles.csv")

    logger.info("=" * 60)
    logger.info("STARTING NETFLIX ANALYTICS DATA PIPELINE")
    logger.info("=" * 60)

    # Execution flow
    df_raw = load_dataset(raw_data_path)
    df_cleaned = clean_text_and_anomalies(df_raw)
    df_transformed = transform_features(df_cleaned)
    build_dimensional_models(df_transformed, base_dir)

    elapsed_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY IN %.2f SECONDS", elapsed_time)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
