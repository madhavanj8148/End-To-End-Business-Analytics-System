"""
Page 9: NovaNest Command Center
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent

from digital_twin.twin_engine import build_digital_twin_state
from digital_twin.twin_dependencies import get_impact_chain
from ai.insights.business_insights import generate_business_insights
from decision.next_best_action import generate_next_best_actions
from decision_simulation.scenario_engine import run_scenario

st.set_page_config(page_title=f"Command Center — {PAGE_TITLE}", page_icon=PAGE_ICON, layout="wide")

st.title("🌐 NovaNest Command Center")
st.caption("Unified Business Intelligence, AI & Decision Intelligence Platform")

# 1. Load Data & Build Twin State
data, _ = load_all_datasets()
if "orders" not in data or "customers" not in data or "restaurants" not in data:
    st.error("Essential datasets are missing. Cannot load Digital Twin.")
    st.stop()

with st.spinner("Initializing Analytical Business Digital Twin..."):
    twin = build_digital_twin_state(data)

# 2. Business Health Score
st.markdown("---")
health = twin.financial_state.get("Business_Health_Score", 100)
health_color = "green" if health >= 85 else "orange" if health >= 70 else "red"
st.markdown(f"### 🛡️ Overall Business Health Score: <span style='color:{health_color}'>{health}/100</span>", unsafe_allow_html=True)
st.progress(health / 100.0)

# 3. Top KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Customers", format_number(twin.customer_state["Active_Customers"]))
c2.metric("Total Orders", format_number(twin.operations_state["Total_Orders"]))
c3.metric("Gross Revenue", format_currency(twin.financial_state["Gross_Revenue"]))
c4.metric("Profit Margin", format_percent(twin.financial_state["Profit_Margin"]))

st.markdown("---")

# 4. Layout
tab_alerts, tab_ai, tab_nba, tab_sim, tab_explorer = st.tabs([
    "🚨 Executive Alert Center", 
    "🧠 AI Insights (What's happening?)", 
    "💡 Next Best Actions", 
    "🎛️ Scenario Snapshot", 
    "🔍 Twin Entity Explorer"
])

# Tab 1: Alerts & Impact Chain
with tab_alerts:
    st.subheader("Executive Alert Center")
    if not twin.alerts:
        st.success("No active critical alerts.")
    else:
        for alert in twin.alerts:
            color = "red" if alert["Severity"] == "Critical" else "orange" if alert["Severity"] == "High" else "blue"
            with st.expander(f"⚠️ [{alert['Severity']}] {alert['Signal']} ({alert['Category']})"):
                st.write(f"**Entity:** {alert['Entity']}")
                st.write(f"**Business Impact:** {alert['Business_Impact']}")
                st.write(f"**Recommended Action:** {alert['Recommended_Action']}")
                
                # Impact Chain
                st.markdown("#### 🔗 Impact Chain Analysis")
                event_type = "high_discount" if "Leakage" in alert["Signal"] else "demand_spike"
                chain = get_impact_chain(event_type)
                st.markdown(" ➔ ".join([f"`{step}`" for step in chain]))

# Tab 2: AI Executive Summary
with tab_ai:
    st.subheader("AI Executive Summary")
    insights = generate_business_insights(data["orders"], data["customers"])
    for insight in insights:
        st.info(insight)

# Tab 3: Next Best Actions
with tab_nba:
    st.subheader("Next Best Actions")
    nbas = generate_next_best_actions(data["orders"]) # Assume it generates a list
    if nbas:
        for nba in nbas:
            st.success(f"**Action:** {nba}")
    else:
        st.write("No critical interventions required at this time.")

# Tab 4: Scenario Snapshot
with tab_sim:
    st.subheader("Quick Scenario Snapshot")
    st.write("Preview a 10% demand increase scenario.")
    if st.button("Run Quick Simulation"):
        with st.spinner("Simulating..."):
            sim_res = run_scenario("Quick Snapshot", {"demand_change_pct": 10}, data)
            fin_sim = sim_res["results"]["financial"]["simulated"]
            st.metric("Projected Platform Revenue", format_currency(fin_sim["Platform_Revenue"]))
            st.metric("Projected Profit Margin", format_percent(fin_sim["Profit_Margin"]))
            st.write(f"**AI Recommendation:** {sim_res['recommendation']['Decision']}")

# Tab 5: Entity Explorer
with tab_explorer:
    st.subheader("Digital Twin Entity Explorer")
    entity_type = st.selectbox("Select Entity Type", ["Platform", "Customer", "Restaurant"])
    if entity_type == "Platform":
        st.json(twin.to_dict())
    else:
        st.write(f"Explore detailed {entity_type} twin signals. (Integrates with Phase 3 Customer 360 / Restaurant Intelligence).")
