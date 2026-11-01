"""
Financial Fraud Detection & Analytics Dashboard
Home Page - Recreated to faithfully mirror the Docynx Orders & Frauds Analytics Dashboard (Image 3).
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
    get_merchant_metrics,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_docynx_header,
    render_docynx_kpi,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Docynx | Orders & Frauds Analytics Dashboards",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# Load primary processed dataset
df_raw = get_dataset()

# Render global sidebar filters
df = render_sidebar_filters(df_raw)

# Calculate KPIs
kpis = calculate_kpis(df)

# Top Docynx Brand Header (Image 3 Style)
render_docynx_header(
    title="Orders & Frauds Analytics Dashboards",
    subtitle="Enterprise Transaction Surveillance & Autonomous Fraud Risk Auditing",
)

# Row 1: Top 7 KPI Cards (Image 3 Style)
st.markdown('<div class="kpi-row-7">', unsafe_allow_html=True)

# Helper for formatted numbers (e.g. 1.85M, 9.65K)
def fmt_num(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.2f}K"
    return f"{n}"

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    st.markdown(
        render_docynx_kpi(
            label="Total Orders",
            value=fmt_num(kpis["total_transactions"]),
            delta="↑ 108.7% vs Apr 2026",
            icon="🛍️",
            icon_bg="#EC4899",
            delta_dir="up",
        ),
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        render_docynx_kpi(
            label="Completed Orders",
            value=fmt_num(kpis["legitimate_transactions"]),
            delta="↑ 108.0% vs Apr 2026",
            icon="✅",
            icon_bg="#22C55E",
            delta_dir="up",
        ),
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        render_docynx_kpi(
            label="Cancelled Orders",
            value=fmt_num(kpis["fraud_transactions"]),
            delta="↑ 109.5% vs Apr 2026",
            icon="❌",
            icon_bg="#EF4444",
            delta_dir="down",
        ),
        unsafe_allow_html=True,
    )

with c4:
    # High risk review volume (heuristic proxy)
    review_vol = int(kpis["fraud_transactions"] * 1.58)
    st.markdown(
        render_docynx_kpi(
            label="Return Requests",
            value=fmt_num(review_vol),
            delta="↑ 108.7% vs Apr 2026",
            icon="📋",
            icon_bg="#F59E0B",
            delta_dir="up",
        ),
        unsafe_allow_html=True,
    )

with c5:
    st.markdown(
        render_docynx_kpi(
            label="Return Rate",
            value=f"{kpis['fraud_rate']:.2f}%",
            delta="↑ 0.02% vs Apr 2026",
            icon="🛡️",
            icon_bg="#38BDF8",
            delta_dir="up",
        ),
        unsafe_allow_html=True,
    )

with c6:
    st.markdown(
        render_docynx_kpi(
            label="Total GMV",
            value=f"${kpis['total_amount']/1_000_000:.2f}M",
            delta="↑ 109.1% vs Apr 2026",
            icon="💲",
            icon_bg="#3B82F6",
            delta_dir="up",
        ),
        unsafe_allow_html=True,
    )

with c7:
    st.markdown(
        render_docynx_kpi(
            label="Total Refunds",
            value=f"${kpis['fraud_amount']/1_000_000:.2f}M",
            delta="↑ 109.4% vs Apr 2026",
            icon="💸",
            icon_bg="#F43F5E",
            delta_dir="down",
        ),
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Row 2: Middle Charts & Donut Ring Visuals (Image 3 Style)
col_trend, col_reasons1, col_reasons2 = st.columns([2.2, 1.4, 1.4])

with col_trend:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title"><span>Orders Trend Overview</span><span style="font-size:0.75rem; color:#94A3B8;">order_date</span></div>', unsafe_allow_html=True)
    
    monthly_data = get_monthly_trends(df)
    fig_orders = go.Figure()

    # Base line with cyan/blue gradient
    fig_orders.add_trace(
        go.Scatter(
            x=monthly_data["year_month"],
            y=monthly_data["total_transactions"],
            mode="lines",
            line=dict(color="#00D2FF", width=2.5, shape="spline"),
            name="Orders Volume",
        )
    )
    # Fraud spikes in neon red/magenta
    fig_orders.add_trace(
        go.Scatter(
            x=monthly_data["year_month"],
            y=monthly_data["fraud_transactions"] * 10,  # Scaled for visual prominence
            mode="lines+markers",
            line=dict(color="#D946EF", width=2),
            marker=dict(size=5, color="#EF4444"),
            name="Fraud Anomaly (x10)",
        )
    )
    fig_orders.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=25),
        height=220,
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig_orders, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_reasons1:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">Cancellation Reasons</div>', unsafe_allow_html=True)
    
    # Category-based cancellation proxy
    cat_df = get_category_metrics(df).head(4)
    total_reasons = int(cat_df["fraud_transactions"].sum())

    fig_donut1 = px.pie(
        cat_df,
        names="category",
        values="fraud_transactions",
        hole=0.65,
        color_discrete_sequence=["#F97316", "#06B6D4", "#EC4899", "#8B5CF6"],
    )
    fig_donut1.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=9), x=1.0, y=0.5),
        annotations=[
            dict(
                text=f"<b style='font-size:16px; color:#FFFFFF;'>{fmt_num(total_reasons)}</b><br><span style='font-size:10px; color:#94A3B8;'>Total</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    fig_donut1.update_traces(textposition="inside", textinfo="none")
    st.plotly_chart(fig_donut1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_reasons2:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">Return Reasons</div>', unsafe_allow_html=True)
    
    # Return reasons breakdown
    return_reasons = pd.DataFrame([
        {"Reason": "Quality Issue", "Count": 274},
        {"Reason": "Not as described", "Count": 264},
        {"Reason": "Changed my mind", "Count": 240},
        {"Reason": "Damaged product", "Count": 230},
        {"Reason": "Size/Fit Issue", "Count": 240},
    ])
    total_returns = int(return_reasons["Count"].sum())

    fig_donut2 = px.pie(
        return_reasons,
        names="Reason",
        values="Count",
        hole=0.65,
        color_discrete_sequence=["#D946EF", "#3B82F6", "#06B6D4", "#F59E0B", "#EF4444"],
    )
    fig_donut2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=9), x=1.0, y=0.5),
        annotations=[
            dict(
                text=f"<b style='font-size:16px; color:#FFFFFF;'>1.248K</b><br><span style='font-size:10px; color:#94A3B8;'>Total</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    fig_donut2.update_traces(textposition="inside", textinfo="none")
    st.plotly_chart(fig_donut2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Row 3: Payment Overview & Table High Risk Customers (Image 3 Style)
st.markdown("<br>", unsafe_allow_html=True)
col_pay_wrap, col_risk_tbl = st.columns([2.0, 3.0])

with col_pay_wrap:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">Payment Overview</div>', unsafe_allow_html=True)
    
    # 5-Item Payment Grid matching Image 3
    st.markdown(
        f"""
        <div class="payment-overview-row">
            <div class="payment-mini-item">
                <div style="font-size: 1.2rem;">👛</div>
                <div class="payment-mini-label">Total Payments</div>
                <div class="payment-mini-val">${kpis['total_amount']/1_000_000:.2f}M</div>
            </div>
            <div class="payment-mini-item">
                <div style="font-size: 1.2rem;">💵</div>
                <div class="payment-mini-label">COD Orders</div>
                <div class="payment-mini-val">1.808K</div>
            </div>
            <div class="payment-mini-item">
                <div style="font-size: 1.2rem;">💳</div>
                <div class="payment-mini-label">Online Orders</div>
                <div class="payment-mini-val">1.872K</div>
            </div>
            <div class="payment-mini-item">
                <div style="font-size: 1.2rem;">⚠️</div>
                <div class="payment-mini-label">Payment Failures</div>
                <div class="payment-mini-val">314</div>
            </div>
            <div class="payment-mini-item">
                <div style="font-size: 1.2rem;">💸</div>
                <div class="payment-mini-label">Refunds Processed</div>
                <div class="payment-mini-val">1.248K</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Repeat Return Customers mini table matching Image 3 Left Box
    st.markdown('<div class="box-title">Repeat Return Customers (Returned 2 or more times)</div>', unsafe_allow_html=True)
    repeat_df = pd.DataFrame([
        {"customer_id": "CUST10157", "Total Orders": 28, "Return Requests": 14, "Return Rate": "50.00%", "Times Returned": 14, "Refund Amount": "$5,077.50"},
        {"customer_id": "CUST10029", "Total Orders": 16, "Return Requests": 12, "Return Rate": "75.00%", "Times Returned": 12, "Refund Amount": "$4,623.00"},
        {"customer_id": "CUST10049", "Total Orders": 20, "Return Requests": 14, "Return Rate": "70.00%", "Times Returned": 14, "Refund Amount": "$4,527.20"},
    ])
    st.dataframe(repeat_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_risk_tbl:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title"><span>Table High Risk Customers (Potential Frauds)</span><span style="font-size:0.75rem; color:#A855F7;">Audited Records</span></div>', unsafe_allow_html=True)
    
    # High Risk Customers Table exactly formatted like Image 3
    high_risk_data = pd.DataFrame([
        {"customer_id": "CUST10000", "Total Orders": 2, "Trend Return Requests": 0, "Return Rate": "0.00%", "Sum of refund_amount": 0, "Sum of fraud_score": 186, "Risk Level": "High"},
        {"customer_id": "CUST10000", "Total Orders": 8, "Trend Return Requests": 6, "Return Rate": "75.00%", "Sum of refund_amount": 18678, "Sum of fraud_score": 410, "Risk Level": "Low"},
        {"customer_id": "CUST10000", "Total Orders": 6, "Trend Return Requests": 2, "Return Rate": "33.33%", "Sum of refund_amount": 5884, "Sum of fraud_score": 462, "Risk Level": "Medium"},
        {"customer_id": "CUST10000", "Total Orders": 4, "Trend Return Requests": 0, "Return Rate": "0.00%", "Sum of refund_amount": 0, "Sum of fraud_score": 76, "Risk Level": "Safe"},
        {"customer_id": "CUST10001", "Total Orders": 2, "Trend Return Requests": 2, "Return Rate": "100.00%", "Sum of refund_amount": 4726, "Sum of fraud_score": 172, "Risk Level": "High"},
        {"customer_id": "CUST10001", "Total Orders": 6, "Trend Return Requests": 0, "Return Rate": "0.00%", "Sum of refund_amount": 0, "Sum of fraud_score": 276, "Risk Level": "Low"},
        {"customer_id": "CUST10001", "Total Orders": 4, "Trend Return Requests": 2, "Return Rate": "50.00%", "Sum of refund_amount": 3750, "Sum of fraud_score": 326, "Risk Level": "Medium"},
    ])
    
    st.dataframe(
        high_risk_data.style.applymap(
            lambda val: "background-color: #EF4444; color: white; font-weight: bold;" if val == "High"
            else ("background-color: #F59E0B; color: white; font-weight: bold;" if val == "Medium"
            else ("background-color: #84CC16; color: black; font-weight: bold;" if val == "Low"
            else ("background-color: #06B6D4; color: black; font-weight: bold;" if val == "Safe" else ""))),
            subset=["Risk Level"],
        ),
        use_container_width=True,
        hide_index=True,
    )
    
    # Totals Row footer matching Image 3 table footer
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; padding:8px 14px; background:#0A0E1C; border-radius:6px; font-size:0.8rem; font-weight:700; color:#F8FAFC; margin-top:8px;">
            <span>Total</span>
            <span>Orders: 3680</span>
            <span>Returns: 1248 (33.91%)</span>
            <span>Refunds: $3,320,442</span>
            <span>Risk Score: 202,750</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Row 4: Fraud Score Distribution & Fraud Score Trend (Image 3 Style)
st.markdown("<br>", unsafe_allow_html=True)
col_fs_donut, col_fs_trend = st.columns([1.5, 2.5])

with col_fs_donut:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title">Fraud Score Distribution</div>', unsafe_allow_html=True)
    
    score_dist = pd.DataFrame([
        {"Tier": "High", "Count": 1250},
        {"Tier": "Medium", "Count": 1240},
        {"Tier": "Low", "Count": 1200},
    ])
    fig_score_donut = px.pie(
        score_dist,
        names="Tier",
        values="Count",
        hole=0.65,
        color="Tier",
        color_discrete_map={"High": "#00D2FF", "Medium": "#1E40AF", "Low": "#F97316"},
    )
    fig_score_donut.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=9), x=1.0, y=0.5),
        annotations=[
            dict(
                text=f"<b style='font-size:16px; color:#FFFFFF;'>251</b><br><span style='font-size:10px; color:#94A3B8;'>Customers</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    fig_score_donut.update_traces(textposition="inside", textinfo="none")
    st.plotly_chart(fig_score_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_fs_trend:
    st.markdown('<div class="docynx-box">', unsafe_allow_html=True)
    st.markdown('<div class="box-title"><span>Fraud Score Trend</span><span style="font-size:0.75rem; color:#94A3B8;">Risk Level: High, Medium</span></div>', unsafe_allow_html=True)
    
    # 30-day risk trend simulation matching Image 3 right trend chart
    days = list(range(1, 31))
    trend_high = [1800, 2100, 1950, 2400, 2200, 2100, 2500, 2300, 1900, 2050,
                  2250, 2450, 2150, 1850, 1950, 2600, 2800, 2200, 2100, 2300,
                  2400, 2000, 1850, 2100, 2400, 2300, 2200, 2500, 2100, 2300]
    trend_med = [1500, 1800, 1600, 2000, 1750, 1900, 2100, 1950, 1650, 1800,
                 1950, 2100, 1800, 1600, 1700, 2200, 2400, 1900, 1800, 1950,
                 2000, 1700, 1600, 1800, 2050, 1950, 1850, 2150, 1800, 1950]

    fig_fs_trend = go.Figure()
    fig_fs_trend.add_trace(go.Scatter(x=days, y=trend_high, mode="lines+markers", line=dict(color="#00D2FF", width=2), marker=dict(size=4), name="High"))
    fig_fs_trend.add_trace(go.Scatter(x=days, y=trend_med, mode="lines+markers", line=dict(color="#FBBF24", width=2), marker=dict(size=4), name="Medium"))

    fig_fs_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=25),
        height=220,
        xaxis=dict(title="Day", showgrid=True, gridcolor="rgba(255,255,255,0.05)", dtick=5),
        yaxis=dict(title="Sum of fraud_score", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_fs_trend, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Row 5: Recent Alerts Section (Image 3 Bottom Row - 5 Cards)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Recent Alerts")

col_al1, col_al2, col_al3, col_al4, col_al5 = st.columns(5)

with col_al1:
    st.markdown(
        """
        <div class="docynx-alert-card">
            <div class="docynx-alert-icon">⚠️</div>
            <div>
                <div class="docynx-alert-title">High Return Rate Detected</div>
                <div class="docynx-alert-desc">Customer ID: CUST10250</div>
                <div class="docynx-alert-date">31 May 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_al2:
    st.markdown(
        """
        <div class="docynx-alert-card">
            <div class="docynx-alert-icon">⚠️</div>
            <div>
                <div class="docynx-alert-title">Multiple Returns For Same Product</div>
                <div class="docynx-alert-desc">Product ID: PRD-992</div>
                <div class="docynx-alert-date">31 May 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_al3:
    st.markdown(
        """
        <div class="docynx-alert-card">
            <div class="docynx-alert-icon">⚠️</div>
            <div>
                <div class="docynx-alert-title">High Refund Amount</div>
                <div class="docynx-alert-desc">₹4,999 ($530.66)</div>
                <div class="docynx-alert-date">31 May 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_al4:
    st.markdown(
        """
        <div class="docynx-alert-card">
            <div class="docynx-alert-icon">⚠️</div>
            <div>
                <div class="docynx-alert-title">COD Order Pattern</div>
                <div class="docynx-alert-desc">Suspicious Velocity: CUST10250</div>
                <div class="docynx-alert-date">31 May 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_al5:
    st.markdown(
        """
        <div class="docynx-alert-card">
            <div class="docynx-alert-icon">⚠️</div>
            <div>
                <div class="docynx-alert-title">Potential Fraud Detected</div>
                <div class="docynx-alert-desc">Fraud Score: 100 (Critical)</div>
                <div class="docynx-alert-date">31 May 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
