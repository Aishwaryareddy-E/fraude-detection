"""
Analytics and KPI module for the Financial Fraud Detection & Analytics System.
Provides calculation routines for executive KPIs, temporal trends, categorical breakdowns,
geographic distributions, and transparent investigation indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes all core executive transaction and fraud KPIs.
    """
    total_trans = int(len(df))
    if total_trans == 0:
        return {
            "total_transactions": 0,
            "fraud_transactions": 0,
            "legitimate_transactions": 0,
            "fraud_rate": 0.0,
            "total_amount": 0.0,
            "fraud_amount": 0.0,
            "legitimate_amount": 0.0,
            "avg_amount": 0.0,
            "avg_fraud_amount": 0.0,
            "avg_legit_amount": 0.0,
            "fraud_amount_share": 0.0,
            "amount_fraud_ratio": 0.0,
        }

    fraud_mask = df["is_fraud"] == 1
    fraud_trans = int(fraud_mask.sum())
    legit_trans = total_trans - fraud_trans
    fraud_rate = (fraud_trans / total_trans) * 100.0

    total_amt = float(df["amt"].sum())
    fraud_amt = float(df.loc[fraud_mask, "amt"].sum()) if fraud_trans > 0 else 0.0
    legit_amt = total_amt - fraud_amt

    avg_amt = total_amt / total_trans
    avg_fraud_amt = (fraud_amt / fraud_trans) if fraud_trans > 0 else 0.0
    avg_legit_amt = (legit_amt / legit_trans) if legit_trans > 0 else 0.0
    fraud_amt_share = (fraud_amt / total_amt * 100.0) if total_amt > 0 else 0.0
    amount_fraud_ratio = (avg_fraud_amt / avg_legit_amt) if avg_legit_amt > 0 else 0.0

    return {
        "total_transactions": total_trans,
        "fraud_transactions": fraud_trans,
        "legitimate_transactions": legit_trans,
        "fraud_rate": round(fraud_rate, 4),
        "total_amount": round(total_amt, 2),
        "fraud_amount": round(fraud_amt, 2),
        "legitimate_amount": round(legit_amt, 2),
        "avg_amount": round(avg_amt, 2),
        "avg_fraud_amount": round(avg_fraud_amt, 2),
        "avg_legit_amount": round(avg_legit_amt, 2),
        "fraud_amount_share": round(fraud_amt_share, 4),
        "amount_fraud_ratio": round(amount_fraud_ratio, 2),
    }


def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly volume, fraud volume, fraud rate, and amount aggregates.
    """
    monthly = (
        df.groupby("year_month")
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
            fraud_amount=("amt", lambda s: float(s[df.loc[s.index, "is_fraud"] == 1].sum())),
        )
        .reset_index()
    )
    monthly["fraud_rate"] = (monthly["fraud_transactions"] / monthly["total_transactions"]) * 100.0
    monthly["fraud_amt_share"] = (monthly["fraud_amount"] / monthly["total_amount"]) * 100.0
    return monthly.sort_values("year_month").reset_index(drop=True)


def get_hourly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes hourly diurnal patterns (0-23 hours).
    """
    hourly = (
        df.groupby("hour")
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
        )
        .reset_index()
    )
    hourly["fraud_rate"] = (hourly["fraud_transactions"] / hourly["total_transactions"]) * 100.0
    return hourly.sort_values("hour").reset_index(drop=True)


def get_weekday_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes weekly fraud patterns ordered Monday through Sunday.
    """
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = (
        df.groupby("day_name", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
        )
        .reindex(order)
        .reset_index()
    )
    weekday["fraud_rate"] = (weekday["fraud_transactions"] / weekday["total_transactions"]) * 100.0
    return weekday


def get_category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes category-wise volume, fraud counts, fraud rates, and amounts.
    """
    cat = (
        df.groupby("category", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
            fraud_amount=("amt", lambda s: float(s[df.loc[s.index, "is_fraud"] == 1].sum())),
            avg_amount=("amt", "mean"),
        )
        .reset_index()
    )
    cat["fraud_rate"] = (cat["fraud_transactions"] / cat["total_transactions"]) * 100.0
    cat["fraud_amount_share"] = (cat["fraud_amount"] / cat["total_amount"]) * 100.0
    return cat.sort_values("fraud_rate", ascending=False).reset_index(drop=True)


