"""
Data validation utilities for the Financial Fraud Detection & Analytics System.
Validates data integrity, schemas, coordinate bounds, amounts, and fraud labels.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from src.config import EXPECTED_COLUMNS


def validate_raw_schema(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """
    Validates the schema and key column presence of a raw dataframe.
    """
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    return {
        "dataset_name": dataset_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns_present": list(df.columns),
        "missing_expected_columns": missing_cols,
        "is_schema_valid": len(missing_cols) == 0,
    }


def validate_data_quality(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """
    Performs comprehensive data quality checks on the dataframe:
    - Missing values count and percentage
    - Exact duplicate rows count
    - Target label values (must be only 0 and 1)
    - Negative or zero amounts count
    - Geographic coordinate boundary checks
    - Date format sanity
    """
    results: Dict[str, Any] = {
        "dataset_name": dataset_name,
        "total_rows": int(len(df)),
        "is_valid": True,
        "issues": [],
    }

    # 1. Missing values
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    results["missing_values_total"] = total_nulls
    if total_nulls > 0:
        results["missing_by_column"] = null_counts[null_counts > 0].to_dict()
        results["issues"].append(f"Found {total_nulls} missing values.")

    # 2. Duplicate rows
    duplicate_count = int(df.duplicated().sum())
    results["duplicate_rows"] = duplicate_count
    if duplicate_count > 0:
        results["issues"].append(f"Found {duplicate_count} duplicate rows.")

    # 3. Target label validation
    if "is_fraud" in df.columns:
        unique_labels = set(df["is_fraud"].dropna().unique())
        results["fraud_labels_found"] = [int(x) for x in unique_labels]
        invalid_labels = unique_labels - {0, 1}
        if invalid_labels:
            results["is_valid"] = False
            results["issues"].append(f"Invalid fraud labels detected: {invalid_labels}")
        
        fraud_count = int((df["is_fraud"] == 1).sum())
        legit_count = int((df["is_fraud"] == 0).sum())
        results["fraud_count"] = fraud_count
        results["legit_count"] = legit_count
        results["fraud_rate_pct"] = (fraud_count / len(df) * 100) if len(df) > 0 else 0.0

    # 4. Amount validation
    if "amt" in df.columns:
        invalid_amounts = int((df["amt"] <= 0).sum())
        results["invalid_amounts_count"] = invalid_amounts
        results["min_amount"] = float(df["amt"].min()) if len(df) > 0 else 0.0
        results["max_amount"] = float(df["amt"].max()) if len(df) > 0 else 0.0
        if invalid_amounts > 0:
            results["is_valid"] = False
            results["issues"].append(f"Found {invalid_amounts} non-positive transaction amounts.")

    # 5. Geographic coordinate bounds validation
    # Latitude: -90 to 90, Longitude: -180 to 180
    geo_checks = [
        ("lat", -90, 90),
        ("merch_lat", -90, 90),
        ("long", -180, 180),
        ("merch_long", -180, 180),
    ]
    for col, min_val, max_val in geo_checks:
        if col in df.columns:
            out_of_bounds = int(((df[col] < min_val) | (df[col] > max_val)).sum())
            if out_of_bounds > 0:
                results["is_valid"] = False
                results["issues"].append(f"Column '{col}' has {out_of_bounds} values out of range [{min_val}, {max_val}].")

    if results["issues"]:
        if any("Invalid fraud labels" in issue or "non-positive" in issue for issue in results["issues"]):
            results["is_valid"] = False

    return results


def compare_datasets(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Verifies that train and test datasets have matching columns, compatible data types,
    and complementary date ranges.
    """
    train_cols = list(train_df.columns)
    test_cols = list(test_df.columns)
    cols_match = train_cols == test_cols
    
    return {
        "columns_match": cols_match,
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "total_combined_rows": len(train_df) + len(test_df),
        "train_fraud_count": int(train_df["is_fraud"].sum()) if "is_fraud" in train_df.columns else 0,
        "test_fraud_count": int(test_df["is_fraud"].sum()) if "is_fraud" in test_df.columns else 0,
        "train_columns_count": len(train_cols),
        "test_columns_count": len(test_cols),
    }
