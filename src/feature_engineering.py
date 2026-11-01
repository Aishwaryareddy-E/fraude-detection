"""
Feature engineering module for the Financial Fraud Detection & Analytics System.
Computes temporal features, exact customer age, customer-to-merchant Haversine distance,
and categorized analytical groupings.
"""

import pandas as pd
import numpy as np
from src.config import EARTH_RADIUS_KM


def calculate_haversine_distance(
    lat1: pd.Series, lon1: pd.Series, lat2: pd.Series, lon2: pd.Series
) -> pd.Series:
    """
    Computes great-circle distance between customer and merchant coordinates
    using the vectorized Haversine formula in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    # Haversine formula
    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2.0) ** 2)
    )
    # Clip values to [0, 1] to avoid slight float precision anomalies before arcsin
    a = np.clip(a, 0.0, 1.0)
    c = 2.0 * np.arcsin(np.sqrt(a))
    distance_km = EARTH_RADIUS_KM * c
    return distance_km.round(2)


def calculate_exact_age(trans_dates: pd.Series, birth_dates: pd.Series) -> pd.Series:
    """
    Calculates exact customer age at the date of the transaction,
    accounting for whether the birthday has occurred in the transaction year.
    """
    trans_dt = pd.to_datetime(trans_dates)
    dob_dt = pd.to_datetime(birth_dates)

    # Difference in calendar years
    age = trans_dt.dt.year - dob_dt.dt.year

    # Check if birthday hasn't occurred yet in the transaction year
    has_not_had_birthday = (trans_dt.dt.month < dob_dt.dt.month) | (
        (trans_dt.dt.month == dob_dt.dt.month) & (trans_dt.dt.day < dob_dt.dt.day)
    )
    age = age - has_not_had_birthday.astype(int)
    return age.astype("int16")


def assign_time_of_day(hour_series: pd.Series) -> pd.Series:
    """Categorizes transaction hour into standard diurnal periods."""
    bins = [-1, 5, 11, 17, 24]
    labels = ["Night (00-06)", "Morning (06-12)", "Afternoon (12-18)", "Evening (18-24)"]
    return pd.cut(hour_series, bins=bins, labels=labels)


def assign_age_groups(age_series: pd.Series) -> pd.Series:
    """Categorizes customer age into demographical segments."""
    bins = [0, 24, 34, 49, 64, 150]
    labels = ["<25", "25-34", "35-49", "50-64", "65+"]
    return pd.cut(age_series, bins=bins, labels=labels)


def assign_distance_bins(distance_series: pd.Series) -> pd.Series:
    """Categorizes distance between customer and merchant into analysis tiers."""
    bins = [-1.0, 5.0, 20.0, 50.0, 100.0, np.inf]
    labels = ["< 5 km", "5 - 20 km", "20 - 50 km", "50 - 100 km", "> 100 km"]
    return pd.cut(distance_series, bins=bins, labels=labels)


def assign_amount_tiers(amt_series: pd.Series) -> pd.Series:
    """Categorizes transaction amounts into standard retail tiers."""
    bins = [0.0, 25.0, 50.0, 100.0, 500.0, 1000.0, np.inf]
    labels = ["$0 - $25", "$25 - $50", "$50 - $100", "$100 - $500", "$500 - $1000", "> $1000"]
    return pd.cut(amt_series, bins=bins, labels=labels)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the complete feature engineering pipeline to the cleaned dataframe.
    """
    data = df.copy()

    # Ensure datetime format
    if not np.issubdtype(data["trans_date_trans_time"].dtype, np.datetime64):
        data["trans_date_trans_time"] = pd.to_datetime(data["trans_date_trans_time"])
    if not np.issubdtype(data["dob"].dtype, np.datetime64):
        data["dob"] = pd.to_datetime(data["dob"])

    dt = data["trans_date_trans_time"]

    # 1. Temporal Features
    data["year"] = dt.dt.year.astype("int16")
    data["month"] = dt.dt.month.astype("int8")
    data["day"] = dt.dt.day.astype("int8")
    data["hour"] = dt.dt.hour.astype("int8")
    data["day_name"] = dt.dt.day_name().astype("category")
    data["year_month"] = dt.dt.to_period("M").astype(str)
    data["is_weekend"] = dt.dt.dayofweek.isin([5, 6]).astype("int8")
    data["time_of_day"] = assign_time_of_day(data["hour"]).astype("category")

    # 2. Customer Demographics
    data["age"] = calculate_exact_age(data["trans_date_trans_time"], data["dob"])
    data["age_group"] = assign_age_groups(data["age"]).astype("category")

    # 3. Customer-to-Merchant Distance
    data["distance_km"] = calculate_haversine_distance(
        data["lat"], data["long"], data["merch_lat"], data["merch_long"]
    )
    data["distance_bin"] = assign_distance_bins(data["distance_km"]).astype("category")

    # 4. Amount Tiers
    data["amount_tier"] = assign_amount_tiers(data["amt"]).astype("category")

    # 5. Clean Merchant Name (strip prefix 'fraud_' if present)
    data["clean_merchant"] = data["merchant"].astype(str).str.replace("^fraud_", "", regex=True)

    # 6. Optimize category dtypes for memory & performance
    cat_cols = ["category", "gender", "state", "city", "job", "source_dataset"]
    for col in cat_cols:
        if col in data.columns:
            data[col] = data[col].astype("category")

    return data
