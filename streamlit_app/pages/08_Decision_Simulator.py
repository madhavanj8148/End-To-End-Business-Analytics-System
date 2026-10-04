"""
Page 8: NovaNest Decision Simulator
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from decision_simulation.scenario_engine import run_scenario

st.set_page_config(page_title=f"Decision Simulator — {PAGE_TITLE}", page_icon=PAGE_ICON, layout="wide")

# Load data
data, _ = load_all_datasets()
if "orders" not in data or "customers" not in data or "restaurants" not in data:
    st.error("Essential datasets are missing. Cannot run simulations.")
    st.stop()

st.title("🎛️ NovaNest Decision Simulator")
st.caption("Test business decisions before implementing them using deterministic scenario simulation.")

# Sidebar Controls
st.sidebar.header("Scenario Parameters")
st.sidebar.markdown("Adjust parameters to simulate business impact.")

scenario_name = st.sidebar.text_input("Scenario Name", "My Custom Scenario")

st.sidebar.subheader("Demand & Pricing")
demand_change_pct = st.sidebar.slider("Demand Change (%)", -50, 100, 0)
aov_change_pct = st.sidebar.slider("AOV Change (%)", -30, 50, 0)
discount_change_pct = st.sidebar.slider("Discount Spend Change (%)", -50, 50, 0)

st.sidebar.subheader("Customer")
retention_change_pct = st.sidebar.slider("Retention Improvement (%)", -20, 50, 0)
churn_reduction_pct = st.sidebar.slider("Churn Reduction (%)", 0, 100, 0)
acq_change_pct = st.sidebar.slider("Customer Acquisition (%)", -20, 100, 0)

st.sidebar.subheader("Restaurant & Operations")
commission_change_pct = st.sidebar.slider("Commission Change (%)", -20, 30, 0)
delivery_fee_change_pct = st.sidebar.slider("Delivery Fee Change (%)", -30, 100, 0)
rider_capacity_change_pct = st.sidebar.slider("Rider Capacity Change (%)", -30, 100, 0)
delivery_time_change_pct = st.sidebar.slider("Delivery Time Change (%)", -30, 50, 0)

# Build parameter dict
params = {
    "demand_change_pct": float(demand_change_pct),
    "aov_change_pct": float(aov_change_pct),
    "discount_change_pct": float(discount_change_pct),
    "retention_change_pct": float(retention_change_pct),
    "churn_reduction_pct": float(churn_reduction_pct),
    "customer_acquisition_pct": float(acq_change_pct),
    "commission_change_pct": float(commission_change_pct),
    "delivery_fee_change_pct": float(delivery_fee_change_pct),
    "rider_capacity_change_pct": float(rider_capacity_change_pct),
    "delivery_time_change_pct": float(delivery_time_change_pct)
}

# Run Scenario
scenario = run_scenario(scenario_name, params, data)
results = scenario["results"]
rec = scenario["recommendation"]

# Tabs
tabs = st.tabs([
    "Financial Impact", 
    "Customer Impact", 
    "Operations & Restaurant Impact", 
    "Decision Recommendation"
])

# Helpers
def render_delta_metric(label, baseline, simulated, formatter, invert_color=False):
    delta = simulated - baseline
    delta_str = formatter(delta) if delta < 0 else f"+{formatter(delta)}"
    # Inverse color logic: for churn, positive delta is bad (inverse=True)
    if invert_color:
        delta_color = "normal" if delta <= 0 else "inverse"
    else:
        delta_color = "normal" if delta >= 0 else "inverse"
        
    st.metric(label=f"Simulated {label}", value=formatter(simulated), delta=delta_str, delta_color=delta_color)

with tabs[0]:
    st.subheader("Financial Intelligence (What-If Analysis)")
    fin = results["financial"]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_delta_metric("Total Orders", fin["baseline"]["Orders"], fin["simulated"]["Orders"], format_number)
    with col2:
        render_delta_metric("Gross Revenue", fin["baseline"]["Gross_Revenue"], fin["simulated"]["Gross_Revenue"], format_currency)
    with col3:
        render_delta_metric("Platform Revenue", fin["baseline"]["Platform_Revenue"], fin["simulated"]["Platform_Revenue"], format_currency)
    with col4:
        render_delta_metric("Profit Margin", fin["baseline"]["Profit_Margin"], fin["simulated"]["Profit_Margin"], format_percent)
        
    st.divider()
    
    # Visual comparison chart
    st.markdown("##### Baseline vs Simulated Revenue Breakdown")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Baseline', 'Simulated'],
        y=[fin["baseline"]["Gross_Revenue"], fin["simulated"]["Gross_Revenue"]],
        name='Gross Revenue',
        marker_color='rgb(55, 83, 109)'
    ))
    fig.add_trace(go.Bar(
        x=['Baseline', 'Simulated'],
        y=[fin["baseline"]["Platform_Revenue"], fin["simulated"]["Platform_Revenue"]],
        name='Platform Revenue',
        marker_color='rgb(26, 118, 255)'
    ))
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("Customer Intelligence Impact")
    cust = results["customer"]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_delta_metric("Active Base", cust["baseline"]["Ending_Active_Base"], cust["simulated"]["Ending_Active_Base"], format_number)
    with c2:
        render_delta_metric("Churn Rate", cust["baseline"]["Churn_Rate"], cust["simulated"]["Churn_Rate"], format_percent, invert_color=True)
    with c3:
        render_delta_metric("New Acquisitions", cust["baseline"]["New_Acquisitions"], cust["simulated"]["New_Acquisitions"], format_number)

with tabs[2]:
    st.subheader("Operations & Restaurant Intelligence Impact")
    ops = results["operations"]
    rest = results["restaurant"]
    
    o1, o2, o3 = st.columns(3)
    with o1:
        render_delta_metric("Avg ETA (mins)", ops["baseline"]["Avg_ETA_Mins"], ops["simulated"]["Avg_ETA_Mins"], lambda x: f"{x:.1f}", invert_color=True)
    with o2:
        render_delta_metric("SLA Compliance", ops["baseline"]["SLA_Compliance"], ops["simulated"]["SLA_Compliance"], format_percent)
    with o3:
        render_delta_metric("Restaurant Revenue", rest["baseline"]["Total_Restaurant_Revenue"], rest["simulated"]["Total_Restaurant_Revenue"], format_currency)

with tabs[3]:
    st.subheader("AI Decision Recommendation Engine")
    
    st.info(f"**Decision:** {rec['Decision']}")
    st.success(f"**Expected Benefit:** {rec['Expected_Benefit']}")
    st.warning(f"**Main Risk:** {rec['Main_Risk']}")
    st.caption(f"*Confidence Level:* {rec['Confidence']}")
    
    st.markdown("---")
    st.markdown("*Note: All simulated values are deterministic estimates based on historical baselines and user-defined multipliers. Do not interpret as guaranteed future observations.*")
