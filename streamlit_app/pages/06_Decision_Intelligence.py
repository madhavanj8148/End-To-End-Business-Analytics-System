"""
Page 6: Decision Intelligence & Next Best Action Engine
-------------------------------------------------------
Phase 3 & Phase 4 Extended Decision Engine synthesizing Customer Retention,
Restaurant Operations, Logistics Allocation, and Revenue Leakage Interventions.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "customer"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "restaurant"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "operations"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "decision"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number
from components.sidebar import render_sidebar
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

from clv import calculate_customer_clv
from rfm import calculate_advanced_rfm
from health_score import calculate_restaurant_health_score
from risk_detection import detect_restaurant_risks
from benchmarking import calculate_restaurant_benchmarks
from next_best_action import generate_customer_next_best_actions, generate_restaurant_next_best_actions, generate_operational_next_best_actions

st.set_page_config(page_title=f"Decision Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

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
        title="AI Decision Engine", 
        subtitle="Automated Actionable Interventions & AI Verdicts",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

orders_df = data["orders"]
customers_df = data["customers"]
restaurants_df = data["restaurants"]
ratings_df = data["ratings_reviews"]
alerts_df = data.get("operational_alerts", pd.DataFrame())
leakage_df = data.get("revenue_leakage", pd.DataFrame())

# Load Churn Predictions
churn_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "engineered" / "customer_churn_predictions.csv"
churn_df = pd.read_csv(churn_path) if churn_path.exists() else customers_df[["customer_id"]].assign(Churn_Probability=0.05, Churn_Risk="Low Risk")

# Compute Intelligence & Actions
clv_df = calculate_customer_clv(orders_df, customers_df)
rfm_df = calculate_advanced_rfm(orders_df, customers_df)

health_df = calculate_restaurant_health_score(restaurants_df, orders_df, ratings_df)
risk_df = detect_restaurant_risks(health_df)
bench_df = calculate_restaurant_benchmarks(risk_df)

cust_actions = generate_customer_next_best_actions(churn_df, clv_df, rfm_df)
rest_actions = generate_restaurant_next_best_actions(risk_df, bench_df)
ops_actions = generate_operational_next_best_actions(alerts_df, leakage_df)

all_actions = cust_actions + rest_actions + ops_actions

total_cust_nba = len(cust_actions)
total_rest_nba = len(rest_actions)
total_ops_nba = len(ops_actions)
high_priority_nba = sum(1 for a in all_actions if a["priority"] == "High")

# ==========================================
# DECISION ENGINE KPIs
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Engine Execution Status</h3>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
metrics_orbit = [
    ("CUSTOMER VERDICTS", format_number(total_cust_nba), ""),
    ("PARTNER VERDICTS", format_number(total_rest_nba), "var(--accent-cyan)"),
    ("LOGISTICS VERDICTS", format_number(total_ops_nba), ""),
    ("CRITICAL APPROVALS", format_number(high_priority_nba), "var(--danger)")
]
for col, (title, val, color) in zip([k1, k2, k3, k4], metrics_orbit):
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
# ACTION QUEUE (TERMINAL VERDICTS)
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>AI Verdicts & Action Queue</h3>", unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)
with col_f1:
    target_filter = st.radio("Target Entity:", ["All", "Customer", "Restaurant", "Operations & Logistics", "Revenue Operations"], horizontal=True)
with col_f2:
    priority_filter = st.selectbox("Priority Level:", ["All", "High", "Medium", "Low"])

filtered_actions = all_actions
if target_filter != "All":
    filtered_actions = [a for a in filtered_actions if a["target_type"] == target_filter]
if priority_filter != "All":
    filtered_actions = [a for a in filtered_actions if a["priority"] == priority_filter]

st.markdown(f"<div style='font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;'>Displaying {len(filtered_actions)} verdicts requiring approval.</div>", unsafe_allow_html=True)

for action in filtered_actions[:15]:
    prio = action["priority"]
    color_map = {"High": "var(--danger)", "Medium": "var(--warning)", "Low": "var(--success)"}
    prio_color = color_map.get(prio, "var(--text-primary)")
    bg_color = f"rgba({239 if prio=='High' else 245 if prio=='Medium' else 16}, {68 if prio=='High' else 158 if prio=='Medium' else 185}, {68 if prio=='High' else 11 if prio=='Medium' else 129}, 0.05)"
    
    entity_str = f"{action['target_type'].upper()}_{action['entity_id']}" + (f" ({action['entity_name']})" if "entity_name" in action else "")
    
    st.markdown(f"""
    <div style="background: {bg_color}; border: 1px solid {prio_color}; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; font-family: 'Courier New', Courier, monospace;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 0.75rem;">
            <div style="color: {prio_color}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">[{prio} PRIORITY] VERDICT PENDING</div>
            <div style="color: var(--text-secondary); font-size: 0.7rem;">TARGET: {entity_str}</div>
        </div>
        
        <div style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.25rem;">> ANALYSIS_CONDITION:</div>
        <div style="color: var(--text-primary); font-size: 0.9rem; margin-bottom: 0.75rem; font-weight: 500;">{action['detected_condition']}</div>
        
        <div style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.25rem;">> RATIONALE:</div>
        <div style="color: var(--text-primary); font-size: 0.85rem; margin-bottom: 1rem;">{action['reason']}</div>
        
        <div style="background: rgba(0,0,0,0.5); padding: 0.75rem; border-left: 3px solid var(--accent-cyan); border-radius: 4px;">
            <div style="color: var(--accent-cyan); font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">$ execute_action --force</div>
            <div style="color: var(--text-primary); font-size: 0.95rem; font-weight: 700;">{action['recommended_action']}</div>
        </div>
        
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <div style="padding: 0.4rem 1rem; background: var(--accent-indigo); color: white; border-radius: 4px; font-size: 0.75rem; font-weight: 600; cursor: pointer;">[A] APPROVE</div>
            <div style="padding: 0.4rem 1rem; background: transparent; border: 1px solid var(--text-secondary); color: var(--text-secondary); border-radius: 4px; font-size: 0.75rem; font-weight: 600; cursor: pointer;">[D] DECLINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
