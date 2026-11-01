"""
Financial Fraud Detection & Analytics Dashboard
Executive Overview Page
Designed with an enterprise Power BI / Tableau Dark Theme layout using 100% real dataset metrics.
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
    get_merchant_metrics,
    evaluate_investigation_rules,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_powerbi_header,
    render_pbi_kpi,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Financial Fraud Detection | Executive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# Load primary processed dataset
df_raw = get_dataset()

# Render Power BI sidebar slicers
df = render_sidebar_filters(df_raw)

# Calculate core KPIs on active filtered data
kpis = calculate_kpis(df)

# Header Banner
render_powerbi_header(
    title="Financial Fraud Detection & Analytics System",
    subtitle="Enterprise Forensic Intelligence Dashboard | Auditing 1,852,394 Historical Transactions across 2019–2020",
    badge="GROUND-TRUTH ANALYTICS",
)

# Row 1: Executive Power BI KPI Cards
st.markdown('<div class="pbi-kpi-grid">', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(
        render_pbi_kpi(
            label="Total Transactions",
            value=f"{kpis['total_transactions']:,}",
            subtext=f"{kpis['legitimate_transactions']:,} Legit",
            delta="Audited",
            delta_type="neutral",
            card_type="neutral",
        ),
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        render_pbi_kpi(
            label="Fraud Incidents",
            value=f"{kpis['fraud_transactions']:,}",
            subtext=f"Prevalence: {kpis['fraud_rate']:.3f}%",
            delta="▲ Confirmed",
            delta_type="fraud",
            card_type="fraud",
        ),
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        render_pbi_kpi(
            label="Gross Dollar Volume",
            value=f"${kpis['total_amount']/1_000_000:.2f}M",
            subtext=f"Avg Ticket: ${kpis['avg_amount']:.2f}",
            delta="Turnover",
            delta_type="good",
            card_type="legit",
        ),
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        render_pbi_kpi(
            label="Fraud-Associated Volume",
            value=f"${kpis['fraud_amount']/1_000_000:.2f}M",
            subtext=f"Share: {kpis['fraud_amount_share']:.2f}% of Spend",
            delta="▲ Exposure",
            delta_type="fraud",
            card_type="warning",
        ),
        unsafe_allow_html=True,
    )

with c5:
    st.markdown(
        render_pbi_kpi(
            label="Mean Legit Ticket",
            value=f"${kpis['avg_legit_amount']:.2f}",
            subtext="Baseline customer spend",
            delta="Normal",
            delta_type="good",
            card_type="neutral",
        ),
        unsafe_allow_html=True,
    )

with c6:
    st.markdown(
        render_pbi_kpi(
            label="Mean Fraud Ticket",
            value=f"${kpis['avg_fraud_amount']:.2f}",
            subtext=f"Disparity: {kpis['amount_fraud_ratio']:.2f}x",
            delta="▲ 7.84x Surge",
            delta_type="fraud",
            card_type="fraud",
        ),
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Row 2: Tableau Multi-Chart Grid (Monthly Trajectory & Category Donut)
col_left_chart, col_right_donut = st.columns([3, 2])

with col_left_chart:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>📅 Monthly Transaction Volume & Fraud Trajectory (2019–2020)</span><span style="font-size:0.75rem; color:#38BDF8;">Dual-Axis Trend</span></div>',
        unsafe_allow_html=True,
    )

    monthly_data = get_monthly_trends(df)

    if not monthly_data.empty:
        fig_monthly = go.Figure()

        # Bar chart for Total Transactions (primary y-axis)
        fig_monthly.add_trace(
            go.Bar(
                x=monthly_data["year_month"],
                y=monthly_data["total_transactions"],
                name="Total Transactions",
                marker_color="rgba(14, 165, 233, 0.25)",
                marker_line=dict(color="#0284C7", width=1),
            )
        )

        # Line chart for Fraud Incidents (secondary y-axis)
        fig_monthly.add_trace(
            go.Scatter(
                x=monthly_data["year_month"],
                y=monthly_data["fraud_transactions"],
                name="Fraud Cases",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="#EF4444", width=3),
                marker=dict(size=6, color="#EF4444"),
            )
        )

        fig_monthly.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=25),
            height=300,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, tickangle=-35),
            yaxis=dict(title="Transaction Volume", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis2=dict(
                title=dict(text="Fraud Cases", font=dict(color="#EF4444")),
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(color="#EF4444"),
            ),
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("No records match the active slicers.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right_donut:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>🏷️ Fraud Incidents by Category</span><span style="font-size:0.75rem; color:#94A3B8;">Volume Share</span></div>',
        unsafe_allow_html=True,
    )

    cat_df = get_category_metrics(df).head(6)

    if not cat_df.empty:
        fig_donut = px.pie(
            cat_df,
            names="category",
            values="fraud_transactions",
            hole=0.62,
            color_discrete_sequence=["#EF4444", "#F59E0B", "#0EA5E9", "#10B981", "#8B5CF6", "#EC4899"],
        )
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            showlegend=True,
            legend=dict(orientation="v", font=dict(size=10), x=1.0, y=0.5),
            annotations=[
                dict(
                    text=f"<b style='font-size:18px; color:#FFFFFF;'>{kpis['fraud_transactions']:,}</b><br><span style='font-size:10px; color:#94A3B8;'>Fraud Cases</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )
            ],
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 3: Diurnal Pattern & Day-of-Week Breakdown
col_hour_chart, col_week_chart = st.columns(2)

with col_hour_chart:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>⏰ Diurnal Attack Intensity (Hour 00:00 to 23:00)</span><span style="font-size:0.75rem; color:#EF4444;">Hour 22 Peak (2.60%)</span></div>',
        unsafe_allow_html=True,
    )

    hourly_df = get_hourly_trends(df)

    if not hourly_df.empty:
        fig_hour = go.Figure()

        # Add shaded risk area for 22:00 to 03:00 window
        fig_hour.add_vrect(
            x0=21.5,
            x1=23.5,
            fillcolor="rgba(239, 68, 68, 0.15)",
            layer="below",
            line_width=0,
            annotation_text="High Risk Window",
            annotation_position="top left",
        )
        fig_hour.add_vrect(
            x0=-0.5,
            x1=3.5,
            fillcolor="rgba(239, 68, 68, 0.15)",
            layer="below",
            line_width=0,
        )

        fig_hour.add_trace(
            go.Scatter(
                x=hourly_df["hour"],
                y=hourly_df["fraud_rate"],
                mode="lines+markers",
                name="Fraud Rate (%)",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=6, color="#0EA5E9"),
                fill="tozeroy",
                fillcolor="rgba(14, 165, 233, 0.1)",
            )
        )

        fig_hour.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=25),
            height=260,
            xaxis=dict(title="Hour of Day (0 to 23)", dtick=2, showgrid=False),
            yaxis=dict(title="Fraud Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_week_chart:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>🗓️ Weekly Transaction Distribution (Monday to Sunday)</span><span style="font-size:0.75rem; color:#94A3B8;">Day of Week</span></div>',
        unsafe_allow_html=True,
    )

    weekday_df = get_weekday_trends(df)

    if not weekday_df.empty:
        fig_week = px.bar(
            weekday_df,
            x="day_name",
            y="fraud_rate",
            color="fraud_transactions",
            color_continuous_scale="Reds",
            labels={"day_name": "Day", "fraud_rate": "Fraud Rate (%)", "fraud_transactions": "Fraud Cases"},
        )
        fig_week.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=25),
            height=260,
            coloraxis_showscale=False,
            xaxis=dict(title=None, showgrid=False),
            yaxis=dict(title="Fraud Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig_week, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 4: Top Merchants & Triage Ledger (Tableau Grid)
col_merch, col_triage_table = st.columns([2, 3])

with col_merch:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>🏪 Top 8 Merchants by Fraud Incident Volume</span><span style="font-size:0.75rem; color:#F59E0B;">Exposure</span></div>',
        unsafe_allow_html=True,
    )

    merch_df = get_merchant_metrics(df, top_n=8)

    if not merch_df.empty:
        fig_merch = px.bar(
            merch_df.sort_values("fraud_transactions", ascending=True),
            x="fraud_transactions",
            y="clean_merchant" if "clean_merchant" in merch_df.columns else "merchant",
            orientation="h",
            color="fraud_rate",
            color_continuous_scale="Reds",
            labels={"clean_merchant": "Merchant", "fraud_transactions": "Fraud Cases", "fraud_rate": "Rate (%)"},
        )
        fig_merch.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=25),
            height=300,
            coloraxis_showscale=False,
            xaxis=dict(title="Fraud Incident Count", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title=None, showgrid=False),
        )
        st.plotly_chart(fig_merch, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_triage_table:
    st.markdown('<div class="tableau-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="tableau-card-title"><span>🛡️ Priority Forensic Triage Ledger (Sample of Flagged Anomalies)</span><span style="font-size:0.75rem; color:#38BDF8;">Risk Scanner</span></div>',
        unsafe_allow_html=True,
    )

    # Heuristic rules evaluation on active sample
    sample_eval = df.head(5000)
    flagged_triage = evaluate_investigation_rules(sample_eval, amount_threshold=300.0, distance_threshold=80.0)
    priority_records = flagged_triage[flagged_triage["risk_score"] >= 2].head(7)

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
            "risk_score": "Flags",
            "risk_level": "Risk Tier",
            "is_fraud": "Ground Truth",
        }).style.format({
            "Amount ($)": "${:.2f}",
            "Dist (km)": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 5: Executive Policy Directives derived strictly from Dataset Analytics
st.markdown("### 💡 Data-Driven Executive Policy Directives")

col_d1, col_d2, col_d3, col_d4 = st.columns(4)

with col_d1:
    st.markdown(
        """
        <div class="directive-card critical">
            <div class="directive-title">1. E-Commerce Vulnerability</div>
            <div class="directive-text">
                <code>shopping_net</code> exhibits the highest fraud rate (<b>1.593%</b>), triple the baseline (0.521%). 
                <code>grocery_pos</code> leads in volume with <b>2,228 cases</b>. Mandate 3DS OTP on online carts > $250.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_d2:
    st.markdown(
        """
        <div class="directive-card warning">
            <div class="directive-title">2. Diurnal Attack Surge</div>
            <div class="directive-text">
                Attacks surge during nocturnal hours. At <b>22:00 (10:00 PM)</b>, fraud prevalence spikes to <b>2.601%</b> (5x daytime baseline), 
                accounting for 2,481 confirmed cases. Tighten risk scoring thresholds between 22:00 and 04:00.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_d3:
    st.markdown(
        """
        <div class="directive-card">
            <div class="directive-title">3. Value Disparity Multiplier</div>
            <div class="directive-text">
                Fraudulent tickets average <b>$530.66</b> vs <b>$67.65</b> for legitimate purchases (<b>7.84x disparity</b>). 
                While fraud accounts for only 0.52% of transaction count, it captures <b>3.95% of gross dollar volume</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_d4:
    st.markdown(
        """
        <div class="directive-card success">
            <div class="directive-title">4. Geographic Clustering</div>
            <div class="directive-text">
                New York leads nationwide in raw incident volume (<b>730 cases</b>). Among major states with >= 5,000 transactions, 
                Oregon exhibits an elevated rate of <b>0.746%</b>. Deploy localized geo-fencing on sudden merchant displacements.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
