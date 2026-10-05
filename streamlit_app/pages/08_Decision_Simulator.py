"""
Page 8: NovaNest Decision Simulator
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from decision_simulation.scenario_engine import run_scenario
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Decision Simulator — {PAGE_TITLE}", page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="collapsed")

apply_custom_theme()

# Hide Sidebar for cinematic feel
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
        .stSlider > div > div > div > div {
            background-color: var(--accent-cyan) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load data
data, data_source = load_all_datasets()
if "orders" not in data or "customers" not in data or "restaurants" not in data:
    st.error("Essential datasets are missing. Cannot run simulations.")
    st.stop()

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="War Game Simulator", 
        subtitle="Deterministic Business Scenario Modeling & Impact Prediction",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom: 1.5rem;'>Scenario Initialization</h3>", unsafe_allow_html=True)

# Parameter Control Module
col_params, col_results = st.columns([1, 2], gap="large")

with col_params:
    st.markdown("""
    <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <div style="color: var(--accent-cyan); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(6,182,212,0.3); padding-bottom: 0.5rem;">Parameter Control Module</div>
    """, unsafe_allow_html=True)
    
    scenario_name = st.text_input("Scenario ID", "WAR_GAME_ALPHA_01")
    
    st.markdown("<div style='font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1rem; margin-bottom: 0.5rem;'>Demand & Pricing Vectors</div>", unsafe_allow_html=True)
    demand_change_pct = st.slider("Demand Volatility (%)", -50, 100, 0)
    aov_change_pct = st.slider("AOV Adjustment (%)", -30, 50, 0)
    discount_change_pct = st.slider("Subsidy Expenditure (%)", -50, 50, 0)
    
    st.markdown("<div style='font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1rem; margin-bottom: 0.5rem;'>Customer Vectors</div>", unsafe_allow_html=True)
    retention_change_pct = st.slider("Retention Coefficient (%)", -20, 50, 0)
    churn_reduction_pct = st.slider("Churn Mitigation (%)", 0, 100, 0)
    acq_change_pct = st.slider("Acquisition Velocity (%)", -20, 100, 0)
    
    st.markdown("<div style='font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1rem; margin-bottom: 0.5rem;'>Operational Vectors</div>", unsafe_allow_html=True)
    commission_change_pct = st.slider("Partner Commission (%)", -20, 30, 0)
    delivery_fee_change_pct = st.slider("Logistics Fee (%)", -30, 100, 0)
    rider_capacity_change_pct = st.slider("Fleet Capacity (%)", -30, 100, 0)
    delivery_time_change_pct = st.slider("Transit Time Offset (%)", -30, 50, 0)
    
    st.markdown("</div>", unsafe_allow_html=True)

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
with st.spinner("Executing War Game Scenario..."):
    scenario = run_scenario(scenario_name, params, data)
results = scenario["results"]
rec = scenario["recommendation"]

with col_results:
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom: 1.5rem;'>Simulation Impact Matrix</h3>", unsafe_allow_html=True)
    
    fin = results["financial"]
    cust = results["customer"]
    ops = results["operations"]
    
    def render_impact_card(title, baseline, simulated, formatter, invert_color=False):
        delta = simulated - baseline
        delta_str = formatter(delta) if delta < 0 else f"+{formatter(delta)}"
        
        if invert_color:
            is_positive = delta <= 0
        else:
            is_positive = delta >= 0
            
        color = "var(--success)" if is_positive else "var(--danger)"
        bg_color = "rgba(16, 185, 129, 0.05)" if is_positive else "rgba(239, 68, 68, 0.05)"
        
        if delta == 0:
            color = "var(--text-secondary)"
            bg_color = "var(--surface-bg)"
            
        st.markdown(f"""
        <div style="background: {bg_color}; border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">{title}</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">{formatter(simulated)}</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: {color};">{delta_str}</div>
            </div>
            <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem;">Baseline: {formatter(baseline)}</div>
        </div>
        """, unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        render_impact_card("Platform Revenue", fin["baseline"]["Platform_Revenue"], fin["simulated"]["Platform_Revenue"], format_currency)
        render_impact_card("Profit Margin", fin["baseline"]["Profit_Margin"], fin["simulated"]["Profit_Margin"], format_percent)
    with r2:
        render_impact_card("Active Base", cust["baseline"]["Ending_Active_Base"], cust["simulated"]["Ending_Active_Base"], format_number)
        render_impact_card("Churn Rate", cust["baseline"]["Churn_Rate"], cust["simulated"]["Churn_Rate"], format_percent, invert_color=True)
    with r3:
        render_impact_card("SLA Compliance", ops["baseline"]["SLA_Compliance"], ops["simulated"]["SLA_Compliance"], format_percent)
        render_impact_card("Avg Transit Time", ops["baseline"]["Avg_ETA_Mins"], ops["simulated"]["Avg_ETA_Mins"], lambda x: f"{x:.1f}m", invert_color=True)
        
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom: 1.5rem; margin-top: 2rem;'>AI War Game Recommendation</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(79, 70, 229, 0.05); border: 1px solid rgba(79, 70, 229, 0.3); border-left: 3px solid var(--accent-indigo); border-radius: 4px 8px 8px 4px; padding: 1.5rem;">
        <div style="font-size: 0.75rem; color: var(--accent-indigo); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">VERDICT_CONFIDENCE: {rec['Confidence']}</div>
        <div style="font-size: 1.1rem; color: var(--text-primary); font-weight: 600; margin-bottom: 1rem;">{rec['Decision']}</div>
        <div style="display: flex; gap: 1.5rem;">
            <div style="flex: 1;">
                <div style="font-size: 0.75rem; color: var(--success); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">Primary Benefit</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">{rec['Expected_Benefit']}</div>
            </div>
            <div style="flex: 1;">
                <div style="font-size: 0.75rem; color: var(--danger); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">Critical Risk</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">{rec['Main_Risk']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
