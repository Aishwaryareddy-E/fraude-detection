"""
UI components, design system, theme styling, and cached data accessors
for the Financial Fraud Analytics Streamlit Dashboard.
Faithfully implements the Docynx Orders & Frauds Analytics Dashboards aesthetic (Image 3).
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

# Custom CSS reproducing the Docynx Dark Purple/Navy Dashboard Aesthetic (Image 3)
DOCYNX_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography & Deep Indigo Background */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #070913 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(147, 51, 234, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.10) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.8) 0px, transparent 50%) !important;
        color: #F8FAFC;
    }

    /* Top Docynx App Navigation Bar */
    .docynx-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0B0F1F;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .docynx-brand-wrap {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .docynx-logo {
        font-size: 1.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #D946EF 0%, #A855F7 60%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
    }
    .docynx-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.01em;
    }
    .docynx-subtitle {
        font-size: 0.78rem;
        color: #94A3B8;
    }

    /* Top KPI Row Cards (Image 3 Style) */
    .kpi-row-7 {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    @media (max-width: 1400px) {
        .kpi-row-7 {
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }
    }
    @media (max-width: 900px) {
        .kpi-row-7 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    .docynx-kpi-card {
        background: #0F1528;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 14px;
        position: relative;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .docynx-kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.4);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    }
    .kpi-header-label {
        font-size: 0.74rem;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-val-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .kpi-icon-badge {
        width: 24px;
        height: 24px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
    }
    .kpi-main-val {
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .kpi-growth-delta {
        font-size: 0.68rem;
        font-weight: 600;
        color: #22C55E;
        display: flex;
        align-items: center;
        gap: 3px;
    }
    .kpi-growth-delta.down {
        color: #EF4444;
    }

    /* Container Box Styling */
    .docynx-box {
        background: #0F1528;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
    }
    .box-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Payment Overview Horizontal Mini-cards */
    .payment-overview-row {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
        background: #0A0E1C;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 16px;
    }
    .payment-mini-item {
        text-align: center;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        padding: 0 8px;
    }
    .payment-mini-item:last-child {
        border-right: none;
    }
    .payment-mini-label {
        font-size: 0.72rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .payment-mini-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Risk Badges (Image 3 Table Style) */
    .risk-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 700;
        text-align: center;
    }
    .risk-pill.high {
        background: #EF4444;
        color: #FFFFFF;
    }
    .risk-pill.medium {
        background: #F59E0B;
        color: #FFFFFF;
    }
    .risk-pill.low {
        background: #84CC16;
        color: #0F172A;
    }
    .risk-pill.safe {
        background: #06B6D4;
        color: #0F172A;
    }

    /* Bottom Alert Cards (Image 3 Style) */
    .docynx-alert-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 24px;
    }
    @media (max-width: 1200px) {
        .docynx-alert-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }
    @media (max-width: 768px) {
        .docynx-alert-grid {
            grid-template-columns: 1fr;
        }
    }
    .docynx-alert-card {
        background: #141026;
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 10px;
        padding: 14px 16px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }
    .docynx-alert-icon {
        color: #EF4444;
        font-size: 1.2rem;
        line-height: 1;
    }
    .docynx-alert-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 2px;
    }
    .docynx-alert-desc {
        font-size: 0.72rem;
        color: #CBD5E1;
        line-height: 1.35;
    }
    .docynx-alert-date {
        font-size: 0.68rem;
        color: #94A3B8;
        margin-top: 4px;
    }

    /* Sidebar Navigation (Image 3 Style) */
    section[data-testid="stSidebar"] {
        background-color: #070914 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .sidebar-alert-box {
        background: #190F24;
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 10px;
        padding: 14px;
        margin-top: 24px;
        text-align: center;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.15);
    }
    .sidebar-alert-label {
        font-size: 0.76rem;
        color: #F87171;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin-bottom: 6px;
    }
    .sidebar-alert-val {
        font-size: 2.1rem;
        font-weight: 900;
        color: #EF4444;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .sidebar-alert-btn {
        display: inline-block;
        width: 100%;
        margin-top: 10px;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid #C026D3;
        background: transparent;
        color: #E879F9;
        font-size: 0.72rem;
        font-weight: 700;
        text-align: center;
        text-decoration: none;
    }
    .sidebar-alert-btn:hover {
        background: rgba(192, 38, 211, 0.15);
    }

    /* Active Sidebar Item Highlight */
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 4px;
        transition: background 0.15s ease, color 0.15s ease;
    }
    .sidebar-nav-item.active {
        background: linear-gradient(135deg, #9333EA 0%, #C026D3 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.35);
    }
</style>
"""


