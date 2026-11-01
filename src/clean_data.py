"""
Data cleaning and preprocessing pipeline for the Financial Fraud Detection & Analytics System.
Removes PII columns, converts datatypes, unites train & test datasets, applies feature engineering,
and exports optimized Parquet artifacts.
"""

import logging
import pandas as pd
from typing import Tuple
from src.config import (
    DROP_COLUMNS,
    PROCESSED_PARQUET_FILE,
    PROCESSED_SAMPLE_FILE,
)
from src.load_data import load_raw_datasets
from src.validate_data import validate_data_quality, compare_datasets
from src.feature_engineering import engineer_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_single_dataset(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Cleans a single dataset partition."""
    logger.info(f"Cleaning {source_name} dataset (Initial shape: {df.shape})...")

    # Drop PII / unnecessary columns
    cols_to_drop = [col for col in DROP_COLUMNS if col in df.columns]
    df_clean = df.drop(columns=cols_to_drop).copy()

    # Convert datetimes
    df_clean["trans_date_trans_time"] = pd.to_datetime(
        df_clean["trans_date_trans_time"], errors="coerce"
    )
    df_clean["dob"] = pd.to_datetime(df_clean["dob"], errors="coerce")

    # Ensure amount and target are strictly correct types
    df_clean["amt"] = df_clean["amt"].astype("float32")
    df_clean["is_fraud"] = df_clean["is_fraud"].astype("int8")

    # Preserve original source dataset label
    df_clean["source_dataset"] = source_name

    logger.info(f"Finished cleaning {source_name} (New shape: {df_clean.shape}).")
    return df_clean


def build_unified_dataset() -> pd.DataFrame:
    """
    Executes full extraction, cleaning, concatenation, feature engineering,
    and returns the processed dataframe.
    """
    logger.info("Loading raw train and test datasets...")
    train_raw, test_raw = load_raw_datasets()

    # Compare and validate
    comparison = compare_datasets(train_raw, test_raw)
    logger.info(f"Dataset comparison: {comparison}")

    train_clean = clean_single_dataset(train_raw, "Train")
    test_clean = clean_single_dataset(test_raw, "Test")

    logger.info("Concatenating datasets and sorting chronologically...")
    combined = pd.concat([train_clean, test_clean], ignore_index=True)
    combined = combined.sort_values("trans_date_trans_time").reset_index(drop=True)

    logger.info(f"Combined total records: {len(combined):,}, Fraud: {int(combined['is_fraud'].sum()):,}")

    logger.info("Executing feature engineering pipeline...")
    engineered = engineer_features(combined)

    logger.info(f"Feature engineering complete. Final shape: {engineered.shape}")
    return engineered


def run_pipeline(save_sample: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Runs the complete preprocessing pipeline and saves Parquet files to disk.
    """
    PROCESSED_PARQUET_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    df = build_unified_dataset()

    logger.info(f"Writing complete dataset to Parquet: {PROCESSED_PARQUET_FILE}...")
    df.to_parquet(PROCESSED_PARQUET_FILE, engine="pyarrow", compression="snappy", index=False)
    logger.info(f"Saved {PROCESSED_PARQUET_FILE.name} ({PROCESSED_PARQUET_FILE.stat().st_size / (1024*1024):.2f} MB).")

    sample_df = None
    if save_sample:
        logger.info("Creating stratified 100k sample for fast local testing...")
        # Stratified sampling by is_fraud to preserve the exact fraud ratio
        fraud_sample = df[df["is_fraud"] == 1]
        legit_sample = df[df["is_fraud"] == 0].sample(n=min(99500, len(df[df["is_fraud"] == 0])), random_state=42)
        sample_df = pd.concat([fraud_sample, legit_sample], ignore_index=True)
        sample_df = sample_df.sort_values("trans_date_trans_time").reset_index(drop=True)
        sample_df.to_parquet(PROCESSED_SAMPLE_FILE, engine="pyarrow", compression="snappy", index=False)
        logger.info(f"Saved sample: {PROCESSED_SAMPLE_FILE.name} with {len(sample_df):,} records.")

    return df, sample_df


if __name__ == "__main__":
    run_pipeline()
