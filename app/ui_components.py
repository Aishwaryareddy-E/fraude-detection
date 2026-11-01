"""
UI components, design system, theme styling, and cached data accessors
for the Financial Fraud Analytics Streamlit Dashboard.
Implements the futuristic Command-Center aesthetic seen in advanced cyber forensic centers.
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

# Custom CSS for executive glassmorphic financial command-center theme
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography & Deep Dark Cyber Grid */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0B1120 0%, #050811 100%);
        color: #F8FAFC;
    }

    /* Executive Command Header */
    .command-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 19, 43, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 24px;
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-left {
        max-width: 800px;
    }
    .command-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .command-subtitle {
        color: #94A3B8;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .pulse-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.25);
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background: #EF4444;
        border-radius: 50%;
        box-shadow: 0 0 8px #EF4444;
        animation: pulseAnimation 1.8s infinite;
    }
    @keyframes pulseAnimation {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }

    /* KPI Metric Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        backdrop-filter: blur(10px);
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.5), 0 0 16px rgba(56, 189, 248, 0.15);
    }
    .kpi-card.fraud { border-left: 4px solid #EF4444; }
    .kpi-card.legit { border-left: 4px solid #10B981; }
    .kpi-card.neutral { border-left: 4px solid #38BDF8; }
    .kpi-card.warning { border-left: 4px solid #F59E0B; }
    .kpi-card.purple { border-left: 4px solid #A855F7; }

    .kpi-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .kpi-delta {
        font-size: 0.76rem;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .delta-up { color: #EF4444; }
    .delta-down { color: #10B981; }
    .delta-neutral { color: #38BDF8; }

    /* Concentric Ring Gauge Cards (Image 1 Style) */
    .gauge-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
        transition: border-color 0.2s ease;
    }
    .gauge-card:hover {
        border-color: rgba(56, 189, 248, 0.35);
    }
    .gauge-circle {
        position: relative;
        width: 68px;
        height: 68px;
        flex-shrink: 0;
    }
    .gauge-info {
        flex-grow: 1;
    }
    .gauge-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 2px;
    }
    .gauge-desc {
        font-size: 0.76rem;
        color: #94A3B8;
    }

    /* Live Incident Alerts Grid (Image 3 Style) */
    .alert-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 14px;
        margin-top: 14px;
        margin-bottom: 24px;
    }
    .alert-card {
        background: rgba(239, 68, 68, 0.07);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 12px;
        padding: 14px 16px;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .alert-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.5);
    }
    .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .alert-type {
        font-size: 0.74rem;
        font-weight: 700;
        color: #EF4444;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .alert-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
        color: #F8FAFC;
    }
    .alert-details {
        font-size: 0.78rem;
        color: #CBD5E1;
        margin-top: 4px;
        line-height: 1.4;
    }

    /* Badges & Chips */
    .chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .chip-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .chip-elevated {
        background: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .chip-safe {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .chip-neutral {
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #080D1A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
"""


def apply_theme():
    """Injects high-end financial styling into the active Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading primary transaction database...", ttl=3600)
def get_dataset(use_sample: bool = False) -> pd.DataFrame:
    """Cached loader for the primary processed Parquet dataset."""
    return load_processed_data(sample=use_sample)


@st.cache_data(show_spinner="Loading credit card comparative database...", ttl=3600)
def get_creditcard_dataset() -> pd.DataFrame:
    """Cached loader for the European Credit Card dataset."""
    return load_creditcard_data()


def render_hero(title: str, subtitle: str, badge_text: str = "COMMAND CENTER", pulse_alert: Optional[str] = None):
    """Renders the executive command center hero header."""
    pulse_html = ""
    if pulse_alert:
        pulse_html = f"""
        <div class="pulse-badge">
            <div class="pulse-dot"></div>
            <span>{pulse_alert}</span>
        </div>
        """

    st.markdown(
        f"""
        <div class="command-header">
            <div class="header-left">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span class="chip chip-neutral">{badge_text}</span>
                    <span style="color: #64748B; font-size: 0.8rem;">1,852,394 Primary Records + 284,807 European Records</span>
                </div>
                <div class="command-title">{title}</div>
                <div class="command-subtitle">{subtitle}</div>
            </div>
            <div>
                {pulse_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    subtext: str = "",
    status: str = "neutral",
    delta: str = "",
    delta_type: str = "neutral",
):
    """Generates an HTML snippet for a stylized metric card with delta indicator."""
    delta_class = f"delta-{delta_type}"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card {status}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div style="font-size: 0.78rem; color: #64748B; margin-top: 4px;">{subtext}</div>
        {delta_html}
    </div>
    """


def render_circular_gauge(label: str, percentage: float, color: str = "#38BDF8", subtext: str = "", value_override: str = ""):
    """
    Renders an SVG concentric circular progress gauge matching Image 1.
    """
    circumference = 2 * 3.14159 * 26
    dasharray = f"{(percentage / 100) * circumference} {circumference}"
    val_text = value_override if value_override else f"{percentage:.1f}%"
    return f"""
    <div class="gauge-card">
        <div class="gauge-circle">
            <svg viewBox="0 0 68 68" width="68" height="68">
                <circle cx="34" cy="34" r="26" fill="transparent" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
                <circle cx="34" cy="34" r="26" fill="transparent" stroke="{color}" stroke-width="6"
                        stroke-dasharray="{dasharray}" stroke-linecap="round"
                        transform="rotate(-90 34 34)" style="filter: drop-shadow(0 0 6px {color});"/>
                <text x="34" y="38" text-anchor="middle" fill="#F8FAFC" font-size="12" font-weight="700" font-family="'JetBrains Mono', monospace">{val_text}</text>
            </svg>
        </div>
        <div class="gauge-info">
            <div class="gauge-title">{label}</div>
            <div class="gauge-desc">{subtext}</div>
        </div>
    </div>
    """


def render_alert_card(alert_type: str, entity_id: str, details: str, time_str: str = "Real-Time"):
    """
    Renders a live incident alert card matching Image 3 bottom row.
    """
    return f"""
    <div class="alert-card">
        <div class="alert-header">
            <span class="alert-type">⚠️ {alert_type}</span>
            <span style="font-size: 0.72rem; color: #64748B;">{time_str}</span>
        </div>
        <div class="alert-id">{entity_id}</div>
        <div class="alert-details">{details}</div>
    </div>
    """


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders global interactive sidebar filters and returns the filtered dataframe.
    """
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #38BDF8; letter-spacing: -0.01em;">
                🛡️ Fraud Intelligence
            </div>
            <div style="font-size: 0.78rem; color: #64748B;">Multi-Tier Forensic Slicers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Dataset Partition
    sources = ["All Historical Sources"] + sorted(list(df["source_dataset"].unique()))
    selected_source = st.sidebar.selectbox("Data Source", sources, index=0)

    # 2. Date Range Filter
    min_date = df["trans_date_trans_time"].min().date()
    max_date = df["trans_date_trans_time"].max().date()

    date_range = st.sidebar.date_input(
        "Date Window",
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
    selected_state = st.sidebar.selectbox("Jurisdiction", all_states, index=0)

    # 5. Fraud Status Filter
    fraud_filter = st.sidebar.radio(
        "Classification",
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

    filter_pct = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0.0
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.8rem; color: #94A3B8;">
            <b>Active Ledger Window:</b><br>
            <span style="color: #38BDF8; font-family: 'JetBrains Mono', monospace; font-weight: 600;">
                {len(filtered_df):,}
            </span> / {len(df):,} ({filter_pct:.1f}%)
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df
