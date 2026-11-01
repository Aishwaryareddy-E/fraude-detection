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
    Priority order:
      1. If sample=True and sample file exists → load 100k sample
      2. Full processed parquet (local dev)
      3. 100k sample as cloud deployment fallback
    """
    if sample and PROCESSED_SAMPLE_FILE.exists():
        return pd.read_parquet(PROCESSED_SAMPLE_FILE)
    if PROCESSED_PARQUET_FILE.exists():
        return pd.read_parquet(PROCESSED_PARQUET_FILE)
    if PROCESSED_SAMPLE_FILE.exists():
        # Cloud deployment: fall back to sample automatically
        return pd.read_parquet(PROCESSED_SAMPLE_FILE)
    raise FileNotFoundError(
        f"Processed data not found. Expected:\n"
        f"  {PROCESSED_PARQUET_FILE}\n  {PROCESSED_SAMPLE_FILE}\n"
        "Run the preprocessing pipeline first."
    )


def load_creditcard_data() -> pd.DataFrame:
    """
    Load the European Credit Card dataset.
    Priority order:
      1. Full processed Parquet (local dev, 72MB)
      2. 50k stratified sample Parquet (Streamlit Cloud deployment, 14MB)
      3. Raw CSV (local dev fallback, regenerates Parquet cache)
    """
    from src.config import PROCESSED_CREDITCARD_FILE, RAW_CREDITCARD_FILE, PROCESSED_DATA_DIR
    # Full processed file (local dev)
    if PROCESSED_CREDITCARD_FILE.exists():
        return pd.read_parquet(PROCESSED_CREDITCARD_FILE)
    # Stratified 50k sample (Streamlit Cloud deployment)
    sample_file = PROCESSED_DATA_DIR / "creditcard_sample_50k.parquet"
    if sample_file.exists():
        return pd.read_parquet(sample_file)
    # Raw CSV fallback (local dev)
    elif RAW_CREDITCARD_FILE.exists():
        df = pd.read_csv(RAW_CREDITCARD_FILE)
        df.to_parquet(PROCESSED_CREDITCARD_FILE, engine="pyarrow", compression="snappy", index=False)
        return df
    else:
        raise FileNotFoundError(
            "creditcard dataset not found. Expected one of:\n"
            f"  {PROCESSED_CREDITCARD_FILE}\n"
            f"  {sample_file}\n"
            f"  {RAW_CREDITCARD_FILE}"
        )
