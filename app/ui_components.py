"""
UI components, design system, theme styling, and cached data accessors
for the Financial Fraud Analytics Streamlit Dashboard.
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
from typing import Tuple, Optional
from src.load_data import load_processed_data
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

# Custom CSS for executive glassmorphic financial theme
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0B1120 0%, #050811 100%);
        color: #F8FAFC;
    }

    /* Executive Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(14, 165, 233, 0.25);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        font-weight: 400;
        max-width: 900px;
        line-height: 1.5;
    }

    /* KPI Metric Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(8px);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.4), 0 0 15px rgba(56, 189, 248, 0.15);
    }
    .kpi-card.fraud {
        border-left: 4px solid #EF4444;
    }
    .kpi-card.legit {
        border-left: 4px solid #10B981;
    }
    .kpi-card.neutral {
        border-left: 4px solid #38BDF8;
    }
    .kpi-card.warning {
        border-left: 4px solid #F59E0B;
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Badges & Chips */
    .chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .chip-fraud {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .chip-legit {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .chip-neutral {
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Plotly Chart Card Wrapper */
    .chart-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #090E17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Dataframe tweaks */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
"""


def apply_theme():
    """Injects high-end financial styling into the active Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading financial transaction database...", ttl=3600)
def get_dataset(use_sample: bool = False) -> pd.DataFrame:
    """Cached loader for the processed Parquet dataset."""
    return load_processed_data(sample=use_sample)


def render_hero(title: str, subtitle: str, badge_text: str = "PRODUCTION ANALYTICS"):
    """Renders the executive hero banner."""
    st.markdown(
        f"""
        <div class="hero-container">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="chip chip-neutral">{badge_text}</span>
                <span style="color: #64748B; font-size: 0.82rem;">1,852,394 Total Historical Transactions</span>
            </div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    subtext: str = "",
    status: str = "neutral",
    icon: str = "📊",
):
    """Generates an HTML snippet for a stylized metric card."""
    return f"""
    <div class="kpi-card {status}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="kpi-label">{label}</div>
            <span style="font-size: 1.1rem;">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders global interactive sidebar filters and returns the filtered dataframe.
    """
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #38BDF8; letter-spacing: -0.01em;">
                🛡️ Fraud Analytics
            </div>
            <div style="font-size: 0.78rem; color: #64748B;">Interactive Investigation Slicers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Dataset Partition (Train / Test / All)
    sources = ["All Historical Sources"] + sorted(list(df["source_dataset"].unique()))
    selected_source = st.sidebar.selectbox("Data Partition", sources, index=0)

    # 2. Date Range Filter
    min_date = df["trans_date_trans_time"].min().date()
    max_date = df["trans_date_trans_time"].max().date()

    date_range = st.sidebar.date_input(
        "Transaction Date Window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # 3. Category Multi-select
    all_categories = sorted(list(df["category"].dropna().unique()))
    selected_categories = st.sidebar.multiselect(
        "Merchant Category",
        options=all_categories,
        default=[],
        placeholder="All Categories (Default)",
    )

    # 4. State Filter
    all_states = ["All States"] + sorted(list(df["state"].dropna().unique()))
    selected_state = st.sidebar.selectbox("State / Region", all_states, index=0)

    # 5. Fraud Status Filter
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
            <b>Active Selection:</b><br>
            <span style="color: #38BDF8; font-family: 'JetBrains Mono', monospace; font-weight: 600;">
                {len(filtered_df):,}
            </span> / {len(df):,} ({filter_pct:.1f}%)
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df
