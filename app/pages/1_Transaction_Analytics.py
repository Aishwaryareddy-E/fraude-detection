"""
Page 1: Transaction Analytics Module
Analyzes transaction volume, amount distribution, merchant profiles, and customer spending habits.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import (
    calculate_kpis,
    get_category_metrics,
    get_merchant_metrics,
    get_age_metrics,
    get_amount_tier_metrics,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Transaction Analytics | Financial Fraud Analytics",
    page_icon="💳",
    layout="wide",
)

apply_theme()
df_raw = get_dataset()
df = render_sidebar_filters(df_raw)

render_hero(
    title="Transaction Volume & Merchant Analytics",
    subtitle=(
        "Comprehensive profiling of transaction velocity, commercial category spending, "
        "merchant concentration, and customer spending distributions."
    ),
    badge_text="TRANSACTION ANALYTICS",
)

kpis = calculate_kpis(df)

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        render_kpi_card("Total Transactions", f"{kpis['total_transactions']:,}", "Filtered ledger", "neutral", "💳"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        render_kpi_card("Total Value", f"${kpis['total_amount']:,.0f}", "Gross processed", "legit", "💵"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        render_kpi_card("Average Ticket", f"${kpis['avg_amount']:.2f}", "Mean ticket size", "neutral", "📊"),
        unsafe_allow_html=True,
    )
with c4:
    unique_merchants = df["clean_merchant"].nunique() if "clean_merchant" in df.columns else df["merchant"].nunique()
    st.markdown(
        render_kpi_card("Active Merchants", f"{unique_merchants:,}", "Distinct commercial entities", "warning", "🏪"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for structured exploration
tab1, tab2, tab3 = st.tabs(["🏷️ Category Performance", "🏪 Merchant Intelligence", "👥 Customer Spending Habits"])

with tab1:
    st.markdown("### Transaction Volume & Dollar Share by Category")
    cat_df = get_category_metrics(df)

    col_c1, col_c2 = st.columns([3, 2])

    with col_c1:
        # Category volume & total spend bar chart
        fig_cat_vol = px.bar(
            cat_df,
            x="category",
            y="total_transactions",
            color="total_amount",
            color_continuous_scale="Viridis",
            labels={"category": "Category", "total_transactions": "Volume", "total_amount": "Total Spend ($)"},
            title="Total Transaction Volume by Category (Color = Dollar Spend)",
        )
        fig_cat_vol.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            xaxis_tickangle=-45,
            margin=dict(l=20, r=20, t=40, b=50),
        )
        st.plotly_chart(fig_cat_vol, use_container_width=True)

    with col_c2:
        # Donut chart of dollar spend by category
        fig_donut = px.pie(
            cat_df,
            names="category",
            values="total_amount",
            hole=0.55,
            title="Dollar Share Distribution",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_donut, use_container_width=True)

    # Detailed Category Summary Table
    st.markdown("#### Category Metrics Breakdown")
    st.dataframe(
        cat_df[[
            "category", "total_transactions", "fraud_transactions", "fraud_rate", "total_amount", "avg_amount"
        ]].rename(columns={
            "category": "Category",
            "total_transactions": "Total Transactions",
            "fraud_transactions": "Fraud Cases",
            "fraud_rate": "Fraud Rate (%)",
            "total_amount": "Total Amount ($)",
            "avg_amount": "Avg Ticket ($)",
        }).style.format({
            "Total Transactions": "{:,}",
            "Fraud Cases": "{:,}",
            "Fraud Rate (%)": "{:.3f}%",
            "Total Amount ($)": "${:,.2f}",
            "Avg Ticket ($)": "${:.2f}",
        }),
        use_container_width=True,
    )

with tab2:
    st.markdown("### Top Merchants by Transaction Volume")
    merch_df = get_merchant_metrics(df, top_n=20)

    fig_merch = px.bar(
        merch_df,
        x="total_transactions",
        y="clean_merchant" if "clean_merchant" in merch_df.columns else "merchant",
        orientation="h",
        color="avg_amount",
        color_continuous_scale="Tealgrn",
        labels={"clean_merchant": "Merchant", "total_transactions": "Transactions", "avg_amount": "Avg Ticket ($)"},
        title="Top 20 Merchants by Activity Volume (Color = Average Ticket)",
    )
    fig_merch.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=40, b=30),
    )
    st.plotly_chart(fig_merch, use_container_width=True)

with tab3:
    st.markdown("### Customer Demographic & Ticket Size Breakdown")
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        age_metrics = get_age_metrics(df)
        if not age_metrics.empty:
            fig_age = px.bar(
                age_metrics,
                x="age_group",
                y="total_transactions",
                color="avg_amount",
                color_continuous_scale="Blues",
                labels={"age_group": "Age Bracket", "total_transactions": "Transaction Count", "avg_amount": "Avg Ticket ($)"},
                title="Transaction Activity by Age Demographic",
            )
            fig_age.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                margin=dict(l=20, r=20, t=40, b=30),
            )
            st.plotly_chart(fig_age, use_container_width=True)

    with col_d2:
        tier_metrics = get_amount_tier_metrics(df)
        if not tier_metrics.empty:
            fig_tier = px.bar(
                tier_metrics,
                x="amount_tier",
                y="total_transactions",
                color="total_amount",
                color_continuous_scale="Purples",
                labels={"amount_tier": "Ticket Tier", "total_transactions": "Volume", "total_amount": "Total Dollars ($)"},
                title="Transaction Distribution by Ticket Size Tier",
            )
            fig_tier.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                xaxis_tickangle=-30,
                margin=dict(l=20, r=20, t=40, b=30),
            )
            st.plotly_chart(fig_tier, use_container_width=True)
