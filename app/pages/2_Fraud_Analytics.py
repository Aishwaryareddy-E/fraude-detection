"""
Page 2: Fraud Analytics Module
Deep-dive forensic analysis into fraud rate vs fraud volume, temporal cycles,
weekday distributions, and category vulnerabilities.
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
    get_category_metrics,
    get_hourly_trends,
    get_weekday_trends,
    get_monthly_trends,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Fraud Analytics | Financial Fraud Analytics",
    page_icon="🚨",
    layout="wide",
)

apply_theme()
df_raw = get_dataset()
df = render_sidebar_filters(df_raw)

render_hero(
    title="Historical Fraud Pattern Analytics",
    subtitle=(
        "Forensic evaluation distinguishing between raw fraud count and relative fraud rate (%). "
        "Uncovers diurnal cycles, weekly spikes, and high-vulnerability commercial categories."
    ),
    badge_text="FRAUD FORENSICS",
)

kpis = calculate_kpis(df)

# Top KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        render_kpi_card("Fraud Incidents", f"{kpis['fraud_transactions']:,}", f"Rate: {kpis['fraud_rate']:.3f}%", "fraud", "🚨"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        render_kpi_card("Fraud Dollar Volume", f"${kpis['fraud_amount']:,.0f}", f"{kpis['fraud_amount_share']:.2f}% of total spend", "warning", "💸"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        render_kpi_card("Avg Fraud Ticket", f"${kpis['avg_fraud_amount']:.2f}", f"Legit avg: ${kpis['avg_legit_amount']:.2f}", "fraud", "🏷️"),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        render_kpi_card("Value Disparity Ratio", f"{kpis['amount_fraud_ratio']:.1f}x", "Fraud ticket multiplier", "neutral", "⚖️"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Callout banner: Avoiding Analytical Bias
st.info(
    "💡 **Analytical Best Practice (Count vs Rate)**: A high transaction count can artificially elevate raw fraud counts. "
    "To isolate true systemic vulnerability, always contrast raw fraud counts against normalized fraud rates (%)."
)

# Section 1: Fraud Rate vs Fraud Volume by Category
st.markdown("### 🏷️ Category Forensic Matrix: Fraud Rate (%) vs Fraud Count")

cat_df = get_category_metrics(df)

col_mat1, col_mat2 = st.columns([1, 1])

with col_mat1:
    # Ranked by Fraud Rate
    fig_cat_rate = px.bar(
        cat_df.sort_values("fraud_rate", ascending=True),
        x="fraud_rate",
        y="category",
        orientation="h",
        color="fraud_rate",
        color_continuous_scale="Reds",
        labels={"fraud_rate": "Fraud Rate (%)", "category": "Category"},
        title="Ranked by Vulnerability (Fraud Rate %)",
    )
    fig_cat_rate.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_cat_rate, use_container_width=True)

with col_mat2:
    # Ranked by Raw Fraud Volume
    fig_cat_vol = px.bar(
        cat_df.sort_values("fraud_transactions", ascending=True),
        x="fraud_transactions",
        y="category",
        orientation="h",
        color="fraud_transactions",
        color_continuous_scale="Oranges",
        labels={"fraud_transactions": "Fraud Cases", "category": "Category"},
        title="Ranked by Raw Exposure (Fraud Cases)",
    )
    fig_cat_vol.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_cat_vol, use_container_width=True)

# Section 2: Diurnal & Weekly Temporal Cycles
st.markdown("### ⏳ Temporal Attack Vectors: Diurnal & Day-of-Week Patterns")

col_t1, col_t2 = st.columns(2)

with col_t1:
    hourly_df = get_hourly_trends(df)
    fig_hour_dual = go.Figure()

    fig_hour_dual.add_trace(
        go.Bar(
            x=hourly_df["hour"],
            y=hourly_df["fraud_transactions"],
            name="Fraud Cases",
            marker_color="rgba(239, 68, 68, 0.6)",
        )
    )
    fig_hour_dual.add_trace(
        go.Scatter(
            x=hourly_df["hour"],
            y=hourly_df["fraud_rate"],
            name="Fraud Rate (%)",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#38BDF8", width=3),
        )
    )
    fig_hour_dual.update_layout(
        title="Hourly Attack Cycle (Hour 22 Spike)",
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis=dict(title="Hour of Day (0 to 23)", dtick=2),
        yaxis=dict(title="Fraud Incident Count", showgrid=False),
        yaxis2=dict(
            title="Fraud Rate (%)",
            overlaying="y",
            side="right",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_hour_dual, use_container_width=True)

with col_t2:
    weekday_df = get_weekday_trends(df)
    fig_week = px.bar(
        weekday_df,
        x="day_name",
        y="fraud_rate",
        color="fraud_transactions",
        color_continuous_scale="Reds",
        labels={"day_name": "Day of Week", "fraud_rate": "Fraud Rate (%)", "fraud_transactions": "Fraud Cases"},
        title="Day-of-Week Fraud Distribution",
    )
    fig_week.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=40, b=30),
    )
    st.plotly_chart(fig_week, use_container_width=True)

# Section 3: Value Disparity Insights
st.markdown("### 💰 Fraud Ticket Size Distribution Analysis")
st.markdown(
    """
    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <span style="color: #38BDF8; font-weight: 700; font-size: 1.05rem;">Forensic Finding on Dollar Disparity:</span><br>
        <span style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.6;">
            Legitimate credit card transactions in this dataset have a median of roughly <b>$47.00</b> and an average of <b>$67.65</b>. 
            In contrast, historically identified fraudulent transactions average <b>$530.66</b> (a <b>7.84x disparity</b>). 
            Transactions above $300 that occur during the late-night window (22:00 – 03:00) represent the highest concentration of fraud dollars.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
