"""
Unit tests for data validation module.
"""

import pytest
import pandas as pd
import numpy as np
from src.validate_data import validate_raw_schema, validate_data_quality, compare_datasets
from src.config import EXPECTED_COLUMNS


@pytest.fixture
def sample_valid_df():
    return pd.DataFrame({
        "trans_date_trans_time": ["2020-01-01 10:00:00", "2020-01-01 12:00:00"],
        "merchant": ["merch_a", "merch_b"],
        "category": ["grocery_pos", "shopping_net"],
        "amt": [50.0, 320.0],
        "gender": ["M", "F"],
        "city": ["New York", "Albany"],
        "state": ["NY", "NY"],
        "lat": [40.7128, 42.6526],
        "long": [-74.0060, -73.7562],
        "city_pop": [8000000, 100000],
        "job": ["Engineer", "Teacher"],
        "dob": ["1985-05-12", "1992-09-20"],
        "trans_num": ["t1", "t2"],
        "unix_time": [1577872800, 1577880000],
        "merch_lat": [40.7306, 42.6600],
        "merch_long": [-73.9352, -73.7600],
        "is_fraud": [0, 1],
    })


def test_validate_raw_schema_valid(sample_valid_df):
    result = validate_raw_schema(sample_valid_df, "ValidSample")
    assert result["is_schema_valid"] is True
    assert len(result["missing_expected_columns"]) == 0


def test_validate_raw_schema_missing_column(sample_valid_df):
    df_missing = sample_valid_df.drop(columns=["is_fraud"])
    result = validate_raw_schema(df_missing, "MissingColSample")
    assert result["is_schema_valid"] is False
    assert "is_fraud" in result["missing_expected_columns"]


def test_validate_data_quality_clean(sample_valid_df):
    result = validate_data_quality(sample_valid_df, "CleanSample")
    assert result["is_valid"] is True
    assert result["missing_values_total"] == 0
    assert result["duplicate_rows"] == 0
    assert result["fraud_count"] == 1
    assert result["legit_count"] == 1
    assert result["fraud_rate_pct"] == 50.0


def test_validate_data_quality_invalid_labels(sample_valid_df):
    df_bad = sample_valid_df.copy()
    df_bad.loc[0, "is_fraud"] = 5  # Invalid label
    result = validate_data_quality(df_bad, "BadLabelSample")
    assert result["is_valid"] is False
    assert any("Invalid fraud labels" in issue for issue in result["issues"])


def test_validate_data_quality_negative_amount(sample_valid_df):
    df_bad = sample_valid_df.copy()
    df_bad.loc[0, "amt"] = -10.0
    result = validate_data_quality(df_bad, "NegativeAmountSample")
    assert result["is_valid"] is False
    assert result["invalid_amounts_count"] == 1


def test_validate_data_quality_out_of_bounds_coords(sample_valid_df):
    df_bad = sample_valid_df.copy()
    df_bad.loc[0, "lat"] = 999.0  # Latitude must be <= 90
    result = validate_data_quality(df_bad, "BadCoordsSample")
    assert result["is_valid"] is False
    assert any("lat" in issue for issue in result["issues"])


def test_compare_datasets(sample_valid_df):
    train = sample_valid_df.copy()
    test = sample_valid_df.copy()
    comp = compare_datasets(train, test)
    assert comp["columns_match"] is True
    assert comp["train_rows"] == 2
    assert comp["test_rows"] == 2
    assert comp["total_combined_rows"] == 4
