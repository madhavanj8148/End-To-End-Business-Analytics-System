"""
NovaNest Main Application Hub
-----------------------------
AI-Powered Food Delivery Analytics, Decision Intelligence & Digital Twin Platform
"""

import sys
from pathlib import Path
import streamlit as st

# Add streamlit_app root to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.validation import get_data_quality_status
from components.sidebar import render_sidebar

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)

# Load data
data, data_source = load_all_datasets()

# Render Global Sidebar
filters = render_sidebar(data_source)

# Main Banner Header
st.title("🍔 NovaNest Analytics Platform")
st.caption("AI-Powered Food Delivery Analytics, Decision Intelligence & Digital Twin Platform")

st.markdown("""
Welcome to **NovaNest** — the central analytics engine for monitoring food delivery operations, customer purchasing behaviors, restaurant partner health, and financial performance across multi-city logistics.
""")

st.markdown("---")

# Quick Stats / System Status Grid
col1, col2, col3, col4 = st.columns(4)

quality_score, health_status, health_msg = get_data_quality_status()

with col1:
    st.metric("Total Customers", f"{len(data['customers']):,}")
with col2:
    st.metric("Active Restaurants", f"{len(data['restaurants']):,}")
with col3:
    st.metric("Processed Orders", f"{len(data['orders']):,}")
with col4:
    st.metric("Data Quality Score", f"{quality_score}/100", delta=health_status)

st.markdown("---")

# Page Navigation Cards Guide
st.markdown("### 🧭 **Explore Intelligence Modules**")

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    #### 🏢 **1. Executive Command Center**
    High-level platform KPIs, revenue & order trends, city performance benchmarks, clickstream conversion funnels, and early business warning signals.
    """)

    st.markdown("""
    #### 👥 **2. Customer Intelligence & Customer 360**
    Demographic breakdowns, persona segmentation, RFM analysis (Champions, Loyal, At Risk), and interactive Customer 360 profile exploration.
    """)

    st.markdown("""
    #### 🍽️ **3. Restaurant Intelligence & Health Score**
    Partner performance leaderboards, 2x2 revenue/order volume matrix, cuisine distribution, and rule-based Restaurant Health Scores.
    """)

with c2:
    st.markdown("""
    #### 🚚 **4. Operations Intelligence & Logistics**
    Delivery speed, distance distributions, city delivery duration benchmarks, rider performance tracking, and geographic demand heatmaps.
    """)

    st.markdown("""
    #### 💰 **5. Financial Intelligence & Unit Economics**
    Gross vs Net Revenue analysis, average order values (AOV), discount leakage, delivery fee secondary revenue, and dynamic commission platform margins.
    """)

st.markdown("---")
st.info("👈 **Use the left sidebar navigation** to select a specific Intelligence Module or apply global filters.")
