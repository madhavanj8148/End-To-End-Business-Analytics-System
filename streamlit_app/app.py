"""
NovaNest Main Application Hub
-----------------------------
AI-Powered Food Delivery Analytics, Decision Intelligence & Digital Twin Platform
"""

import sys
from pathlib import Path
import streamlit as st
import datetime

# Add streamlit_app root to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.validation import get_data_quality_status
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_grid
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="expanded")

# Apply Premium UI Theme
apply_custom_theme()

# Load data
data, data_source = load_all_datasets()

# Render Global Sidebar
filters = render_sidebar(data_source)

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="Business Analytics & Decision Intelligence", 
        subtitle="Transform operational data into actionable business decisions.",
        icon="🍔"
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=f"Updated Today, {last_refresh}")

st.markdown("---")

# Calculate Top-Level KPIs from data if available, else placeholders
try:
    total_revenue = data['orders']['total_amount'].sum()
    total_orders = len(data['orders'])
    total_customers = len(data['customers'])
    total_restaurants = len(data['restaurants'])
    aov = total_revenue / total_orders if total_orders > 0 else 0
    avg_delivery = data['orders']['delivery_time_mins'].mean() if 'delivery_time_mins' in data['orders'].columns else 35.2
    
    kpis = [
        {"title": "REVENUE", "value": f"₹{total_revenue/1e6:.2f}M", "delta": "+8.4%", "subtext": "vs previous period"},
        {"title": "ORDERS", "value": f"{total_orders:,}", "delta": "+5.2%", "subtext": "vs previous period"},
        {"title": "CUSTOMERS", "value": f"{total_customers:,}", "delta": "+12.1%", "subtext": "Active this month"},
        {"title": "RESTAURANTS", "value": f"{total_restaurants:,}", "delta": "+2.4%", "subtext": "Onboarded partners"},
        {"title": "AVG ORDER VALUE", "value": f"₹{aov:.0f}", "delta": "-1.2%", "subtext": "Target: ₹350"},
        {"title": "AVG DELIVERY TIME", "value": f"{avg_delivery:.1f}m", "delta": "-2.1m", "subtext": "Target: <30m"}
    ]
except Exception as e:
    # Fallback if datasets are missing/empty
    kpis = [
        {"title": "REVENUE", "value": "₹48.2M", "delta": "+8.4%", "subtext": "vs previous period"},
        {"title": "ORDERS", "value": "125,430", "delta": "+5.2%", "subtext": "vs previous period"},
        {"title": "CUSTOMERS", "value": "45,210", "delta": "+12.1%", "subtext": "Active this month"},
        {"title": "RESTAURANTS", "value": "1,204", "delta": "+2.4%", "subtext": "Onboarded partners"},
        {"title": "AVG ORDER VALUE", "value": "₹320", "delta": "-1.2%", "subtext": "Target: ₹350"},
        {"title": "AVG DELIVERY TIME", "value": "34m", "delta": "-2.1m", "subtext": "Target: <30m"}
    ]

# Render KPIs
render_kpi_grid(kpis, cols_count=3)

st.markdown("---")

# Business Health Section
st.markdown("### 🏢 **BUSINESS HEALTH**")
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns(5)
with hcol1:
    st.metric("Revenue Health", "92/100", "Stable")
with hcol2:
    st.metric("Customer Health", "88/100", "Warning: Churn")
with hcol3:
    st.metric("Restaurant Health", "95/100", "Optimal")
with hcol4:
    st.metric("Operations Health", "82/100", "Alert: Delays")
with hcol5:
    st.metric("Financial Health", "90/100", "Stable Margin")

st.markdown("---")

# Today's Business Signals
st.markdown("### 📡 **TODAY'S BUSINESS SIGNALS**")
signal_cols = st.columns(3)
with signal_cols[0]:
    st.error("🚨 **High Churn Risk Detected**\n\n12% of 'At Risk' segment showing inactivity in Bangalore.")
with signal_cols[1]:
    st.warning("⚠️ **Delivery Delay Spike**\n\nAverage delivery times in Chennai South increased by 8 mins due to weather.")
with signal_cols[2]:
    st.success("📈 **Revenue Target Exceeded**\n\nWeekend promotion drove 15% higher order volume than baseline.")

st.markdown("---")

# Quick Decisions Section
st.markdown("### ⚡ **WHAT WOULD YOU LIKE TO ANALYZE?**")
nav_cols = st.columns(3)

with nav_cols[0]:
    if st.button("📊 Analyze Customers", use_container_width=True):
        st.switch_page("pages/02_Customer_Intelligence.py")
    if st.button("🍽️ Analyze Restaurants", use_container_width=True):
        st.switch_page("pages/03_Restaurant_Intelligence.py")
        
with nav_cols[1]:
    if st.button("🚚 Analyze Operations", use_container_width=True):
        st.switch_page("pages/04_Operations_Intelligence.py")
    if st.button("💰 Analyze Financials", use_container_width=True):
        st.switch_page("pages/05_Financial_Intelligence.py")
        
with nav_cols[2]:
    if st.button("🤖 Ask NovaNest AI", use_container_width=True):
        st.switch_page("pages/07_Ask_NovaNest.py")
    if st.button("🔮 Run Scenario Simulation", use_container_width=True):
        st.switch_page("pages/08_Decision_Simulator.py")