def get_merchant_metrics(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Computes merchant-level statistics for top merchants by fraud volume.
    """
    merchant_col = "clean_merchant" if "clean_merchant" in df.columns else "merchant"
    merchants = (
        df.groupby(merchant_col, observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
            avg_amount=("amt", "mean"),
        )
        .reset_index()
    )
    merchants["fraud_rate"] = (merchants["fraud_transactions"] / merchants["total_transactions"]) * 100.0
    return merchants.sort_values("fraud_transactions", ascending=False).head(top_n).reset_index(drop=True)


def get_state_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes state-level geographic volume, fraud volume, fraud rates, and amounts.
    """
    state_df = (
        df.groupby("state", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
        )
        .reset_index()
    )
    state_df["fraud_rate"] = (state_df["fraud_transactions"] / state_df["total_transactions"]) * 100.0
    return state_df.sort_values("total_transactions", ascending=False).reset_index(drop=True)


def get_distance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes distribution and fraud rates across customer-merchant distance tiers.
    """
    if "distance_bin" not in df.columns:
        return pd.DataFrame()
    dist = (
        df.groupby("distance_bin", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            avg_amount=("amt", "mean"),
        )
        .reset_index()
    )
    dist["fraud_rate"] = (dist["fraud_transactions"] / dist["total_transactions"]) * 100.0
    return dist


def get_age_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes distribution and fraud rates across customer age brackets.
    """
    if "age_group" not in df.columns:
        return pd.DataFrame()
    age_df = (
        df.groupby("age_group", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            avg_amount=("amt", "mean"),
        )
        .reset_index()
    )
    age_df["fraud_rate"] = (age_df["fraud_transactions"] / age_df["total_transactions"]) * 100.0
    return age_df


def get_amount_tier_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes volume and fraud rate across transaction value tiers.
    """
    if "amount_tier" not in df.columns:
        return pd.DataFrame()
    tier_df = (
        df.groupby("amount_tier", observed=False)
        .agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            total_amount=("amt", "sum"),
        )
        .reset_index()
    )
    tier_df["fraud_rate"] = (tier_df["fraud_transactions"] / tier_df["total_transactions"]) * 100.0
    return tier_df


def evaluate_investigation_rules(
    df: pd.DataFrame,
    amount_threshold: float = 300.0,
    distance_threshold: float = 80.0,
    night_start: int = 22,
    night_end: int = 4,
    high_risk_categories: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Transparent, heuristic business-rule indicator scanner.
    Flags transactions meeting specific criteria for analyst triage.
    NOTE: These are exploratory investigation flags, not confirmed fraud predictions.
    """
    if high_risk_categories is None:
        high_risk_categories = ["shopping_net", "grocery_pos", "misc_net"]

    data = df.copy()

    # Rule 1: High Transaction Value
    data["flag_high_amount"] = data["amt"] >= amount_threshold

    # Rule 2: Unusually large customer-merchant distance
    if "distance_km" in data.columns:
        data["flag_high_distance"] = data["distance_km"] >= distance_threshold
    else:
        data["flag_high_distance"] = False

    # Rule 3: Late night transaction window
    if "hour" in data.columns:
        data["flag_unusual_hour"] = (data["hour"] >= night_start) | (data["hour"] <= night_end)
    else:
        data["flag_unusual_hour"] = False

    # Rule 4: High risk category
    data["flag_high_risk_category"] = data["category"].astype(str).isin(high_risk_categories)

    # Composite risk score (number of rules triggered: 0 to 4)
    data["risk_score"] = (
        data["flag_high_amount"].astype(int)
        + data["flag_high_distance"].astype(int)
        + data["flag_unusual_hour"].astype(int)
        + data["flag_high_risk_category"].astype(int)
    )

    data["risk_level"] = pd.cut(
        data["risk_score"],
        bins=[-1, 0, 1, 2, 4],
        labels=["Low", "Medium", "Elevated", "Critical"],
    )

    return data


def generate_business_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes data-driven business findings and analyst recommendations based strictly on dataset metrics.
    """
    kpis = calculate_kpis(df)
    cat_df = get_category_metrics(df)
    state_df = get_state_metrics(df)
    monthly_df = get_monthly_trends(df)
    hourly_df = get_hourly_trends(df)

    # 1. Category insights
    highest_fraud_rate_cat = cat_df.iloc[0]
    highest_fraud_vol_cat = cat_df.sort_values("fraud_transactions", ascending=False).iloc[0]

    # 2. State insights
    highest_vol_state = state_df.sort_values("fraud_transactions", ascending=False).iloc[0]
    # Filter states with meaningful volume (e.g. >= 5000 transactions)
    qualified_states = state_df[state_df["total_transactions"] >= 5000]
    highest_rate_state = (
        qualified_states.sort_values("fraud_rate", ascending=False).iloc[0]
        if len(qualified_states) > 0
        else state_df.sort_values("fraud_rate", ascending=False).iloc[0]
    )

    # 3. Monthly insights
    highest_month = monthly_df.sort_values("fraud_transactions", ascending=False).iloc[0]

    # 4. Hourly insights
    peak_hour = hourly_df.sort_values("fraud_transactions", ascending=False).iloc[0]

    return {
        "kpis": kpis,
        "highest_fraud_rate_category": {
            "category": str(highest_fraud_rate_cat["category"]),
            "fraud_rate": round(float(highest_fraud_rate_cat["fraud_rate"]), 3),
            "fraud_transactions": int(highest_fraud_rate_cat["fraud_transactions"]),
            "total_transactions": int(highest_fraud_rate_cat["total_transactions"]),
        },
        "highest_fraud_vol_category": {
            "category": str(highest_fraud_vol_cat["category"]),
            "fraud_transactions": int(highest_fraud_vol_cat["fraud_transactions"]),
            "total_transactions": int(highest_fraud_vol_cat["total_transactions"]),
            "fraud_rate": round(float(highest_fraud_vol_cat["fraud_rate"]), 3),
        },
        "highest_fraud_volume_state": {
            "state": str(highest_vol_state["state"]),
            "fraud_transactions": int(highest_vol_state["fraud_transactions"]),
            "total_transactions": int(highest_vol_state["total_transactions"]),
            "fraud_rate": round(float(highest_vol_state["fraud_rate"]), 3),
        },
        "highest_fraud_rate_state": {
            "state": str(highest_rate_state["state"]),
            "fraud_rate": round(float(highest_rate_state["fraud_rate"]), 3),
            "fraud_transactions": int(highest_rate_state["fraud_transactions"]),
            "total_transactions": int(highest_rate_state["total_transactions"]),
        },
        "highest_fraud_month": {
            "month": str(highest_month["year_month"]),
            "fraud_transactions": int(highest_month["fraud_transactions"]),
            "total_transactions": int(highest_month["total_transactions"]),
            "fraud_rate": round(float(highest_month["fraud_rate"]), 3),
        },
        "peak_fraud_hour": {
            "hour": int(peak_hour["hour"]),
            "fraud_transactions": int(peak_hour["fraud_transactions"]),
            "fraud_rate": round(float(peak_hour["fraud_rate"]), 3),
        },
        "amount_disparity": {
            "avg_legit_amt": kpis["avg_legit_amount"],
            "avg_fraud_amt": kpis["avg_fraud_amount"],
            "ratio": kpis["amount_fraud_ratio"],
        },
    }


def get_hour_weekday_matrix(df: pd.DataFrame, metric: str = "fraud_count") -> pd.DataFrame:
    """
    Computes a 2D matrix of Day of Week (rows) vs Hour of Day (columns 0-23).
    metric can be 'fraud_count' or 'fraud_rate'.
    """
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if metric == "fraud_count":
        pivot = df.pivot_table(
            index="day_name",
            columns="hour",
            values="is_fraud",
            aggfunc="sum",
            fill_value=0,
            observed=False,
        )
    else:
        pivot = df.pivot_table(
            index="day_name",
            columns="hour",
            values="is_fraud",
            aggfunc=lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0,
            fill_value=0,
            observed=False,
        )
    return pivot.reindex(order)


def get_creditcard_metrics(cc_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes statistical and PCA correlation metrics on the creditcard.csv dataset.
    """
    total = len(cc_df)
    fraud = int(cc_df["Class"].sum())
    legit = total - fraud
    fraud_rate = (fraud / total) * 100.0

    total_amt = float(cc_df["Amount"].sum())
    fraud_amt = float(cc_df[cc_df["Class"] == 1]["Amount"].sum())
    legit_amt = total_amt - fraud_amt

    mean_amt = float(cc_df["Amount"].mean())
    mean_fraud_amt = float(cc_df[cc_df["Class"] == 1]["Amount"].mean())
    mean_legit_amt = float(cc_df[cc_df["Class"] == 0]["Amount"].mean())
    median_fraud_amt = float(cc_df[cc_df["Class"] == 1]["Amount"].median())
    median_legit_amt = float(cc_df[cc_df["Class"] == 0]["Amount"].median())

    # PCA feature correlation with target Class
    corrs = cc_df.corr()["Class"].drop("Class").sort_values()

    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "legitimate_transactions": legit,
        "fraud_rate": round(fraud_rate, 4),
        "total_amount": round(total_amt, 2),
        "fraud_amount": round(fraud_amt, 2),
        "legit_amount": round(legit_amt, 2),
        "mean_amount": round(mean_amt, 2),
        "mean_fraud_amount": round(mean_fraud_amt, 2),
        "mean_legit_amount": round(mean_legit_amt, 2),
        "median_fraud_amount": round(median_fraud_amt, 2),
        "median_legit_amount": round(median_legit_amt, 2),
        "correlations": corrs.to_dict(),
        "top_negative_features": corrs.head(5).to_dict(),
        "top_positive_features": corrs.tail(5).sort_values(ascending=False).to_dict(),
    }


