"""
Page 5: Reports & Executive Intelligence
Generates downloadable CSV and Excel analytical summaries, compiles KPI scorecards,
and presents strategic business recommendations.
"""

import streamlit as st
import pandas as pd
import io
import json
from src.analytics import (
    calculate_kpis,
    get_category_metrics,
    get_monthly_trends,
    get_state_metrics,
    generate_business_insights,
)
from app.ui_components import (
    apply_theme,
    get_dataset,
    render_hero,
    render_kpi_card,
    render_sidebar_filters,
)

st.set_page_config(
    page_title="Executive Reports | Financial Fraud Analytics",
    page_icon="📑",
    layout="wide",
)

apply_theme()
df_raw = get_dataset()
df = render_sidebar_filters(df_raw)

render_hero(
    title="Executive Forensic Intelligence & Analytical Reporting",
    subtitle=(
        "Downloadable intelligence packages, executive KPI balance sheets, "
        "and empirical business recommendations for institutional fraud prevention units."
    ),
    badge_text="REPORTS & EXPORT",
)

kpis = calculate_kpis(df)
cat_metrics = get_category_metrics(df)
state_metrics = get_state_metrics(df)
monthly_metrics = get_monthly_trends(df)

# Section 1: Executive KPI Scorecard
st.markdown("### 📊 Executive Forensic Balance Sheet")

summary_table = pd.DataFrame([
    {"Metric Name": "Total Processed Transactions", "Calculated Value": f"{kpis['total_transactions']:,}", "Analytical Context": "Total transaction volume evaluated"},
    {"Metric Name": "Historical Fraud Identifications", "Calculated Value": f"{kpis['fraud_transactions']:,}", "Analytical Context": "Strictly verified historical fraud instances"},
    {"Metric Name": "Systemic Fraud Rate", "Calculated Value": f"{kpis['fraud_rate']:.4f}%", "Analytical Context": "Fraud instances as % of total transactions"},
    {"Metric Name": "Total Dollar Volume Processed", "Calculated Value": f"${kpis['total_amount']:,.2f}", "Analytical Context": "Gross financial turnover (2019-2020)"},
    {"Metric Name": "Fraud-Associated Dollar Volume", "Calculated Value": f"${kpis['fraud_amount']:,.2f}", "Analytical Context": "Historical transaction values flagged as fraud"},
    {"Metric Name": "Fraud Dollar Share", "Calculated Value": f"{kpis['fraud_amount_share']:.4f}%", "Analytical Context": "Fraud dollars as % of total gross dollars"},
    {"Metric Name": "Mean Legitimate Ticket Size", "Calculated Value": f"${kpis['avg_legit_amount']:.2f}", "Analytical Context": "Average non-fraudulent purchase ticket"},
    {"Metric Name": "Mean Fraudulent Ticket Size", "Calculated Value": f"${kpis['avg_fraud_amount']:.2f}", "Analytical Context": "Average fraudulent transaction value"},
    {"Metric Name": "Value Disparity Multiplier", "Calculated Value": f"{kpis['amount_fraud_ratio']:.2f}x", "Analytical Context": "Multiplier of fraud ticket vs legit ticket"},
])

st.dataframe(summary_table, use_container_width=True, hide_index=True)

# Section 2: Empirical Strategic Business Findings
st.markdown("### 💡 Data-Driven Business Findings & Policy Directives")

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #38BDF8; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #38BDF8; margin-bottom: 6px;">1. Online E-Commerce Vulnerability (shopping_net)</div>
            <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                <code>shopping_net</code> has the highest fraud rate (<b>1.593%</b>) among all categories, more than triple the baseline average (0.521%). 
                Additionally, <code>grocery_pos</code> exhibits the highest absolute fraud incident count (<b>2,228</b> incidents).
                <b>Directive:</b> Mandate biometric / 3DS challenge authentication on all online shopping transactions exceeding $250.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #EF4444; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #EF4444; margin-bottom: 6px;">2. Diurnal Attack Window (Hour 22 Spike)</div>
            <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                Fraud attacks are strongly diurnal. At hour 22:00 (10:00 PM), fraud rates surge to <b>2.601%</b> (a 5x spike over daytime averages), 
                accounting for 2,481 confirmed cases.
                <b>Directive:</b> Tighten transaction velocity scoring rules during the 22:00 – 04:00 nocturnal window.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b2:
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #F59E0B; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #F59E0B; margin-bottom: 6px;">3. Severe Dollar Value Disparity</div>
            <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                Fraudulent transactions average <b>$530.66</b> compared to <b>$67.65</b> for legitimate purchases. 
                Although fraud represents only 0.52% of transaction volume, it represents nearly <b>4.0% of total financial turnover</b>.
                <b>Directive:</b> Introduce secondary fraud analyst queues specifically triggered by first-time cardholder transactions over $500.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid #10B981; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #10B981; margin-bottom: 6px;">4. Geographic Concentration Hubs</div>
            <div style="color: #CBD5E1; font-size: 0.88rem; line-height: 1.5;">
                New York (NY) leads in raw fraud incident volume with <b>730 cases</b>. 
                Among jurisdictions with substantial activity (>= 5,000 transactions), Oregon (OR) demonstrates an elevated fraud rate of <b>0.746%</b>.
                <b>Directive:</b> Establish localized fraud rules for high-density metropolitan transaction clusters.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Section 3: Data Export Center
st.markdown("### 📥 Forensic Intelligence Export Center")
st.markdown("Export aggregated analytical tables directly to CSV or Excel for executive distribution.")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.markdown("#### 📄 Export Category Metrics (CSV)")
    cat_csv = cat_metrics.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Category Analytics (CSV)",
        data=cat_csv,
        file_name="category_fraud_analytics.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_exp2:
    st.markdown("#### 📗 Export Complete Executive Pack (Excel)")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        summary_table.to_excel(writer, sheet_name="KPI_Scorecard", index=False)
        cat_metrics.to_excel(writer, sheet_name="Category_Analytics", index=False)
        state_metrics.to_excel(writer, sheet_name="State_Analytics", index=False)
        monthly_metrics.to_excel(writer, sheet_name="Monthly_Trends", index=False)
    
    excel_data = excel_buffer.getvalue()
    st.download_button(
        label="Download Full Intelligence Pack (Excel .xlsx)",
        data=excel_data,
        file_name="Fraud_Analytics_Executive_Pack.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
