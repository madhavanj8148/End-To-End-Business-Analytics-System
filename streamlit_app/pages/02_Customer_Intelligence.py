"""
Page 2: Advanced Customer Intelligence, RFM, Cohorts, Churn ML & Digital Twin
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "customer"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "ai" / "recommendations"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.charts import plot_bar_chart, plot_donut_chart, plot_histogram
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

from clv import calculate_customer_clv
from rfm import calculate_advanced_rfm
from cohort import calculate_cohort_matrix
from customer_360 import build_customer_360_profile
from digital_twin import create_customer_digital_twin
from hybrid_recommender import get_hybrid_recommendations

st.set_page_config(page_title=f"Customer Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

apply_custom_theme()

# Hide Sidebar for cinematic feel
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

data, data_source = load_all_datasets()
# filters = render_sidebar(data_source) # Hidden sidebar per instructions

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="Customer Intelligence Console", 
        subtitle="Advanced Segmentation, Retention Analytics & ML Churn Prediction",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

orders_df = data["orders"]
customers_df = data["customers"]

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

# ==========================================
# CUSTOMER INTELLIGENCE CONSOLE - TOP KPIs
# ==========================================
total_cust = len(customers_df)
active_cust = len(clv_df[clv_df["Total_Orders"] > 0])
avg_clv = clv_df["Estimated_CLV"].mean()
high_churn_count = (churn_df["Churn_Risk"] == "High Risk").sum()
high_clv_count = (clv_df["CLV_Segment"] == "Very High Value").sum()

k1, k2, k3, k4, k5 = st.columns(5)
metrics_orbit = [
    ("TOTAL PROFILES", format_number(total_cust), ""),
    ("ACTIVE CUSTOMERS", format_number(active_cust), "var(--accent-cyan)"),
    ("AVERAGE CLV", format_currency(avg_clv), "var(--success)"),
    ("HIGH VALUE CUST", format_number(high_clv_count), "var(--accent-indigo)"),
    ("HIGH CHURN RISK", format_number(high_churn_count), "var(--danger)")
]
for col, (title, val, color) in zip([k1, k2, k3, k4, k5], metrics_orbit):
    with col:
        c_str = f"color: {color};" if color else "color: var(--text-primary);"
        border_top = f"border-top: 2px solid {color};" if color else "border-top: 2px solid var(--border-color);"
        st.markdown(f"""
        <div style="background: var(--surface-bg); border: 1px solid var(--border-color); {border_top} border-radius: 8px; padding: 1.25rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="font-size: 0.65rem; color: var(--text-secondary); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">{title}</div>
            <div style="font-size: 1.7rem; font-weight: 700; {c_str}">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# INTELLIGENCE VISUALIZATION LAYER
# ==========================================
c_left, c_right = st.columns([1, 1], gap="large")

with c_left:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>9-Segment RFM Architecture</h3>", unsafe_allow_html=True)
    rfm_counts = rfm_df["RFM_Segment"].value_counts().reset_index()
    rfm_counts.columns = ["RFM_Segment", "Count"]
    fig_rfm = plot_donut_chart(rfm_counts, "RFM_Segment", "Count", "")
    fig_rfm.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_rfm, use_container_width=True)

with c_right:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Lifetime Value (CLV) Distribution</h3>", unsafe_allow_html=True)
    fig_clv_dist = plot_histogram(clv_df, "Estimated_CLV", "", nbins=30)
    fig_clv_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_clv_dist, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
c_bot_left, c_bot_right = st.columns([1, 1], gap="large")

with c_bot_left:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Cohort Retention Matrix</h3>", unsafe_allow_html=True)
    if not retention_matrix.empty:
        fig_heatmap = px.imshow(
            retention_matrix,
            labels=dict(x="Months Since First Order", y="Cohort Month", color="Retention (%)"),
            x=[f"Month {col}" for col in retention_matrix.columns],
            y=retention_matrix.index,
            color_continuous_scale="blues",
            aspect="auto"
        )
        fig_heatmap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_heatmap, use_container_width=True)

with c_bot_right:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>ML Churn Risk Assessment</h3>", unsafe_allow_html=True)
    risk_counts = churn_df["Churn_Risk"].value_counts().reset_index()
    risk_counts.columns = ["Churn_Risk", "Count"]
    fig_risk = plot_donut_chart(risk_counts, "Churn_Risk", "Count", "")
    fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# CUSTOMER 360 DIGITAL TWIN PROFILE
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--accent-cyan); text-align:center;'>Digital Twin Profile Explorer</h3>", unsafe_allow_html=True)
selected_cust_id = st.selectbox("ISOLATE CUSTOMER ENTITY", customers_df["customer_id"].unique()[:200])

profile = build_customer_360_profile(selected_cust_id, customers_df, orders_df, rfm_df, clv_df, churn_df)
digital_twin = create_customer_digital_twin(profile)

col360_1, col360_2, col360_3 = st.columns(3)

with col360_1:
    st.markdown(f"""
    <div style="background: var(--surface-bg); border: 1px solid var(--border-color); padding: 1.5rem; border-radius: 8px; height: 100%;">
        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">Entity Identity</div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">Name:</span> <span style="color:var(--text-primary); font-weight:600;">{digital_twin.identity['Name']}</span></div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">Location:</span> <span style="color:var(--text-primary); font-weight:600;">{digital_twin.identity['City']}</span></div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">Classification:</span> <span style="color:var(--accent-cyan); font-weight:600;">{digital_twin.identity['Persona']}</span></div>
    </div>
    """, unsafe_allow_html=True)

with col360_2:
    st.markdown(f"""
    <div style="background: var(--surface-bg); border: 1px solid var(--border-color); padding: 1.5rem; border-radius: 8px; height: 100%;">
        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">Intelligence State</div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">RFM Matrix:</span> <span style="color:var(--text-primary); font-weight:600;">{digital_twin.rfm_intelligence['RFM_Segment']}</span></div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">Projected CLV:</span> <span style="color:var(--success); font-weight:600;">{format_currency(digital_twin.clv_intelligence['Estimated_CLV'])}</span></div>
        <div style="margin-bottom: 0.5rem;"><span style="color:var(--text-secondary);">ML Churn Risk:</span> <span style="color:var(--danger); font-weight:600;">{digital_twin.churn_intelligence['Churn_Risk']} ({digital_twin.churn_intelligence['Churn_Probability']:.2f})</span></div>
    </div>
    """, unsafe_allow_html=True)

with col360_3:
    st.markdown(f"""
    <div style="background: rgba(79, 70, 229, 0.1); border: 1px solid var(--accent-indigo); padding: 1.5rem; border-radius: 8px; height: 100%;">
        <div style="font-size: 0.75rem; color: var(--accent-indigo); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; font-weight: 600;">Next Best Action Engine</div>
        <div style="color: var(--text-primary); font-size: 0.95rem; line-height: 1.5;">{digital_twin.recommended_action}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
