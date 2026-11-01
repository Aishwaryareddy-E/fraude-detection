"""
Data loading utilities for the Financial Fraud Detection & Analytics System.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
from src.config import (
    RAW_TRAIN_FILE,
    RAW_TEST_FILE,
    PROCESSED_PARQUET_FILE,
    PROCESSED_SAMPLE_FILE,
)


def load_raw_train_data(nrows: Optional[int] = None) -> pd.DataFrame:
    """Load the raw training dataset."""
    if not RAW_TRAIN_FILE.exists():
        raise FileNotFoundError(f"Raw training file not found at: {RAW_TRAIN_FILE}")
    return pd.read_csv(RAW_TRAIN_FILE, nrows=nrows)


def load_raw_test_data(nrows: Optional[int] = None) -> pd.DataFrame:
    """Load the raw test dataset."""
    if not RAW_TEST_FILE.exists():
        raise FileNotFoundError(f"Raw test file not found at: {RAW_TEST_FILE}")
    return pd.read_csv(RAW_TEST_FILE, nrows=nrows)


def load_raw_datasets(
    train_nrows: Optional[int] = None, test_nrows: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load both raw datasets."""
    train_df = load_raw_train_data(nrows=train_nrows)
    test_df = load_raw_test_data(nrows=test_nrows)
    return train_df, test_df


def load_processed_data(sample: bool = False) -> pd.DataFrame:
    """
    Load the cleaned and feature-engineered Parquet dataset.
    If sample is True, loads the 100k sample for fast local rendering if present.
    """
    target_file = PROCESSED_SAMPLE_FILE if sample and PROCESSED_SAMPLE_FILE.exists() else PROCESSED_PARQUET_FILE
    if not target_file.exists():
        raise FileNotFoundError(
            f"Processed data file not found at: {target_file}. Run the preprocessing pipeline first."
        )
    return pd.read_parquet(target_file)
