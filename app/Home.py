"""
Financial Fraud Detection & Analytics Dashboard
Executive Command Center Page
Designed in accordance with modern cyber-forensic command centers (concentric gauges,
2D hour-weekday matrix, geospatial heatmaps, live alert cards, and real-time anomaly waveforms).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import (
    calculate_kpis,
    get_monthly_trends,
    get_category_metrics,
    get_hourly_trends,
    get_weekday_trends,
    get_hour_weekday_matrix,
    get_merchant_metrics,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_circular_gauge,
    render_alert_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Executive Command Center | Financial Fraud Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# Load primary processed dataset
df_raw = get_dataset()

# Render global filters
df = render_sidebar_filters(df_raw)

# Calculate global KPIs
kpis = calculate_kpis(df)

# Command Center Header with live pulse counter
render_hero(
    title="Financial Fraud Intelligence Command Center",
    subtitle=(
        "Enterprise cyber-forensic surveillance platform tracking 1.85M historical financial transactions. "
        "Real-time anomaly triage, diurnal vulnerability detection, and cross-channel risk monitoring."
    ),
    badge_text="COMMAND CENTER LIVE",
    pulse_alert=f"{kpis['fraud_transactions']:,} FRAUD INCIDENTS AUDITED",
)

# Row 1: Executive KPI Scorecards with Delta Badges (Image 2 Style)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        render_kpi_card("Total Ledger Volume", f"{kpis['total_transactions']:,}", f"{kpis['legitimate_transactions']:,} Legit", "neutral", "1.85M Lifetime", "neutral"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        render_kpi_card("Historical Fraud Cases", f"{kpis['fraud_transactions']:,}", f"Prevalence: {kpis['fraud_rate']:.3f}%", "fraud", "▲ 0.52% Baseline", "up"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        render_kpi_card("Total Financial Turnover", f"${kpis['total_amount']:,.0f}", f"Avg Ticket: ${kpis['avg_amount']:.2f}", "legit", "$129.8M Gross", "neutral"),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        render_kpi_card("Fraud Dollar Turnover", f"${kpis['fraud_amount']:,.0f}", f"Share: {kpis['fraud_amount_share']:.2f}% of Spend", "warning", "▲ 3.95% Exposure", "up"),
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        render_kpi_card("Disparity Multiplier", f"{kpis['amount_fraud_ratio']:.1f}x", f"${kpis['avg_fraud_amount']:.0f} vs ${kpis['avg_legit_amount']:.0f}", "fraud", "▲ 7.84x Avg Ticket", "up"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Command Center Triad (Image 1 Layout: Circular Gauges | Map | Anomaly Wave)
col_gauges, col_map, col_wave = st.columns([1.2, 2.2, 1.6])

with col_gauges:
    st.markdown("#### 🎯 System Risk Gauges")
    # Gauge 1: Fraud Rate %
    st.markdown(render_circular_gauge("System Fraud Rate", kpis["fraud_rate"], "#EF4444", "Prevalence in ledger", f"{kpis['fraud_rate']:.2f}%"), unsafe_allow_html=True)
    # Gauge 2: Dollar Exposure %
    st.markdown(render_circular_gauge("Dollar Exposure", kpis["fraud_amount_share"], "#F59E0B", "Share of total turnover", f"{kpis['fraud_amount_share']:.1f}%"), unsafe_allow_html=True)
    # Gauge 3: Peak Nocturnal Hour % (Hour 22)
    st.markdown(render_circular_gauge("Peak Nocturnal Surge", 2.60, "#EF4444", "22:00 window fraud rate", "2.60%"), unsafe_allow_html=True)
    # Gauge 4: Top Category Risk (shopping_net)
    st.markdown(render_circular_gauge("E-Commerce Risk", 1.59, "#38BDF8", "shopping_net fraud rate", "1.59%"), unsafe_allow_html=True)

with col_map:
    st.markdown("#### 🗺️ Geospatial Forensic Cluster Map")
    # Subsample points for smooth high-FPS rendering
    sample_geo = df.sample(n=min(3000, len(df)), random_state=42) if len(df) > 3000 else df
    fig_geo = px.scatter_geo(
        sample_geo,
        lat="lat",
        lon="long",
        color="is_fraud",
        color_discrete_map={0: "rgba(56, 189, 248, 0.4)", 1: "#EF4444"},
        size=sample_geo["amt"].clip(upper=1000),
        size_max=12,
        scope="usa",
        title="Live US Transaction Clusters & Hotspots (Red = Fraud)",
    )
    fig_geo.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        geo=dict(bgcolor="rgba(15, 23, 42, 0.0)", lakecolor="rgba(15, 23, 42, 0.3)"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig_geo, use_container_width=True)

with col_wave:
    st.markdown("#### 📈 Anomaly Detection Wave")
    monthly_data = get_monthly_trends(df)
    fig_wave = go.Figure()
    fig_wave.add_trace(
        go.Scatter(
            x=monthly_data["year_month"],
            y=monthly_data["fraud_transactions"],
            mode="lines+markers",
            line=dict(color="#38BDF8", width=3, shape="spline"),
            marker=dict(size=6, color="#0EA5E9"),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.12)",
            name="Fraud Trend",
        )
    )
    fig_wave.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=10, r=10, t=30, b=30),
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="Fraud Cases"),
        height=380,
    )
    st.plotly_chart(fig_wave, use_container_width=True)

# Row 3: Matrix Heatmap & Risk Distribution (Image 2 & 3 Middle Section)
st.markdown("<br>", unsafe_allow_html=True)
col_hm, col_donut, col_triage = st.columns([2.2, 1.4, 2.0])

with col_hm:
    st.markdown("#### 🗓️ Attack Vector Heatmap: Day of Week × Hour (Image 2 Style)")
    matrix_df = get_hour_weekday_matrix(df, metric="fraud_count")
    fig_matrix = px.imshow(
        matrix_df,
        labels=dict(x="Hour of Day (0 to 23)", y="Day of Week", color="Fraud Cases"),
        x=matrix_df.columns,
        y=matrix_df.index,
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig_matrix.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=30, b=30),
        height=320,
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

with col_donut:
    st.markdown("#### 🍩 Risk Tier Breakdown")
    cat_df = get_category_metrics(df).head(5)
    fig_donut = px.pie(
        cat_df,
        names="category",
        values="fraud_transactions",
        hole=0.6,
        color_discrete_sequence=["#EF4444", "#F59E0B", "#38BDF8", "#10B981", "#8B5CF6"],
    )
    fig_donut.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        showlegend=False,
        annotations=[dict(text=f"<b>{kpis['fraud_transactions']:,}</b><br><span style='font-size:10px; color:#94A3B8;'>Fraud Cases</span>", x=0.5, y=0.5, font_size=16, showarrow=False)],
    )
    fig_donut.update_traces(textposition="inside", textinfo="percent")
    st.plotly_chart(fig_donut, use_container_width=True)

with col_triage:
    st.markdown("#### ⚠️ High-Risk Commercial Entities (Image 3 Table)")
    merch_triage = get_merchant_metrics(df, top_n=6)
    st.dataframe(
        merch_triage[["clean_merchant", "total_transactions", "fraud_transactions", "fraud_rate"]].rename(columns={
            "clean_merchant": "Merchant Name",
            "total_transactions": "Volume",
            "fraud_transactions": "Fraud Cases",
            "fraud_rate": "Fraud Rate (%)",
        }).style.format({
            "Volume": "{:,}",
            "Fraud Cases": "{:,}",
            "Fraud Rate (%)": "{:.3f}%",
        }),
        use_container_width=True,
        height=320,
    )

# Row 4: Recent Forensic Incident Ticker / Alert Stream (Image 3 Bottom Row)
st.markdown("### 🚨 Live Forensic Incident Feed & Anomaly Alerts")
st.markdown('<div class="alert-grid">', unsafe_allow_html=True)

col_a1, col_a2, col_a3, col_a4 = st.columns(4)

with col_a1:
    st.markdown(
        render_alert_card(
            alert_type="Nocturnal Surge Window",
            entity_id="HOUR 22:00 SPIKE",
            details="2,481 confirmed fraud transactions concentrated at 22:00 (2.60% fraud rate, 5x daytime baseline).",
            time_str="22:00 - 03:00",
        ),
        unsafe_allow_html=True,
    )

with col_a2:
    st.markdown(
        render_alert_card(
            alert_type="Ticket Size Disparity",
            entity_id="VALUE OUTLIER",
            details="Average fraudulent purchase ticket is $530.66 vs $67.65 for legitimate purchases (7.84x disparity ratio).",
            time_str="All Channels",
        ),
        unsafe_allow_html=True,
    )

with col_a3:
    st.markdown(
        render_alert_card(
            alert_type="E-Commerce Vulnerability",
            entity_id="shopping_net",
            details="E-commerce shopping exhibits the highest historical fraud rate (1.593%), with grocery_pos leading in volume (2,228 cases).",
            time_str="Online Pos",
        ),
        unsafe_allow_html=True,
    )

with col_a4:
    st.markdown(
        render_alert_card(
            alert_type="Geographic Hub Risk",
            entity_id="NY & OR CLUSTER",
            details="New York state leads nationwide in fraud incident volume (730 cases). Oregon exhibits elevated rate (0.746%).",
            time_str="Metro Corridor",
        ),
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Strategic Footnote
st.markdown(
    """
    <div style="font-size: 0.78rem; color: #64748B; margin-top: 20px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08);">
        <b>Forensic Notice:</b> This command center aggregates historical transaction records for financial crime analysis. 
        All monetary amounts represent historical transaction amounts.
    </div>
    """,
    unsafe_allow_html=True,
)
