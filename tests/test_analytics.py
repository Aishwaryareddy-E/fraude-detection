"""
Unit tests for analytics and feature engineering routines.
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics import (
    calculate_kpis,
    get_category_metrics,
    get_hourly_trends,
    evaluate_investigation_rules,
)
from src.feature_engineering import calculate_haversine_distance, calculate_exact_age


@pytest.fixture
def synthetic_analytics_df():
    # 4 transactions: 3 legit ($10, $20, $30) and 1 fraud ($140)
    # Total volume: 4
    # Fraud volume: 1 -> Fraud rate: 25.0%
    # Total amount: $200.00
    # Fraud amount: $140.00 -> Fraud amount share: 70.0%
    # Legit amount: $60.00
    # Avg legit amount: $20.00
    # Avg fraud amount: $140.00 -> Ratio: 7.0x
    return pd.DataFrame({
        "amt": [10.0, 20.0, 30.0, 140.0],
        "is_fraud": [0, 0, 0, 1],
        "category": ["grocery_pos", "grocery_pos", "shopping_net", "shopping_net"],
        "hour": [10, 14, 18, 23],
        "distance_km": [2.5, 12.0, 45.0, 150.0],
    })


def test_calculate_kpis(synthetic_analytics_df):
    kpis = calculate_kpis(synthetic_analytics_df)
    assert kpis["total_transactions"] == 4
    assert kpis["fraud_transactions"] == 1
    assert kpis["legitimate_transactions"] == 3
    assert kpis["fraud_rate"] == 25.0
    assert kpis["total_amount"] == 200.0
    assert kpis["fraud_amount"] == 140.0
    assert kpis["legitimate_amount"] == 60.0
    assert kpis["avg_amount"] == 50.0
    assert kpis["avg_legit_amount"] == 20.0
    assert kpis["avg_fraud_amount"] == 140.0
    assert kpis["fraud_amount_share"] == 70.0
    assert kpis["amount_fraud_ratio"] == 7.0


def test_kpis_empty_df():
    empty_df = pd.DataFrame(columns=["amt", "is_fraud"])
    kpis = calculate_kpis(empty_df)
    assert kpis["total_transactions"] == 0
    assert kpis["fraud_transactions"] == 0
    assert kpis["fraud_rate"] == 0.0


def test_calculate_haversine_distance():
    # Test identical coordinates -> distance must be 0
    lat1 = pd.Series([40.7128])
    lon1 = pd.Series([-74.0060])
    lat2 = pd.Series([40.7128])
    lon2 = pd.Series([-74.0060])
    dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    assert dist.iloc[0] == 0.0

    # Known approximate distance: NYC (40.7128, -74.0060) to Philadelphia (39.9526, -75.1652) ~ 129-131 km
    lat_philly = pd.Series([39.9526])
    lon_philly = pd.Series([-75.1652])
    dist_philly = calculate_haversine_distance(lat1, lon1, lat_philly, lon_philly)
    assert 120 < dist_philly.iloc[0] < 140


def test_calculate_exact_age():
    # Person born 1990-05-15
    # Transaction on 2020-05-14 (1 day before birthday) -> age should be 29
    # Transaction on 2020-05-16 (1 day after birthday) -> age should be 30
    dob = pd.Series(["1990-05-15", "1990-05-15"])
    trans_date = pd.Series(["2020-05-14 10:00:00", "2020-05-16 10:00:00"])
    ages = calculate_exact_age(trans_date, dob)
    assert ages.iloc[0] == 29
    assert ages.iloc[1] == 30


def test_get_category_metrics(synthetic_analytics_df):
    cat_df = get_category_metrics(synthetic_analytics_df)
    assert len(cat_df) == 2
    shopping = cat_df[cat_df["category"] == "shopping_net"].iloc[0]
    assert shopping["total_transactions"] == 2
    assert shopping["fraud_transactions"] == 1
    assert shopping["fraud_rate"] == 50.0


def test_evaluate_investigation_rules(synthetic_analytics_df):
    flagged = evaluate_investigation_rules(
        synthetic_analytics_df,
        amount_threshold=100.0,
        distance_threshold=100.0,
        night_start=22,
        night_end=4,
        high_risk_categories=["shopping_net"],
    )
    # The 4th transaction: amt=140 (flag), dist=150 (flag), hour=23 (flag), category=shopping_net (flag)
    # Triggers all 4 rules!
    t4 = flagged.iloc[3]
    assert bool(t4["flag_high_amount"]) is True
    assert bool(t4["flag_high_distance"]) is True
    assert bool(t4["flag_unusual_hour"]) is True
    assert bool(t4["flag_high_risk_category"]) is True
    assert int(t4["risk_score"]) == 4
    assert str(t4["risk_level"]) == "Critical"


def test_get_hour_weekday_matrix():
    from src.analytics import get_hour_weekday_matrix
    df = pd.DataFrame({
        "day_name": ["Monday", "Monday", "Tuesday"],
        "hour": [10, 10, 14],
        "is_fraud": [0, 1, 1],
    })
    matrix = get_hour_weekday_matrix(df, metric="fraud_count")
    assert matrix.loc["Monday", 10] == 1
    assert matrix.loc["Tuesday", 14] == 1


def test_get_creditcard_metrics():
    from src.analytics import get_creditcard_metrics
    df = pd.DataFrame({
        "Time": [0, 10, 20],
        "Amount": [100.0, 50.0, 200.0],
        "V1": [0.1, -0.2, 0.5],
        "V2": [-0.1, 0.3, -0.4],
        "Class": [0, 0, 1],
    })
    metrics = get_creditcard_metrics(df)
    assert metrics["total_transactions"] == 3
    assert metrics["fraud_transactions"] == 1
    assert metrics["mean_fraud_amount"] == 200.0
    assert metrics["mean_legit_amount"] == 75.0


def test_get_radar_profiles():
    from src.analytics import get_radar_profiles
    df = pd.DataFrame({
        "amt": [50.0, 500.0],
        "is_fraud": [0, 1],
        "hour": [14, 22],
        "distance_km": [10.0, 120.0],
        "category": ["grocery_pos", "shopping_net"],
        "is_weekend": [0, 1],
    })
    categories, legit_radar, fraud_radar = get_radar_profiles(df)
    assert len(categories) == 5
    assert len(legit_radar) == 5
    assert len(fraud_radar) == 5
    assert fraud_radar[0] == 100.0  # Normalized max amount


def test_simulate_threshold_interception():
    from src.analytics import simulate_threshold_interception
    df = pd.DataFrame({
        "amt": [50.0, 400.0, 20.0],
        "is_fraud": [0, 1, 0],
        "distance_km": [5.0, 100.0, 2.0],
        "hour": [12, 23, 15],
    })
    res = simulate_threshold_interception(df, amount_cutoff=300.0, distance_cutoff=80.0, night_window_active=True)
    assert res["fraud_caught"] == 1
    assert res["recall_cases_pct"] == 100.0
    assert res["fraud_dollars_caught"] == 400.0


def test_calculate_single_transaction_risk():
    from src.analytics import calculate_single_transaction_risk
    # High risk case: amt=550 (+40), hour=22 (+30), category=shopping_net (+20), distance=120 (+10) -> score=100
    res = calculate_single_transaction_risk(amt=550.0, category="shopping_net", hour=22, distance_km=120.0)
    assert res["score"] == 100.0
    assert res["risk_level"] == "CRITICAL RISK"
    assert "Intercept" in res["recommendation"]
