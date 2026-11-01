"""
UI components, design system, theme styling, and cached data accessors
for the Financial Fraud Analytics Dashboard.
Implements a clean, high-performance Tableau / Power BI Dark Theme with crisp card containers,
synchronized filter slicers, and 100% data-driven metrics.
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
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from src.load_data import load_processed_data, load_creditcard_data
from src.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_BG_DARK,
    COLOR_CARD_DARK,
    COLOR_TEXT_LIGHT,
    COLOR_MUTED,
)

# Power BI / Tableau Enterprise Dark Theme CSS
POWERBI_TABLEAU_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    /* Global Typography & Power BI Dark Canvas */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0B1120 !important;
        background-image: 
            radial-gradient(at 10% 10%, rgba(30, 58, 138, 0.15) 0px, transparent 40%),
            radial-gradient(at 90% 90%, rgba(14, 165, 233, 0.10) 0px, transparent 40%) !important;
        color: #F8FAFC;
    }

    /* Power BI Executive Header Banner */
    .pbi-header {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .pbi-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .pbi-header-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    .pbi-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .pbi-subtitle {
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 2px;
    }
    .pbi-badge {
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid rgba(14, 165, 233, 0.35);
        color: #38BDF8;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    /* Power BI / Tableau KPI Metric Card Grid */
    .pbi-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    .pbi-kpi-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 14px 16px;
        position: relative;
        transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .pbi-kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }
    .pbi-kpi-card.fraud {
        border-top: 3px solid #EF4444;
    }
    .pbi-kpi-card.legit {
        border-top: 3px solid #10B981;
    }
    .pbi-kpi-card.neutral {
        border-top: 3px solid #0EA5E9;
    }
    .pbi-kpi-card.warning {
        border-top: 3px solid #F59E0B;
    }
    .pbi-kpi-card.purple {
        border-top: 3px solid #8B5CF6;
    }

    .pbi-kpi-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .pbi-kpi-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .pbi-kpi-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 6px;
        font-size: 0.74rem;
        color: #64748B;
    }
    .pbi-delta {
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.70rem;
    }
    .pbi-delta.up-fraud {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
    }
    .pbi-delta.up-good {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
    }
    .pbi-delta.neutral {
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
    }

    /* Tableau Chart Containers */
    .tableau-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 16px;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .tableau-card-title {
        font-size: 0.90rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 8px;
    }

    /* Executive Policy Directives Cards */
    .directive-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 14px 16px;
        border-left: 4px solid #0EA5E9;
    }
    .directive-card.critical {
        border-left-color: #EF4444;
    }
    .directive-card.warning {
        border-left-color: #F59E0B;
    }
    .directive-card.success {
        border-left-color: #10B981;
    }
    .directive-title {
        font-size: 0.84rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .directive-text {
        font-size: 0.78rem;
        color: #CBD5E1;
        line-height: 1.45;
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .sidebar-slicer-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 14px;
    }
</style>
"""