def compare_fraud_datasets(df_retail: pd.DataFrame, cc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a formal comparative benchmark table between:
    - Primary Dataset (e-Commerce / Retail transactions, 1.85M records)
    - Credit Card PCA Dataset (European Banking, 284K records)
    """
    kpis_retail = calculate_kpis(df_retail)
    kpis_cc = get_creditcard_metrics(cc_df)

    rows = [
        {"Dimension": "Dataset Title", "Primary Dataset (archive (8).zip)": "Financial Fraud Train/Test", "Credit Card Dataset (creditcard.csv)": "Credit Card Fraud Detection (Kaggle/ULB)"},
        {"Dimension": "Domain / Context", "Primary Dataset (archive (8).zip)": "US Retail & Online Merchants (2019-2020)", "Credit Card Dataset (creditcard.csv)": "European Cardholders (2-Day Swipes, Sept 2013)"},
        {"Dimension": "Total Volume", "Primary Dataset (archive (8).zip)": f"{kpis_retail['total_transactions']:,}", "Credit Card Dataset (creditcard.csv)": f"{kpis_cc['total_transactions']:,}"},
        {"Dimension": "Historical Fraud Count", "Primary Dataset (archive (8).zip)": f"{kpis_retail['fraud_transactions']:,}", "Credit Card Dataset (creditcard.csv)": f"{kpis_cc['fraud_transactions']:,}"},
        {"Dimension": "Baseline Fraud Rate", "Primary Dataset (archive (8).zip)": f"{kpis_retail['fraud_rate']:.3f}%", "Credit Card Dataset (creditcard.csv)": f"{kpis_cc['fraud_rate']:.3f}%"},
        {"Dimension": "Mean Legit Ticket", "Primary Dataset (archive (8).zip)": f"${kpis_retail['avg_legit_amount']:.2f}", "Credit Card Dataset (creditcard.csv)": f"${kpis_cc['mean_legit_amount']:.2f}"},
        {"Dimension": "Mean Fraud Ticket", "Primary Dataset (archive (8).zip)": f"${kpis_retail['avg_fraud_amount']:.2f}", "Credit Card Dataset (creditcard.csv)": f"${kpis_cc['mean_fraud_amount']:.2f}"},
        {"Dimension": "Disparity Ratio", "Primary Dataset (archive (8).zip)": f"{kpis_retail['amount_fraud_ratio']:.2f}x (Higher fraud tickets)", "Credit Card Dataset (creditcard.csv)": f"{kpis_cc['mean_fraud_amount']/kpis_cc['mean_legit_amount']:.2f}x (Modest ticket difference)"},
        {"Dimension": "Feature Representation", "Primary Dataset (archive (8).zip)": "Domain attributes (Category, Merchant, Geo Lat/Long, DOB)", "Credit Card Dataset (creditcard.csv)": "PCA Dimensionality Reduced (V1 to V28) + Time, Amount"},
        {"Dimension": "Primary Detection Vector", "Primary Dataset (archive (8).zip)": "Nocturnal window, Category velocity, Geo distance", "Credit Card Dataset (creditcard.csv)": "PCA subspace anomalies (V14, V17, V12 negative separation)"},
    ]
    return pd.DataFrame(rows)


def get_radar_profiles(df: pd.DataFrame) -> Tuple[List[str], List[float], List[float]]:
    """
    Computes comparative multi-dimensional risk footprint normalized to [0, 100]
    comparing Legitimate vs Fraudulent transactions.
    """
    fraud_mask = df["is_fraud"] == 1
    legit_mask = df["is_fraud"] == 0

    categories = ["Average Ticket", "Nocturnal Probability", "Distance Outlier", "High-Risk Category", "Weekend Ratio"]

    # 1. Average Ticket
    fraud_amt = float(df.loc[fraud_mask, "amt"].mean()) if fraud_mask.any() else 0.0
    legit_amt = float(df.loc[legit_mask, "amt"].mean()) if legit_mask.any() else 0.0
    max_amt = max(fraud_amt, legit_amt, 1.0)
    score_fraud_amt = (fraud_amt / max_amt) * 100
    score_legit_amt = (legit_amt / max_amt) * 100

    # 2. Nocturnal Probability (22:00 to 03:00)
    if "hour" in df.columns:
        night_hours = [22, 23, 0, 1, 2, 3]
        fraud_night = float(df.loc[fraud_mask, "hour"].isin(night_hours).mean()) * 100 if fraud_mask.any() else 0.0
        legit_night = float(df.loc[legit_mask, "hour"].isin(night_hours).mean()) * 100 if legit_mask.any() else 0.0
    else:
        fraud_night, legit_night = 50.0, 50.0

    # 3. Distance Outlier (> 50 km)
    if "distance_km" in df.columns:
        fraud_dist = float((df.loc[fraud_mask, "distance_km"] > 50).mean()) * 100 if fraud_mask.any() else 0.0
        legit_dist = float((df.loc[legit_mask, "distance_km"] > 50).mean()) * 100 if legit_mask.any() else 0.0
    else:
        fraud_dist, legit_dist = 20.0, 20.0

    # 4. High-Risk Category (shopping_net, grocery_pos, misc_net)
    high_cats = ["shopping_net", "grocery_pos", "misc_net"]
    fraud_cat = float(df.loc[fraud_mask, "category"].astype(str).isin(high_cats).mean()) * 100 if fraud_mask.any() else 0.0
    legit_cat = float(df.loc[legit_mask, "category"].astype(str).isin(high_cats).mean()) * 100 if legit_mask.any() else 0.0

    # 5. Weekend Ratio
    if "is_weekend" in df.columns:
        fraud_wknd = float(df.loc[fraud_mask, "is_weekend"].mean()) * 100 if fraud_mask.any() else 0.0
        legit_wknd = float(df.loc[legit_mask, "is_weekend"].mean()) * 100 if legit_mask.any() else 0.0
    else:
        fraud_wknd, legit_wknd = 28.5, 28.5

    fraud_scores = [round(score_fraud_amt, 1), round(fraud_night, 1), round(fraud_dist, 1), round(fraud_cat, 1), round(fraud_wknd, 1)]
    legit_scores = [round(score_legit_amt, 1), round(legit_night, 1), round(legit_dist, 1), round(legit_cat, 1), round(legit_wknd, 1)]

    return categories, legit_scores, fraud_scores


def simulate_threshold_interception(
    df: pd.DataFrame,
    amount_cutoff: float = 300.0,
    distance_cutoff: float = 80.0,
    night_window_active: bool = True,
) -> Dict[str, Any]:
    """
    What-If Simulation Engine: Calculates the operational tradeoff between
    intercepted fraud dollars/cases and analyst review workload across chosen thresholds.
    """
    total_records = len(df)
    total_fraud_records = int((df["is_fraud"] == 1).sum())
    total_fraud_dollars = float(df.loc[df["is_fraud"] == 1, "amt"].sum())

    flag_amount = df["amt"] >= amount_cutoff
    flag_distance = (df["distance_km"] >= distance_cutoff) if "distance_km" in df.columns else False
    if night_window_active and "hour" in df.columns:
        flag_night = (df["hour"] >= 22) | (df["hour"] <= 3)
    else:
        flag_night = False

    # Combined heuristic flag (triggered if amount exceeded OR (night + distance))
    flagged = flag_amount | (flag_night & flag_distance)

    total_flagged = int(flagged.sum())
    fraud_caught = int((flagged & (df["is_fraud"] == 1)).sum())
    fraud_dollars_caught = float(df.loc[flagged & (df["is_fraud"] == 1), "amt"].sum())
    false_positives = total_flagged - fraud_caught

    recall_cases_pct = (fraud_caught / total_fraud_records * 100.0) if total_fraud_records > 0 else 0.0
    recall_dollars_pct = (fraud_dollars_caught / total_fraud_dollars * 100.0) if total_fraud_dollars > 0 else 0.0
    workload_rate_pct = (total_flagged / total_records * 100.0) if total_records > 0 else 0.0
    precision_pct = (fraud_caught / total_flagged * 100.0) if total_flagged > 0 else 0.0

    return {
        "total_flagged": total_flagged,
        "fraud_caught": fraud_caught,
        "total_fraud_records": total_fraud_records,
        "fraud_dollars_caught": round(fraud_dollars_caught, 2),
        "total_fraud_dollars": round(total_fraud_dollars, 2),
        "false_positives": false_positives,
        "recall_cases_pct": round(recall_cases_pct, 2),
        "recall_dollars_pct": round(recall_dollars_pct, 2),
        "workload_rate_pct": round(workload_rate_pct, 2),
        "precision_pct": round(precision_pct, 2),
    }


def calculate_single_transaction_risk(
    amt: float, category: str, hour: int, distance_km: float
) -> Dict[str, Any]:
    """
    Computes a transparent, multi-vector 0 to 100 risk score for a single transaction.
    """
    score = 0.0
    factors = []

    # Amount factor (up to 40 points)
    if amt >= 500:
        score += 40.0
        factors.append(f"Critical Ticket Amount (${amt:.2f} >= $500: +40 pts)")
    elif amt >= 300:
        score += 25.0
        factors.append(f"Elevated Ticket Amount (${amt:.2f} >= $300: +25 pts)")
    elif amt >= 150:
        score += 10.0
        factors.append(f"Moderate Ticket Amount (${amt:.2f} >= $150: +10 pts)")

    # Diurnal Hour factor (up to 30 points)
    if hour in [22, 23, 0, 1, 2]:
        score += 30.0
        factors.append(f"Peak Nocturnal Surge Window (Hour {hour}:00: +30 pts)")
    elif hour in [3, 4, 21]:
        score += 15.0
        factors.append(f"Off-Peak Night Window (Hour {hour}:00: +15 pts)")

    # Category factor (up to 20 points)
    high_cats = ["shopping_net", "grocery_pos", "misc_net"]
    if category in high_cats:
        score += 20.0
        factors.append(f"High-Risk Vulnerable Category ({category}: +20 pts)")

    # Distance factor (up to 10 points)
    if distance_km >= 100:
        score += 10.0
        factors.append(f"Extreme Haversine Distance ({distance_km:.1f} km >= 100 km: +10 pts)")
    elif distance_km >= 50:
        score += 5.0
        factors.append(f"Elevated Haversine Distance ({distance_km:.1f} km >= 50 km: +5 pts)")

    score = min(score, 100.0)

    if score >= 70:
        risk_level = "CRITICAL RISK"
        recommendation = "🚨 Intercept & Hold: Immediate Step-Up Biometric / 3DS Challenge"
        color = "#EF4444"
    elif score >= 45:
        risk_level = "ELEVATED RISK"
        recommendation = "⚠️ Secondary Verification: Trigger Out-of-Band SMS / Push OTP"
        color = "#F59E0B"
    elif score >= 25:
        risk_level = "MODERATE RISK"
        recommendation = "ℹ️ Passive Monitoring: Log Transaction to Analyst Triage Queue"
        color = "#38BDF8"
    else:
        risk_level = "LOW RISK"
        recommendation = "✅ Automated Approval: Normal Commercial Frictionless Flow"
        color = "#10B981"

    return {
        "score": score,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "color": color,
        "factors": factors,
    }
