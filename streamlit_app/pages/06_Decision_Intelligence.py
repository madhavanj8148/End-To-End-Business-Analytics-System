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
from components.kpi_cards import render_kpi_grid
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

from clv import calculate_customer_clv
from rfm import calculate_advanced_rfm
from health_score import calculate_restaurant_health_score
from risk_detection import detect_restaurant_risks
from benchmarking import calculate_restaurant_benchmarks
from next_best_action import generate_customer_next_best_actions, generate_restaurant_next_best_actions, generate_operational_next_best_actions

st.set_page_config(page_title=f"Decision Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="expanded")

apply_custom_theme()

data, data_source = load_all_datasets()
filters = render_sidebar(data_source)

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="Decision Intelligence", 
        subtitle="Automated Actionable Interventions for Customers, Partners & Logistics.",
        icon="🎯"
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=f"Updated Today, {last_refresh}")

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

kpis = [
    {"title": "CUSTOMER ACTIONS", "value": format_number(total_cust_nba), "subtext": "Triggered customer interventions"},
    {"title": "RESTAURANT ACTIONS", "value": format_number(total_rest_nba), "subtext": "Triggered partner interventions"},
    {"title": "OPERATIONS ACTIONS", "value": format_number(total_ops_nba), "subtext": "Triggered logistics interventions"},
    {"title": "HIGH PRIORITY", "value": format_number(high_priority_nba), "delta": "Requires Immediate Action", "subtext": "Critical priority interventions"},
]
render_kpi_grid(kpis, 4)

st.markdown("---")

# Filter Section
st.markdown("### 🎛️ **Action Filters**")
col_f1, col_f2 = st.columns(2)

with col_f1:
    target_filter = st.radio("Target Entity Type:", ["All", "Customer", "Restaurant", "Operations & Logistics", "Revenue Operations"], horizontal=True)

with col_f2:
    priority_filter = st.selectbox("Priority Level:", ["All", "High", "Medium", "Low"])

filtered_actions = all_actions
if target_filter != "All":
    filtered_actions = [a for a in filtered_actions if a["target_type"] == target_filter]

if priority_filter != "All":
    filtered_actions = [a for a in filtered_actions if a["priority"] == priority_filter]

st.markdown(f"#### **Displaying {len(filtered_actions)} Recommended Interventions**")

# Display Action Cards
for action in filtered_actions[:20]:
    prio = action["priority"]
    prio_badge = "🔴 High Priority" if prio == "High" else "🟠 Medium Priority" if prio == "Medium" else "🟢 Low Priority"
    entity_str = f"{action['target_type']} ID: `{action['entity_id']}`" + (f" ({action['entity_name']})" if "entity_name" in action else "")

    with st.expander(f"[{prio_badge}] {action['target_type']} Action: {entity_str}"):
        st.write(f"**Detected Condition:** {action['detected_condition']}")
        st.info(f"💡 **Recommended Action:** {action['recommended_action']}")
        st.write(f"**Business Reason:** {action['reason']}")

st.markdown("---")

st.markdown("### 📋 **DETAILED ANALYSIS**")
# Master Data Table & CSV Download
actions_df = pd.DataFrame(all_actions)
render_interactive_table(actions_df, "Next Best Actions Master Decision Table", "next_best_actions_master", key="nba_table")