def apply_theme():
    """Injects Power BI / Tableau styling into the active Streamlit page."""
    st.markdown(POWERBI_TABLEAU_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading primary transaction dataset...", ttl=3600)
def get_dataset(use_sample: bool = False) -> pd.DataFrame:
    """Cached loader for the primary processed Parquet dataset."""
    return load_processed_data(sample=use_sample)


@st.cache_data(show_spinner="Loading European creditcard dataset...", ttl=3600)
def get_creditcard_dataset() -> pd.DataFrame:
    """Cached loader for the European Credit Card dataset."""
    return load_creditcard_data()


def render_powerbi_header(title: str, subtitle: str, badge: str = "POWER BI ANALYTICS"):
    """
    Renders an executive Power BI / Tableau Header Banner.
    """
    st.markdown(
        f"""
        <div class="pbi-header">
            <div class="pbi-header-left">
                <div class="pbi-header-icon">📊</div>
                <div>
                    <div class="pbi-title">{title}</div>
                    <div class="pbi-subtitle">{subtitle}</div>
                </div>
            </div>
            <div>
                <span class="pbi-badge">{badge}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, badge_text: str = "POWER BI ANALYTICS", pulse_alert: Optional[str] = None):
    """Alias for render_powerbi_header for backward compatibility."""
    return render_powerbi_header(title, subtitle, badge=badge_text)


def render_pbi_kpi(
    label: str,
    value: str,
    subtext: str = "",
    delta: str = "",
    delta_type: str = "neutral",
    card_type: str = "neutral",
):
    """
    Generates a Power BI styled KPI card with top color strip and delta badge.
    """
    delta_class = f"up-fraud" if delta_type == "fraud" else ("up-good" if delta_type == "good" else "neutral")
    delta_html = f'<span class="pbi-delta {delta_class}">{delta}</span>' if delta else ""
    return f"""
    <div class="pbi-kpi-card {card_type}">
        <div class="pbi-kpi-label">{label}</div>
        <div class="pbi-kpi-value">{value}</div>
        <div class="pbi-kpi-footer">
            <span>{subtext}</span>
            {delta_html}
        </div>
    </div>
    """


def render_kpi_card(
    label: str,
    value: str,
    subtext: str = "",
    status: str = "neutral",
    delta: str = "",
    delta_type: str = "neutral",
    icon: str = "📊",
):
    """Alias for render_pbi_kpi for backward compatibility."""
    return render_pbi_kpi(label, value, subtext, delta=delta, delta_type=delta_type, card_type=status)


def render_circular_gauge(
    label: str,
    percentage: float,
    color: str = "#38BDF8",
    subtext: str = "",
    value_override: str = "",
):
    """Clean Power BI / Tableau style metric gauge card."""
    val_text = value_override if value_override else f"{percentage:.1f}%"
    return f"""
    <div style="background:#1E293B; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:12px 14px; margin-bottom:10px;">
        <div style="font-size:0.72rem; color:#94A3B8; text-transform:uppercase; font-weight:700; letter-spacing:0.05em;">{label}</div>
        <div style="font-size:1.35rem; font-weight:700; color:{color}; font-family:'JetBrains Mono', monospace; margin:2px 0;">{val_text}</div>
        <div style="font-size:0.72rem; color:#64748B;">{subtext}</div>
    </div>
    """


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders standard Power BI slicers in the sidebar with live interactive filtering.
    """
    st.sidebar.markdown(
        """
        <div class="sidebar-slicer-title">
            <span>⚙️</span> Interactive Slicers
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Dataset Partition Slicer
    sources = ["All Historical Sources"] + sorted(list(df["source_dataset"].unique()))
    selected_source = st.sidebar.selectbox("Data Partition Slicer", sources, index=0)

    # 2. Date Range Slicer
    min_date = df["trans_date_trans_time"].min().date()
    max_date = df["trans_date_trans_time"].max().date()

    date_range = st.sidebar.date_input(
        "Transaction Date Slicer",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # 3. Category Slicer
    all_categories = sorted(list(df["category"].dropna().unique()))
    selected_categories = st.sidebar.multiselect(
        "Merchant Category Slicer",
        options=all_categories,
        default=[],
        placeholder="All Categories (Default)",
    )

    # 4. State Slicer
    all_states = ["All States"] + sorted(list(df["state"].dropna().unique()))
    selected_state = st.sidebar.selectbox("Jurisdiction / State Slicer", all_states, index=0)

    # 5. Fraud Classification Slicer
    fraud_filter = st.sidebar.radio(
        "Fraud Classification",
        options=["All Transactions", "Fraud Only", "Legitimate Only"],
        index=0,
    )

    # Apply filters
    filtered_df = df

    if selected_source != "All Historical Sources":
        filtered_df = filtered_df[filtered_df["source_dataset"] == selected_source]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = filtered_df[
            (filtered_df["trans_date_trans_time"].dt.date >= start_d)
            & (filtered_df["trans_date_trans_time"].dt.date <= end_d)
        ]

    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

    if selected_state != "All States":
        filtered_df = filtered_df[filtered_df["state"] == selected_state]

    if fraud_filter == "Fraud Only":
        filtered_df = filtered_df[filtered_df["is_fraud"] == 1]
    elif fraud_filter == "Legitimate Only":
        filtered_df = filtered_df[filtered_df["is_fraud"] == 0]

    # Display active filter status in sidebar footer
    filter_pct = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0.0
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.8rem; color: #94A3B8;">
            <b>Active Ledger Slicing:</b><br>
            <span style="color: #38BDF8; font-family: 'JetBrains Mono', monospace; font-weight: 700;">
                {len(filtered_df):,}
            </span> / {len(df):,} ({filter_pct:.1f}%)
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df
