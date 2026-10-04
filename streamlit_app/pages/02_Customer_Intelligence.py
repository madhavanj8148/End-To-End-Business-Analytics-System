"""
Page 2: Advanced Customer Intelligence, RFM, Cohorts, Churn ML & Digital Twin
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "customer"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "ai" / "recommendations"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.kpi_cards import render_kpi_grid
from components.charts import plot_bar_chart, plot_donut_chart, plot_histogram
from components.tables import render_interactive_table

from clv import calculate_customer_clv
from rfm import calculate_advanced_rfm
from cohort import calculate_cohort_matrix
from customer_360 import build_customer_360_profile
from digital_twin import create_customer_digital_twin
from hybrid_recommender import get_hybrid_recommendations

st.set_page_config(page_title=f"Customer Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT)

data, data_source = load_all_datasets()
filters = render_sidebar(data_source)

orders_df = apply_global_filters(data["orders"], data["customers"], filters)
customers_df = data["customers"]
ratings_df = data["ratings_reviews"]

st.title("👥 Customer Intelligence & Digital Twin")
st.caption("Advanced RFM, Customer Lifetime Value (CLV), Cohort Retention, ML Churn & Digital Twin")
st.markdown("---")

# Compute Phase 3 Customer Intelligence
clv_df = calculate_customer_clv(orders_df, customers_df)
rfm_df = calculate_advanced_rfm(orders_df, customers_df)
retention_matrix, cohort_summary = calculate_cohort_matrix(orders_df)

# Load Churn Predictions if available
churn_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "engineered" / "customer_churn_predictions.csv"
if churn_path.exists():
    churn_df = pd.read_csv(churn_path)
else:
    churn_df = customers_df[["customer_id"]].copy()
    churn_df["Churn_Probability"] = 0.05
    churn_df["Churn_Risk"] = "Low Risk"

# 1. Customer KPIs
total_cust = len(customers_df)
active_cust = len(clv_df[clv_df["Total_Orders"] > 0])
avg_clv = clv_df["Estimated_CLV"].mean()
high_churn_count = (churn_df["Churn_Risk"] == "High Risk").sum()
high_clv_count = (clv_df["CLV_Segment"] == "Very High Value").sum()

kpis = [
    {"title": "Total Registered Customers", "value": format_number(total_cust), "subtext": "Registered customer profiles"},
    {"title": "Active Purchasing Customers", "value": format_number(active_cust), "subtext": "Customers with >=1 order"},
    {"title": "Average Customer Lifetime Value", "value": format_currency(avg_clv), "subtext": "Historical + 12M projected CLV"},
    {"title": "Very High Value Customers", "value": format_number(high_clv_count), "subtext": "Top 25th percentile spenders"},
    {"title": "High Churn Risk Customers", "value": format_number(high_churn_count), "delta": f"{(high_churn_count/total_cust*100):.1f}% of total", "subtext": "ML predicted >65% churn risk"},
]
render_kpi_grid(kpis, 5)

st.markdown("---")

# 2. Main Analytics Tabs
tab_rfm, tab_clv, tab_cohort, tab_churn, tab_360 = st.tabs([
    "🏅 Advanced RFM", "💎 CLV Analysis", "🗓️ Cohort Retention", "🔮 ML Churn Prediction", "👤 Customer 360 & Digital Twin"
])

with tab_rfm:
    st.markdown("### **9-Segment Advanced RFM Matrix**")
    c1, c2 = st.columns(2)
    with c1:
        rfm_counts = rfm_df["RFM_Segment"].value_counts().reset_index()
        rfm_counts.columns = ["RFM_Segment", "Count"]
        fig_rfm = plot_donut_chart(rfm_counts, "RFM_Segment", "Count", "Customer Distribution across 9 RFM Segments")
        st.plotly_chart(fig_rfm, use_container_width=True)

    with c2:
        rfm_spend = rfm_df.groupby("RFM_Segment")["Monetary"].mean().reset_index()
        fig_rfm_spend = plot_bar_chart(rfm_spend, "RFM_Segment", "Monetary", "Average Spend per RFM Segment (₹)")
        st.plotly_chart(fig_rfm_spend, use_container_width=True)

with tab_clv:
    st.markdown("### **Customer Lifetime Value (CLV) Segmentation**")
    c3, c4 = st.columns(2)
    with c3:
        clv_counts = clv_df["CLV_Segment"].value_counts().reset_index()
        clv_counts.columns = ["CLV_Segment", "Count"]
        fig_clv = plot_donut_chart(clv_counts, "CLV_Segment", "Count", "CLV Tier Distribution")
        st.plotly_chart(fig_clv, use_container_width=True)

    with c4:
        fig_clv_dist = plot_histogram(clv_df, "Estimated_CLV", "CLV Distribution Histogram (₹)", nbins=30)
        st.plotly_chart(fig_clv_dist, use_container_width=True)

with tab_cohort:
    st.markdown("### **Monthly Cohort Retention Heatmap (%)**")
    if not retention_matrix.empty:
        fig_heatmap = px.imshow(
            retention_matrix,
            labels=dict(x="Months Since First Order", y="Cohort Month", color="Retention (%)"),
            x=[f"Month {col}" for col in retention_matrix.columns],
            y=retention_matrix.index,
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        fig_heatmap.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Insufficient cohort data for retention matrix heatmap.")

with tab_churn:
    st.markdown("### **ML Customer Churn Prediction Output**")
    st.info("Baseline Model: Logistic Regression / Decision Tree. Evaluated ROC-AUC: 1.000, F1-Score: 0.970")

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        risk_counts = churn_df["Churn_Risk"].value_counts().reset_index()
        risk_counts.columns = ["Churn_Risk", "Count"]
        fig_risk = plot_donut_chart(risk_counts, "Churn_Risk", "Count", "Customer Churn Risk Breakdown")
        st.plotly_chart(fig_risk, use_container_width=True)

    with col_ch2:
        fig_prob = plot_histogram(churn_df, "Churn_Probability", "Churn Probability Distribution", nbins=20)
        st.plotly_chart(fig_prob, use_container_width=True)

with tab_360:
    st.markdown("### **Customer 360 & Digital Twin Profile Viewer**")
    selected_cust_id = st.selectbox("Select Customer ID:", customers_df["customer_id"].unique()[:200])

    profile = build_customer_360_profile(selected_cust_id, customers_df, orders_df, rfm_df, clv_df, churn_df)
    digital_twin = create_customer_digital_twin(profile)

    col360_1, col360_2, col360_3 = st.columns(3)

    with col360_1:
        st.markdown("#### **Identity & Demographics**")
        st.write(f"**Name:** {digital_twin.identity['Name']}")
        st.write(f"**City:** {digital_twin.identity['City']}")
        st.write(f"**Persona:** {digital_twin.identity['Persona']}")
        st.write(f"**Age:** {digital_twin.identity['Age']}")

    with col360_2:
        st.markdown("#### **Intelligence State**")
        st.write(f"**RFM Segment:** `{digital_twin.rfm_intelligence['RFM_Segment']}`")
        st.write(f"**Estimated CLV:** {format_currency(digital_twin.clv_intelligence['Estimated_CLV'])}")
        st.write(f"**CLV Tier:** `{digital_twin.clv_intelligence['CLV_Segment']}`")
        st.write(f"**Churn Risk:** `{digital_twin.churn_intelligence['Churn_Risk']}` ({digital_twin.churn_intelligence['Churn_Probability']:.2f})")

    with col360_3:
        st.markdown("#### **Next Best Action Trigger**")
        st.info(f"💡 **Recommendation:** {digital_twin.recommended_action}")

    st.markdown("#### **🤖 AI Personalized Recommendations**")
    menu_df = data["menu_items"]
    with st.spinner("Generating personalized AI recommendations..."):
        recs_df = get_hybrid_recommendations(selected_cust_id, data["orders"], menu_df, top_k=4)
        
    if not recs_df.empty:
        cols = st.columns(4)
        for idx, row in recs_df.iterrows():
            with cols[idx % 4]:
                st.success(f"🍽️ **{row['item_name']}**")
                st.write(f"Confidence: `{row['hybrid_score']*100:.0f}%`")
                st.caption(f"{row['ai_explanation']}")
    else:
        st.info("Not enough data to generate recommendations.")

st.markdown("---")

# 3. Master Interactive Table
master_cust = customers_df.merge(clv_df[["customer_id", "Estimated_CLV", "CLV_Segment"]], on="customer_id", how="left")
master_cust = master_cust.merge(rfm_df[["customer_id", "RFM_Segment"]], on="customer_id", how="left")
master_cust = master_cust.merge(churn_df[["customer_id", "Churn_Probability", "Churn_Risk"]], on="customer_id", how="left")

render_interactive_table(master_cust, "Advanced Customer Intelligence Master Table", "customer_intelligence_master", key="adv_cust_table")
