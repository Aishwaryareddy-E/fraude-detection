"""
Financial Fraud Detection & Analytics Dashboard
Executive Overview Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import (
    calculate_kpis,
    get_monthly_trends,
    get_category_metrics,
    get_hourly_trends,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Executive Overview | Financial Fraud Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# Load dataset
df_raw = get_dataset()

# Render global filters
df = render_sidebar_filters(df_raw)

# Hero Header
render_hero(
    title="Financial Fraud Detection & Analytics System",
    subtitle=(
        "Enterprise-grade forensic dashboard answering core financial questions through "
        "rigorous historical transaction analysis across 1.85M validated records (2019–2020)."
    ),
    badge_text="EXECUTIVE OVERVIEW",
)

# Core Business Questions Accordion / Guide
with st.expander("📌 Key Business Questions & Strategic Answers", expanded=False):
    st.markdown(
        """
        1. **How many financial transactions are happening?**  
           *1,852,394 total transactions across 2019–2020 ($129.79M total historical volume).*
        2. **How many transactions are historically identified as fraudulent?**  
           *9,651 confirmed fraud cases, establishing a baseline fraud rate of 0.521%.*
        3. **What patterns are associated with fraudulent transactions?**  
           *Fraudulent transactions average **$530.66**, which is **7.84x higher** than legitimate purchases ($67.65). Fraud spikes sharply between 22:00 and 03:00.*
        4. **Which transaction categories, merchants, times, and locations show higher fraud rates?**  
           *`shopping_net` (1.59% fraud rate), `grocery_pos` (2,228 fraud cases), late evening hour 22:00 (2.60% fraud rate), and NY/OR state corridors.*
        5. **What insights can financial analysts use to investigate suspicious patterns?**  
           *Multi-vector investigation indicators: high transaction value ($300+), high physical distance (80km+), late-night timing, and high-risk merchant categories.*
        """
    )

# Compute KPIs on filtered view
kpis = calculate_kpis(df)

# Render KPI Grid
st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        render_kpi_card(
            label="Total Transactions",
            value=f"{kpis['total_transactions']:,}",
            subtext=f"{kpis['legitimate_transactions']:,} verified legitimate",
            status="neutral",
            icon="💳",
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        render_kpi_card(
            label="Historical Fraud Records",
            value=f"{kpis['fraud_transactions']:,}",
            subtext=f"Fraud Rate: {kpis['fraud_rate']:.3f}%",
            status="fraud",
            icon="🚨",
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        render_kpi_card(
            label="Total Dollar Volume",
            value=f"${kpis['total_amount']:,.0f}",
            subtext=f"Avg Ticket: ${kpis['avg_amount']:.2f}",
            status="legit",
            icon="💰",
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        render_kpi_card(
            label="Fraud-Associated Volume",
            value=f"${kpis['fraud_amount']:,.0f}",
            subtext=f"Share: {kpis['fraud_amount_share']:.2f}% of total dollars",
            status="warning",
            icon="⚠️",
        ),
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        render_kpi_card(
            label="Fraud vs Legit Disparity",
            value=f"{kpis['amount_fraud_ratio']:.1f}x",
            subtext=f"${kpis['avg_fraud_amount']:.2f} vs ${kpis['avg_legit_amount']:.2f}",
            status="fraud",
            icon="📈",
        ),
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Visualizations: Row 1
c_left, c_right = st.columns([3, 2])

with c_left:
    st.markdown("### 📅 Monthly Transaction Volume & Fraud Trajectory")
    monthly_data = get_monthly_trends(df)

    if not monthly_data.empty:
        fig_monthly = go.Figure()

        # Legitimate volume (bars on primary y-axis)
        fig_monthly.add_trace(
            go.Bar(
                x=monthly_data["year_month"],
                y=monthly_data["total_transactions"],
                name="Total Transactions",
                marker_color="#1E293B",
                marker_line=dict(color="#38BDF8", width=1),
                opacity=0.85,
            )
        )

        # Fraud transactions (line on secondary y-axis)
        fig_monthly.add_trace(
            go.Scatter(
                x=monthly_data["year_month"],
                y=monthly_data["fraud_transactions"],
                name="Fraud Transactions",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="#EF4444", width=3),
                marker=dict(size=7, color="#EF4444"),
            )
        )

        fig_monthly.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=30, b=30),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Total Transactions", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis2=dict(
                title="Fraud Cases",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(color="#EF4444"),
                titlefont=dict(color="#EF4444"),
            ),
            xaxis=dict(showgrid=False, tickangle=-45),
            height=370,
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    else:
        st.info("No data available for selected filter criteria.")

with c_right:
    st.markdown("### 🏷️ Top Fraud-Prone Categories")
    cat_data = get_category_metrics(df).head(7)

    if not cat_data.empty:
        fig_cat = px.bar(
            cat_data,
            x="fraud_rate",
            y="category",
            orientation="h",
            color="fraud_rate",
            color_continuous_scale=["#38BDF8", "#F59E0B", "#EF4444"],
            text=cat_data["fraud_rate"].apply(lambda v: f"{v:.2f}%"),
            labels={"fraud_rate": "Fraud Rate (%)", "category": "Category"},
        )
        fig_cat.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=30, b=30),
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            coloraxis_showscale=False,
            height=370,
        )
        fig_cat.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data found.")

# Visualizations: Row 2
col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown("### ⏰ Diurnal Fraud Intensity (Hourly Fraud Rate %)")
    hourly_data = get_hourly_trends(df)

    if not hourly_data.empty:
        fig_hour = go.Figure()

        # Add shaded risk area for night window
        fig_hour.add_vrect(
            x0=21.5,
            x1=23.5,
            fillcolor="rgba(239, 68, 68, 0.15)",
            layer="below",
            line_width=0,
            annotation_text="High Risk (22:00 - 03:00)",
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
                x=hourly_data["hour"],
                y=hourly_data["fraud_rate"],
                mode="lines+markers",
                name="Fraud Rate %",
                line=dict(color="#38BDF8", width=3),
                marker=dict(size=6, color="#0EA5E9"),
                fill="tozeroy",
                fillcolor="rgba(56, 189, 248, 0.1)",
            )
        )

        fig_hour.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            margin=dict(l=20, r=20, t=30, b=30),
            xaxis=dict(title="Hour of Day (0 to 23)", dtick=2, showgrid=False),
            yaxis=dict(title="Fraud Rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            height=320,
        )
        st.plotly_chart(fig_hour, use_container_width=True)

with col_h2:
    st.markdown("### ⚖️ Dollar Amount Distribution: Fraud vs Legitimate")
    # Subsample for smooth violin/box visualization without UI lagging
    sample_size = min(15000, len(df))
    plot_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df

    fig_box = px.box(
        plot_sample,
        x="is_fraud",
        y="amt",
        color="is_fraud",
        color_discrete_map={0: "#10B981", 1: "#EF4444"},
        log_y=True,
        labels={"is_fraud": "Fraud Classification", "amt": "Amount ($ Log Scale)"},
    )
    fig_box.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=30, b=30),
        xaxis=dict(
            tickvals=[0, 1],
            ticktext=["Legitimate (0)", "Fraudulent (1)"],
            showgrid=False,
        ),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        showlegend=False,
        height=320,
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Strategic Footnote
st.markdown(
    """
    <div style="font-size: 0.8rem; color: #64748B; margin-top: 24px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08);">
        <b>Forensic Audit Notice:</b> Fraud-associated amounts reflect historical transaction totals labelled as fraud, 
        not confirmed write-off losses or recovered amounts. This analytics suite evaluates historical patterns to empower 
        financial crime analysts with triage intelligence.
    </div>
    """,
    unsafe_allow_html=True,
)
