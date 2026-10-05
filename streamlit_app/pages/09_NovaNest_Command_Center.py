"""
Page 9: NovaNest Command Center
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

from digital_twin.twin_engine import build_digital_twin_state
from digital_twin.twin_dependencies import get_impact_chain
from ai.insights.business_insights import generate_business_insights
from decision.next_best_action import generate_next_best_actions
from decision_simulation.scenario_engine import run_scenario

st.set_page_config(page_title=f"Command Center — {PAGE_TITLE}", page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="collapsed")

apply_custom_theme()

# Hide Sidebar for landing page to force "Command Center Navigation"
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# 1. Load Data & Build Twin State
data, data_source = load_all_datasets()
if "orders" not in data or "customers" not in data or "restaurants" not in data:
    st.error("Essential datasets are missing. Cannot load Digital Twin.")
    st.stop()

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="NovaNest Command Center", 
        subtitle="Live Business Digital Twin & Strategy Control Room",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

with st.spinner("Initializing Analytical Business Digital Twin..."):
    twin = build_digital_twin_state(data)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# CENTRAL HEALTH ORBIT
# ==========================================
health = twin.financial_state.get("Business_Health_Score", 88)
health_color = "var(--success)" if health >= 85 else "var(--warning)" if health >= 70 else "var(--danger)"

st.markdown(f"""
<div style="text-align: center; margin-bottom: 3rem;">
    <div style="color: var(--text-secondary); letter-spacing: 0.1em; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 1rem;">Core Digital Twin State</div>
    <div style="display: inline-block; padding: 2rem; border-radius: 50%; background: radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%); border: 1px solid var(--border-glow); box-shadow: 0 0 40px rgba(6,182,212,0.1);">
        <div style="font-size: 1rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em;">Platform Health</div>
        <div style="font-size: 4.5rem; font-weight: 700; color: {health_color}; text-shadow: 0 0 20px {health_color}; line-height: 1;">{health}<span style="font-size:2rem; color:var(--text-tertiary);">/100</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

h1, h2, h3, h4 = st.columns(4)
metrics_orbit = [
    ("CUSTOMER HEALTH", "88/100", "Stable"),
    ("RESTAURANT HEALTH", "95/100", "Optimal"),
    ("OPERATIONS HEALTH", "82/100", "Alert"),
    ("FINANCIAL HEALTH", "90/100", "Stable")
]
for col, (title, val, status) in zip([h1, h2, h3, h4], metrics_orbit):
    with col:
        st.markdown(f"""
        <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-top: 2px solid var(--accent-indigo); border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="font-size: 0.75rem; color: var(--text-secondary); letter-spacing: 0.05em; text-transform: uppercase;">{title}</div>
            <div style="font-size: 1.5rem; color: var(--text-primary); font-weight: 600; margin: 0.5rem 0;">{val}</div>
            <div style="font-size: 0.75rem; color: var(--accent-cyan);">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# COMMAND CENTER PANELS
# ==========================================
col_alerts, col_ai = st.columns([1, 1], gap="large")

with col_alerts:
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary);'>Active Signals & Impact Chain</h3>", unsafe_allow_html=True)
    if not twin.alerts:
        st.markdown("<div class='insight-card'><div class='insight-text'>All systems nominal. No critical alerts detected.</div></div>", unsafe_allow_html=True)
    else:
        for alert in twin.alerts:
            bg_color = "var(--danger)" if alert["Severity"] == "Critical" else "var(--warning)" if alert["Severity"] == "High" else "var(--accent-cyan)"
            st.markdown(f"""
            <div style="background: var(--surface-bg); border-left: 3px solid {bg_color}; padding: 1.25rem; border-radius: 0 8px 8px 0; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: {bg_color}; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">[{alert['Severity']}] {alert['Entity']}</span>
                    <span style="color: var(--text-secondary); font-size: 0.7rem;">{alert['Category']}</span>
                </div>
                <div style="color: var(--text-primary); font-size: 1rem; font-weight: 500; margin-bottom: 0.5rem;">{alert['Signal']}</div>
                <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem;"><b>Impact:</b> {alert['Business_Impact']}</div>
                <div style="background: rgba(0,0,0,0.3); padding: 0.75rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-primary);">
                    <div style="color: var(--accent-indigo); font-size: 0.65rem; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Impact Chain</div>
                    {" ➔ ".join([f"<span>{step}</span>" for step in get_impact_chain("high_discount" if "Leakage" in alert["Signal"] else "demand_spike")])}
                </div>
                <div style="margin-top: 1rem; color: var(--success); font-size: 0.85rem; font-weight: 500;"><b>Action:</b> {alert['Recommended_Action']}</div>
            </div>
            """, unsafe_allow_html=True)

with col_ai:
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary);'>AI Executive Summary & Decisions</h3>", unsafe_allow_html=True)
    
    st.markdown("<div style='color: var(--text-primary); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;'>Synthesized Insights</div>", unsafe_allow_html=True)
    insights = generate_business_insights(data["orders"], data["customers"])
    for insight in insights:
        st.markdown(f"""
        <div style="background: var(--surface-bg); border: 1px solid var(--border-color); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; font-size: 0.9rem; color: var(--text-secondary);">
            <span style="color: var(--accent-cyan); margin-right: 5px;">✦</span> {insight}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><div style='color: var(--text-primary); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;'>Next Best Actions (NBA) Engine</div>", unsafe_allow_html=True)
    nbas = generate_next_best_actions(data["orders"])
    if nbas:
        for i, nba in enumerate(nbas):
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 0.75rem;">
                <div style="background: var(--accent-indigo); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 600; flex-shrink: 0;">{i+1}</div>
                <div style="color: var(--text-primary); font-size: 0.9rem; padding-top: 2px;">{nba}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: var(--text-secondary); font-size: 0.9rem;'>No critical interventions required at this time.</div>", unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# SCENARIO SIMULATION & TWIN
# ==========================================
col_sim, col_twin = st.columns([1, 1], gap="large")

with col_sim:
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary);'>Fast Scenario Simulator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;'>Preview a 10% demand increase scenario across the digital twin state.</p>", unsafe_allow_html=True)
    
    if st.button("Run Quick Simulation", use_container_width=True):
        with st.spinner("Processing through Scenario Engine..."):
            sim_res = run_scenario("Quick Snapshot", {"demand_change_pct": 10}, data)
            fin_sim = sim_res["results"]["financial"]["simulated"]
            st.markdown(f"""
            <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase;">Projected Revenue</div>
                        <div style="color: var(--text-primary); font-size: 1.5rem; font-weight: 600;">{format_currency(fin_sim['Platform_Revenue'])}</div>
                    </div>
                    <div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase;">Projected Margin</div>
                        <div style="color: var(--success); font-size: 1.5rem; font-weight: 600;">{format_percent(fin_sim['Profit_Margin'])}</div>
                    </div>
                </div>
                <div style="background: rgba(16,185,129,0.1); border-left: 2px solid var(--success); padding: 0.75rem; font-size: 0.85rem; color: var(--text-primary);">
                    <b>AI Verdict:</b> {sim_res['recommendation']['Decision']}
                </div>
            </div>
            """, unsafe_allow_html=True)

with col_twin:
    st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary);'>Digital Twin State Explorer</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;'>Inspect the raw JSON object representing the synthesized business state.</p>", unsafe_allow_html=True)
    
    with st.expander("View Raw Digital Twin JSON Object", expanded=False):
        st.json(twin.to_dict())

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
