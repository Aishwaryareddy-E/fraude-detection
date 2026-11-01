"""
Page 6: Credit Card Benchmark & PCA Forensic Analysis
Comparative benchmark and anomaly subspace analysis using creditcard.csv (284,807 European banking transactions).
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.analytics import (
    get_creditcard_metrics,
    compare_fraud_datasets,
    calculate_kpis,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    get_creditcard_dataset,
    render_hero,
    render_kpi_card,
    render_circular_gauge,
)

st.set_page_config(
    page_title="CreditCard Benchmark | Financial Fraud Analytics",
    page_icon="💳",
    layout="wide",
)

apply_theme()

# Load datasets
cc_df = get_creditcard_dataset()
retail_df = get_dataset()

# Calculate credit card metrics
cc_kpis = get_creditcard_metrics(cc_df)

render_hero(
    title="Credit Card Anomaly & Comparative Benchmark",
    subtitle=(
        "Forensic analysis of the European Banking Credit Card dataset (creditcard.csv) with PCA "
        "latent subspace decomposition, feature correlation profiling, and cross-dataset comparative benchmarking."
    ),
    badge_text="COMPARATIVE BENCHMARK",
    pulse_alert=f"{cc_kpis['fraud_transactions']} FRAUD LABELS (0.173%)",
)

# Top KPI Row with deltas
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        render_kpi_card("Total Transactions", f"{cc_kpis['total_transactions']:,}", "48-Hour European Window", "neutral", "284,807 Total", "neutral"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        render_kpi_card("Confirmed Fraud", f"{cc_kpis['fraud_transactions']:,}", f"Rate: {cc_kpis['fraud_rate']:.3f}%", "fraud", "0.173% Prevalence", "up"),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        render_kpi_card("Total Dollar Turnover", f"${cc_kpis['total_amount']:,.0f}", f"Fraud: ${cc_kpis['fraud_amount']:,.0f}", "legit", "€/USD Gross", "neutral"),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        render_kpi_card("Mean Legit Ticket", f"${cc_kpis['mean_legit_amount']:.2f}", f"Median: ${cc_kpis['median_legit_amount']:.2f}", "neutral", "Normal Ticket", "down"),
        unsafe_allow_html=True,
    )
with c5:
    disparity = cc_kpis['mean_fraud_amount'] / cc_kpis['mean_legit_amount']
    st.markdown(
        render_kpi_card("Mean Fraud Ticket", f"${cc_kpis['mean_fraud_amount']:.2f}", f"Disparity: {disparity:.2f}x", "warning", "+38.4% vs Legit", "up"),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Tabs: 1. PCA Subspace Correlation | 2. Cross-Dataset Comparative Benchmark | 3. 48-Hour Wave Dynamics | 4. Anomaly Detection Engine
tab_pca, tab_bench, tab_time, tab_engine = st.tabs([
    "🔬 PCA Subspace Correlations",
    "⚖️ Cross-Dataset Comparative Benchmark",
    "⏳ 48-Hour Velocity Waves",
    "🛡️ PCA Anomaly Engine Sandbox",
])

with tab_pca:
    st.markdown("### 📊 Correlation Spectrum: PCA Latent Components vs Fraud Target")
    st.markdown(
        "Because `creditcard.csv` features anonymized PCA principal components (`V1` to `V28`), "
        "correlation profiling reveals which mathematical dimensions isolate fraudulent behavior from legitimate transactions."
    )

    corrs_series = pd.Series(cc_kpis["correlations"]).sort_values()
    corr_df = pd.DataFrame({"Feature": corrs_series.index, "Correlation": corrs_series.values})

    fig_corr = px.bar(
        corr_df,
        x="Feature",
        y="Correlation",
        color="Correlation",
        color_continuous_scale="RdBu_r",
        title="Pearson Correlation of All Features with Fraud Class",
    )
    fig_corr.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### 🔴 Top Negative Correlated Dimensions")
        neg_df = pd.DataFrame(list(cc_kpis["top_negative_features"].items()), columns=["Component", "Correlation with Fraud"])
        st.dataframe(neg_df.style.format({"Correlation with Fraud": "{:.4f}"}), use_container_width=True, hide_index=True)

        st.info("💡 **Latent Insight**: Strong negative values in `V14` (r = -0.30) and `V17` (r = -0.33) strongly signal high probability of card compromise.")

    with col_p2:
        st.markdown("#### 🔵 Top Positive Correlated Dimensions")
        pos_df = pd.DataFrame(list(cc_kpis["top_positive_features"].items()), columns=["Component", "Correlation with Fraud"])
        st.dataframe(pos_df.style.format({"Correlation with Fraud": "{:.4f}"}), use_container_width=True, hide_index=True)

        st.info("💡 **Latent Insight**: Elevated positive values in `V11` (r = +0.15) and `V4` (r = +0.13) act as co-indicators of anomalous card velocity.")

    # 2D Scatter of Top 2 Separating Dimensions (V14 vs V17)
    st.markdown("#### 🌌 Latent Subspace Separation: V14 vs V17")
    # Sample legitimate for smooth rendering
    legit_sample = cc_df[cc_df["Class"] == 0].sample(n=8000, random_state=42)
    fraud_all = cc_df[cc_df["Class"] == 1]
    plot_sub = pd.concat([legit_sample, fraud_all])

    fig_scatter = px.scatter(
        plot_sub,
        x="V14",
        y="V17",
        color="Class",
        color_discrete_map={0: "rgba(56, 189, 248, 0.4)", 1: "#EF4444"},
        symbol="Class",
        opacity=0.75,
        labels={"V14": "PCA Dimension V14", "V17": "PCA Dimension V17", "Class": "Fraud (1)"},
        title="2D Projection in Principal Component Space (Notice extreme fraud clustering in bottom-left)",
    )
    fig_scatter.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        margin=dict(l=20, r=20, t=40, b=30),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab_bench:
    st.markdown("### ⚖️ Side-by-Side Dataset Architecture Comparison")
    st.markdown(
        "A rigorous comparative evaluation demonstrating why combining `creditcard.csv` and `archive (8).zip` "
        "into a single table is technically flawed, and how their distinct forensic characteristics complement one another."
    )

    bench_table = compare_fraud_datasets(retail_df, cc_df)
    st.dataframe(bench_table, use_container_width=True, hide_index=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #38BDF8; padding: 16px; border-radius: 8px;">
                <div style="font-weight: 700; color: #38BDF8; margin-bottom: 6px;">Primary Dataset (`archive (8).zip`) Characteristics</div>
                <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                    • <b>1,852,394 Records</b> spanning a 24-month horizon (2019-2020).<br>
                    • Rich domain features: Merchant Categories (MCC), Physical Coordinates (Lat/Long), Customer Demographics (DOB/Age).<br>
                    • Massive <b>7.84x</b> dollar ticket disparity ($530 fraud vs $67 legit).<br>
                    • Primary analytical signal is <b>behavioral & temporal</b> (late-night hours, merchant category).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_g2:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #A855F7; padding: 16px; border-radius: 8px;">
                <div style="font-weight: 700; color: #A855F7; margin-bottom: 6px;">Credit Card Dataset (`creditcard.csv`) Characteristics</div>
                <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                    • <b>284,807 Records</b> across a condensed 48-hour European banking snapshot.<br>
                    • Fully anonymized PCA features (`V1` to `V28`) with zero merchant or demographic context.<br>
                    • Subtle <b>1.38x</b> dollar ticket disparity ($122 fraud vs $88 legit).<br>
                    • Primary analytical signal is <b>mathematical subspace anomaly</b> (extreme z-scores in V14, V17).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_time:
    st.markdown("### ⏳ 48-Hour Wave Dynamics & Amount Distribution")

    # Time in hours
    cc_time = cc_df[["Time", "Amount", "Class"]].copy()
    cc_time["Hour"] = (cc_time["Time"] / 3600).astype(int)

    hourly_cc = cc_time.groupby("Hour").agg(
        total=("Class", "count"),
        fraud=("Class", "sum"),
    ).reset_index()
    hourly_cc["fraud_rate"] = hourly_cc["fraud"] / hourly_cc["total"] * 100

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        fig_cc_wave = go.Figure()
        fig_cc_wave.add_trace(
            go.Bar(
                x=hourly_cc["Hour"],
                y=hourly_cc["total"],
                name="Total Swipes",
                marker_color="#1E293B",
                marker_line=dict(color="#A855F7", width=1),
            )
        )
        fig_cc_wave.add_trace(
            go.Scatter(
                x=hourly_cc["Hour"],
                y=hourly_cc["fraud"],
                name="Fraud Swipes",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="#EF4444", width=3),
            )
        )
        fig_cc_wave.update_layout(
            title="48-Hour Transaction Cycle & Fraud Spikes",
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            xaxis=dict(title="Elapsed Hours (0 to 47)", dtick=4),
            yaxis=dict(title="Total Volume", showgrid=False),
            yaxis2=dict(
                title="Fraud Incidents",
                overlaying="y",
                side="right",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=30),
        )
        st.plotly_chart(fig_cc_wave, use_container_width=True)

    with col_w2:
        fig_cc_box = px.box(
            cc_time.sample(n=10000, random_state=42),
            x="Class",
            y="Amount",
            color="Class",
            color_discrete_map={0: "#10B981", 1: "#EF4444"},
            log_y=True,
            title="Amount Distribution by Class (Log Scale)",
            labels={"Class": "Class (0=Legit, 1=Fraud)", "Amount": "Amount ($ Log)"},
        )
        fig_cc_box.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.4)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=30),
        )
        st.plotly_chart(fig_cc_box, use_container_width=True)

with tab_engine:
    st.markdown("### 🛡️ Composite Latent Anomaly Score Engine")
    st.markdown(
        "Demonstrates how multi-dimensional distance from normal PCA distribution flags suspicious transactions. "
        "Score formula: Weighted composite metric using $Z = -0.33 V_{17} - 0.30 V_{14} - 0.26 V_{12} + 0.15 V_{11} + 0.13 V_4$."
    )

    # Compute composite anomaly score on a sample
    sample_eval = cc_df.sample(n=15000, random_state=42).copy()
    sample_eval["anomaly_score"] = (
        -0.33 * sample_eval["V17"]
        - 0.30 * sample_eval["V14"]
        - 0.26 * sample_eval["V12"]
        + 0.15 * sample_eval["V11"]
        + 0.13 * sample_eval["V4"]
    )

    threshold = st.slider("Anomaly Investigation Threshold", min_value=1.0, max_value=12.0, value=4.5, step=0.5)

    sample_eval["flagged_anomaly"] = sample_eval["anomaly_score"] >= threshold
    flagged_count = int(sample_eval["flagged_anomaly"].sum())
    true_fraud_caught = int(((sample_eval["flagged_anomaly"]) & (sample_eval["Class"] == 1)).sum())
    total_fraud_in_sample = int((sample_eval["Class"] == 1).sum())

    c_e1, c_e2, c_e3 = st.columns(3)
    with c_e1:
        st.metric("Total Flagged Transactions", f"{flagged_count:,}")
    with c_e2:
        detection_recall = (true_fraud_caught / total_fraud_in_sample * 100) if total_fraud_in_sample > 0 else 0
        st.metric("Fraud Recall @ Threshold", f"{detection_recall:.1f}%", f"{true_fraud_caught} of {total_fraud_in_sample} frauds caught")
    with c_e3:
        precision = (true_fraud_caught / flagged_count * 100) if flagged_count > 0 else 0
        st.metric("Investigation Precision", f"{precision:.1f}%", "True Positives / Total Flagged")

    st.markdown("#### Top Flagged Anomalous Records")
    st.dataframe(
        sample_eval[sample_eval["flagged_anomaly"]][
            ["Time", "Amount", "V14", "V17", "V12", "anomaly_score", "Class"]
        ].sort_values("anomaly_score", ascending=False).head(50).style.format({
            "Amount": "${:.2f}",
            "V14": "{:.3f}",
            "V17": "{:.3f}",
            "V12": "{:.3f}",
            "anomaly_score": "{:.2f}",
        }),
        use_container_width=True,
    )