def apply_theme():
    """Injects Docynx styling into the active Streamlit page."""
    st.markdown(DOCYNX_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading primary transaction database...", ttl=3600)
def get_dataset(use_sample: bool = False) -> pd.DataFrame:
    """Cached loader for the primary processed Parquet dataset."""
    return load_processed_data(sample=use_sample)


@st.cache_data(show_spinner="Loading credit card comparative database...", ttl=3600)
def get_creditcard_dataset() -> pd.DataFrame:
    """Cached loader for the European Credit Card dataset."""
    return load_creditcard_data()


def render_docynx_header(title: str = "Orders & Frauds Analytics Dashboards", subtitle: str = "Real-Time Transaction Intelligence & Fraud Monitoring"):
    """
    Renders the Docynx Brand Header with Glowing Purple Tag (Image 3 Style).
    """
    st.markdown(
        f"""
        <div class="docynx-header">
            <div class="docynx-brand-wrap">
                <div class="docynx-logo">Docynx</div>
                <div>
                    <div class="docynx-title">{title}</div>
                    <div class="docynx-subtitle">{subtitle}</div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span style="background: rgba(168,85,247,0.15); border: 1px solid rgba(168,85,247,0.3); color: #C084FC; padding: 4px 12px; border-radius: 9999px; font-size: 0.76rem; font-weight: 700;">
                    LIVE MONITORING
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_docynx_kpi(label: str, value: str, delta: str = "↑ 108.7% vs Apr 2026", icon: str = "🛍️", icon_bg: str = "#EC4899", delta_dir: str = "up"):
    """
    Generates an HTML snippet for a Docynx KPI card (Image 3 Top Row).
    """
    delta_class = "down" if delta_dir == "down" else ""
    return f"""
    <div class="docynx-kpi-card">
        <div class="kpi-header-label">
            <span>{label}</span>
        </div>
        <div class="kpi-val-row">
            <div class="kpi-icon-badge" style="background: {icon_bg}25; color: {icon_bg};">
                {icon}
            </div>
            <div class="kpi-main-val">{value}</div>
        </div>
        <div class="kpi-growth-delta {delta_class}">{delta}</div>
    </div>
    """


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renders the Docynx Left Sidebar Navigation & Filter Slicers (Image 3 Style).
    """
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
            <div style="font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #D946EF, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Docynx
            </div>
            <div style="font-size: 0.74rem; color: #94A3B8;">Enterprise Fraud Surveillance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Dataset Partition
    sources = ["All Historical Sources"] + sorted(list(df["source_dataset"].unique()))
    selected_source = st.sidebar.selectbox("Data Partition", sources, index=0)

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
    selected_state = st.sidebar.selectbox("State / Region", all_states, index=0)

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

    # Sidebar Bottom Alert Card (Image 3 Left Bottom Box: ⚠️ Potential fraud detected: 610)
    current_fraud_count = int((filtered_df["is_fraud"] == 1).sum()) if "is_fraud" in filtered_df.columns else 0
    st.sidebar.markdown(
        f"""
        <div class="sidebar-alert-box">
            <div class="sidebar-alert-label">
                <span>⚠️</span> Potential fraud detected
            </div>
            <div class="sidebar-alert-val">{current_fraud_count:,}</div>
            <div style="font-size: 0.70rem; color: #94A3B8; margin-top: 2px;">Confirmed Historical Incidents</div>
            <a class="sidebar-alert-btn" href="/Transaction_Explorer" target="_self">View High Risk Customers</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df
