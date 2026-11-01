"""
Page 4: Transaction Explorer & Investigation Triage
Searchable ledger, multi-parameter forensic filters, and transparent business-rule investigation scanner.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
from src.analytics import evaluate_investigation_rules
from src.validate_data import validate_data_quality, validate_raw_schema
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Transaction Explorer | Financial Fraud Analytics",
    page_icon="🔍",
    layout="wide",
)

apply_theme()
df_raw = get_dataset()
df = render_sidebar_filters(df_raw)

render_hero(
    title="Transaction Forensic Explorer & Triage Scanner",
    subtitle=(
        "Searchable transaction ledger with real-time heuristic rule evaluation, "
        "anomaly indicator scoring, and CSV transaction batch validation."
    ),
    badge_text="EXPLORER & TRIAGE",
)

# Tabs: 1. Historical Explorer | 2. Heuristic Triage Scanner | 3. External CSV Batch Validator
tab_exp, tab_triage, tab_upload = st.tabs([
    "🔍 Historical Ledger Explorer",
    "🛡️ Configurable Rule Scanner",
    "📂 External CSV Batch Ingestion",
])

with tab_exp:
    st.markdown("### 🔎 Search & Filter Historical Transactions")

    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("Search by Merchant Name or Transaction ID:", placeholder="e.g. fraud_Rippin or merchant name")
    with col_s2:
        min_amt, max_amt = st.slider("Amount Range ($)", 0.0, 5000.0, (0.0, 2500.0))
    with col_s3:
        max_records = st.selectbox("Display Limit", [100, 250, 500, 1000], index=1)

    # Filter by search and amount
    exp_df = df[(df["amt"] >= min_amt) & (df["amt"] <= max_amt)]

    if search_query:
        merchant_col = "clean_merchant" if "clean_merchant" in exp_df.columns else "merchant"
        mask = (
            exp_df[merchant_col].astype(str).str.contains(search_query, case=False, na=False)
            | exp_df["trans_num"].astype(str).str.contains(search_query, case=False, na=False)
        )
        exp_df = exp_df[mask]

    st.markdown(f"**Showing top {min(len(exp_df), max_records):,} of {len(exp_df):,} matching records**")

    display_cols = [
        "trans_num",
        "trans_date_trans_time",
        "clean_merchant",
        "category",
        "amt",
        "state",
        "city",
        "age",
        "distance_km",
        "is_fraud",
    ]
    avail_cols = [c for c in display_cols if c in exp_df.columns]

    st.dataframe(
        exp_df[avail_cols].head(max_records).rename(columns={
            "trans_num": "Trans ID",
            "trans_date_trans_time": "Timestamp",
            "clean_merchant": "Merchant",
            "category": "Category",
            "amt": "Amount ($)",
            "state": "State",
            "city": "City",
            "age": "Age",
            "distance_km": "Distance (km)",
            "is_fraud": "Historical Fraud",
        }).style.format({
            "Amount ($)": "${:.2f}",
            "Distance (km)": "{:.1f}",
            "Age": "{:.0f}",
        }),
        use_container_width=True,
        height=450,
    )

with tab_triage:
    st.markdown("### ⚙️ Transparent Business-Rule Investigation Scanner")
    st.info(
        "ℹ️ **Regulatory Notice**: These heuristic indicators are transparent analyst triage flags, "
        "not black-box ML predictions. Triggering flags signifies that a transaction warrants priority analyst review."
    )

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        amt_thresh = st.number_input("High Amount Threshold ($)", min_value=50.0, max_value=5000.0, value=300.0, step=50.0)
    with col_r2:
        dist_thresh = st.number_input("High Distance Threshold (km)", min_value=10.0, max_value=500.0, value=80.0, step=10.0)
    with col_r3:
        night_window = st.checkbox("Flag Late-Night Hours (22:00 - 04:00)", value=True)

    # Evaluate rules on active sample
    sample_for_rules = df.head(5000)
    flagged = evaluate_investigation_rules(
        sample_for_rules,
        amount_threshold=amt_thresh,
        distance_threshold=dist_thresh,
        night_start=22 if night_window else 99,
        night_end=4 if night_window else -1,
    )

    # Risk level distribution metrics
    r_counts = flagged["risk_level"].value_counts()
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.metric("Critical Risk (3-4 Flags)", int(r_counts.get("Critical", 0)))
    with c_m2:
        st.metric("Elevated Risk (2 Flags)", int(r_counts.get("Elevated", 0)))
    with c_m3:
        st.metric("Medium Risk (1 Flag)", int(r_counts.get("Medium", 0)))
    with c_m4:
        st.metric("Low Risk (0 Flags)", int(r_counts.get("Low", 0)))

    # Display flagged transactions
    st.markdown("#### High-Priority Flagged Transactions (Sample of 5,000)")
    priority_records = flagged[flagged["risk_score"] >= 2].head(200)

    st.dataframe(
        priority_records[[
            "trans_num",
            "clean_merchant",
            "category",
            "amt",
            "hour",
            "distance_km",
            "risk_score",
            "risk_level",
            "is_fraud",
        ]].rename(columns={
            "trans_num": "Trans ID",
            "clean_merchant": "Merchant",
            "category": "Category",
            "amt": "Amount ($)",
            "hour": "Hour",
            "distance_km": "Dist (km)",
            "risk_score": "Flags Triggered",
            "risk_level": "Risk Tier",
            "is_fraud": "Historical Label",
        }).style.format({
            "Amount ($)": "${:.2f}",
            "Dist (km)": "{:.1f}",
        }),
        use_container_width=True,
        height=380,
    )

with tab_upload:
    st.markdown("### 📂 Ingest & Validate External Transaction File")
    st.markdown(
        "Upload a batch CSV file of transactions to validate schema integrity, audit data hygiene, "
        "and scan against configurable heuristic risk rules."
    )

    uploaded_file = st.file_uploader("Upload CSV transaction file (e.g. new test batch)", type=["csv"])

    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file, nrows=10000)
            st.success(f"Successfully parsed {len(user_df):,} records from {uploaded_file.name}")

            # Run quality checks
            quality = validate_data_quality(user_df, dataset_name=uploaded_file.name)
            schema = validate_raw_schema(user_df, dataset_name=uploaded_file.name)

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                st.markdown("#### Schema Validation Results")
                if schema["is_schema_valid"]:
                    st.success("✅ All expected schema fields are present.")
                else:
                    st.warning(f"⚠️ Missing columns: {schema['missing_expected_columns']}")

            with col_u2:
                st.markdown("#### Quality Audit Results")
                st.write(f"- Total Rows: **{quality['total_rows']:,}**")
                st.write(f"- Missing Values: **{quality['missing_values_total']:,}**")
                st.write(f"- Duplicate Rows: **{quality['duplicate_rows']:,}**")
                if "fraud_rate_pct" in quality:
                    st.write(f"- Fraud Label Rate: **{quality['fraud_rate_pct']:.3f}%**")

            # Preview
            st.markdown("#### Uploaded Transaction Preview (First 20 records)")
            st.dataframe(user_df.head(20), use_container_width=True)

        except Exception as e:
            st.error(f"Failed to process uploaded file: {str(e)}")
