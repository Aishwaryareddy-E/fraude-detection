"""
Page 3: Geographic Analytics Module
Evaluates spatial distribution, state-level fraud rates, choropleth maps,
and customer-to-merchant Haversine distance distributions.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import (
    calculate_kpis,
    get_state_metrics,
    get_distance_metrics,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Geographic Analytics | Financial Fraud Analytics",
    page_icon="🗺️",
    layout="wide",
)

apply_theme()
df_raw = get_dataset()
df = render_sidebar_filters(df_raw)

render_hero(
    title="Geospatial & Proximity Forensic Analytics",
    subtitle=(
        "State-level transaction mapping, regional fraud rate variations, and customer-to-merchant "
        "Haversine distance distributions across US jurisdictions."
    ),
    badge_text="GEOGRAPHIC ANALYTICS",
)

kpis = calculate_kpis(df)
state_metrics = get_state_metrics(df)

# Top KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        render_kpi_card("Active States", f"{df['state'].nunique():,}", "US jurisdictions tracked", "neutral", "🗺️"),
        unsafe_allow_html=True,
    )
with c2:
    top_vol_state = state_metrics.sort_values("fraud_transactions", ascending=False).iloc[0] if not state_metrics.empty else None
    st.markdown(
        render_kpi_card(
            "Top Fraud Volume State",
            f"{top_vol_state['state'] if top_vol_state is not None else 'N/A'}",
            f"{int(top_vol_state['fraud_transactions']):,} cases ({top_vol_state['fraud_rate']:.2f}%)" if top_vol_state is not None else "",
            "warning",
            "📍",
        ),
        unsafe_allow_html=True,
    )
with c3:
    # State with highest fraud rate (with min 1000 transactions)
    min_vol_states = state_metrics[state_metrics["total_transactions"] >= 1000]
    top_rate_state = min_vol_states.sort_values("fraud_rate", ascending=False).iloc[0] if not min_vol_states.empty else None
    st.markdown(
        render_kpi_card(
            "Highest Fraud Rate State",
            f"{top_rate_state['state'] if top_rate_state is not None else 'N/A'}",
            f"{top_rate_state['fraud_rate']:.3f}% ({int(top_rate_state['fraud_transactions']):,} cases)" if top_rate_state is not None else "",
            "fraud",
            "⚡",
        ),
        unsafe_allow_html=True,
    )
with c4:
    avg_dist = df["distance_km"].mean() if "distance_km" in df.columns else 0.0
    st.markdown(
        render_kpi_card("Mean Customer-Merch Dist", f"{avg_dist:.1f} km", "Haversine great-circle", "legit", "📏"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# US Choropleth Map
st.markdown("### 🇺🇸 State-by-State Fraud Concentration Map")

map_metric = st.radio(
    "Map Visual Metric:",
    ["Fraud Rate (%)", "Total Fraud Cases", "Total Transaction Volume"],
    horizontal=True,
)

if not state_metrics.empty:
    if map_metric == "Fraud Rate (%)":
        col_to_map = "fraud_rate"
        color_scale = "Reds"
        hover_name = "State"
    elif map_metric == "Total Fraud Cases":
        col_to_map = "fraud_transactions"
        color_scale = "Oranges"
    else:
        col_to_map = "total_transactions"
        color_scale = "Blues"

    fig_map = px.choropleth(
        state_metrics,
        locations="state",
        locationmode="USA-states",
        color=col_to_map,
        scope="usa",
        color_continuous_scale=color_scale,
        hover_data={"state": True, "total_transactions": ":,", "fraud_transactions": ":,", "fraud_rate": ":.3f%"},
        labels={"fraud_rate": "Fraud Rate (%)", "fraud_transactions": "Fraud Cases", "total_transactions": "Total Volume"},
    )
    fig_map.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        geo=dict(bgcolor="rgba(15, 23, 42, 0.0)", lakecolor="rgba(15, 23, 42, 0.4)"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=480,
    )
    st.plotly_chart(fig_map, use_container_width=True)

# Section: Customer-to-Merchant Distance Analysis
st.markdown("### 📍 Physical Proximity Analysis (Customer vs Merchant)")

st.warning(
    "⚠️ **Forensic Caution**: Physical distance is an exploratory contextual indicator, not an automatic proof of fraud. "
    "Legitimate e-commerce orders, travel transactions, and centralized fulfillment frequently have high distances without being fraudulent."
)

col_dist1, col_dist2 = st.columns([3, 2])

with col_dist1:
    dist_metrics = get_distance_metrics(df)
    if not dist_metrics.empty:
        fig_dist = px.bar(
            dist_metrics,
            x="distance_bin",
            y="total_transactions",
            color="fraud_rate",
            color_continuous_scale="Reds",
            labels={"distance_bin": "Distance Tier (km)", "total_transactions": "Transactions", "fraud_rate": "Fraud Rate (%)"},
            title="Transaction Volume across Distance Tiers (Color = Fraud Rate %)",
        )
        fig_dist.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=40, b=30),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with col_dist2:
    st.markdown("#### Distance Metrics Summary")
    if not dist_metrics.empty:
        st.dataframe(
            dist_metrics.rename(columns={
                "distance_bin": "Distance Tier",
                "total_transactions": "Total Volume",
                "fraud_transactions": "Fraud Cases",
                "fraud_rate": "Fraud Rate (%)",
                "avg_amount": "Avg Ticket ($)",
            }).style.format({
                "Total Volume": "{:,}",
                "Fraud Cases": "{:,}",
                "Fraud Rate (%)": "{:.3f}%",
                "Avg Ticket ($)": "${:.2f}",
            }),
            use_container_width=True,
        )

# State Ranking Data Table
st.markdown("### 📋 State-Level Forensic League Table")
st.dataframe(
    state_metrics.rename(columns={
        "state": "State",
        "total_transactions": "Total Volume",
        "fraud_transactions": "Fraud Cases",
        "fraud_rate": "Fraud Rate (%)",
        "total_amount": "Total Spend ($)",
    }).style.format({
        "Total Volume": "{:,}",
        "Fraud Cases": "{:,}",
        "Fraud Rate (%)": "{:.3f}%",
        "Total Spend ($)": "${:,.2f}",
    }),
    use_container_width=True,
)
