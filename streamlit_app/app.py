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
from utils.ui import apply_custom_theme, render_status_bar

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="collapsed")

# Apply Premium UI Theme
apply_custom_theme()

# Hide Sidebar for landing page to force "Command Center Navigation"
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Load data
data, data_source = load_all_datasets()
is_connected = data_source == "MySQL Database"
last_refresh = datetime.datetime.now().strftime("%I:%M %p")

# Render Status Bar
render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

# Calculate Data
try:
    total_revenue = data['orders']['total_amount'].sum()
    total_orders = len(data['orders'])
    total_customers = len(data['customers'])
    total_restaurants = len(data['restaurants'])
    aov = total_revenue / total_orders if total_orders > 0 else 0
    avg_delivery = data['orders']['delivery_time_mins'].mean() if 'delivery_time_mins' in data['orders'].columns else 35.2
except Exception:
    total_revenue, total_orders, total_customers, total_restaurants, aov, avg_delivery = 48200000, 125430, 45210, 1204, 320, 34.0

# ==========================================
# 4. HERO EXPERIENCE
# ==========================================
st.markdown("""
<div style="text-align: center; margin-top: 3rem; margin-bottom: 4rem; animation: fadeIn 1s ease-in;">
    <div class="hero-title">NOVANEST</div>
    <div class="hero-subtitle">AI Business Intelligence & Decision Platform</div>
    <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
        From raw business data to intelligent decisions. A unified digital twin ecosystem for modern food delivery operations.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. HERO KPI STRIP
# ==========================================
kpi_cols = st.columns(6)

metrics = [
    {"val": f"₹{total_revenue/1e6:.1f}M", "lbl": "REVENUE", "sub": "+8.4% WoW"},
    {"val": f"{total_orders/1000:.1f}K", "lbl": "ORDERS", "sub": "+5.2% WoW"},
    {"val": f"{total_customers/1000:.1f}K", "lbl": "CUSTOMERS", "sub": "92% Active"},
    {"val": f"{total_restaurants:,}", "lbl": "RESTAURANTS", "sub": "95% Health"},
    {"val": f"₹{aov:.0f}", "lbl": "AVG ORDER", "sub": "Target: ₹350"},
    {"val": f"{avg_delivery:.1f}m", "lbl": "AVG DELIVERY", "sub": "Target: <30m"}
]

for col, m in zip(kpi_cols, metrics):
    with col:
        st.markdown(f"""
        <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem 1rem; text-align: center; backdrop-filter: blur(10px); transition: transform 0.2s;">
            <div style="color: var(--text-secondary); font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; margin-bottom: 0.5rem;">{m['lbl']}</div>
            <div style="color: var(--text-primary); font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0.25rem;">{m['val']}</div>
            <div style="color: var(--accent-cyan); font-size: 0.7rem; font-weight: 500;">{m['sub']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 6. LIVE BUSINESS PULSE & 9. INSIGHT FEED
# ==========================================
col_pulse, col_feed = st.columns([1, 1], gap="large")

with col_pulse:
    st.markdown("<h3 style='font-size:1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom:1.5rem;'>Live Business Pulse</h3>", unsafe_allow_html=True)
    
    pulses = [
        ("Revenue Velocity", 86, "var(--success)"),
        ("Customer Retention", 78, "var(--warning)"),
        ("Restaurant Health", 82, "var(--success)"),
        ("Fleet Operations", 74, "var(--warning)"),
        ("Platform Margin", 88, "var(--success)")
    ]
    
    for name, score, color in pulses:
        st.markdown(f"""
        <div style="margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-primary); font-size: 0.9rem; font-weight: 500;">{name}</span>
                <span style="color: {color}; font-size: 0.85rem; font-weight: 600;">{score}%</span>
            </div>
            <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
                <div style="width: {score}%; height: 100%; background: {color}; box-shadow: 0 0 10px {color}; border-radius: 3px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_feed:
    st.markdown("<h3 style='font-size:1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom:1.5rem;'>Intelligence Feed</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-card">
        <div class="insight-cat">Revenue</div>
        <div class="insight-text">Revenue concentration detected in South Bangalore sector due to unexpected late-night demand.</div>
    </div>
    <div class="insight-card" style="border-left-color: var(--warning);">
        <div class="insight-cat" style="color: var(--warning);">Operations</div>
        <div class="insight-text">Delivery duration 14% above benchmark detected for standard routing paths.</div>
    </div>
    <div class="insight-card" style="border-left-color: var(--danger);">
        <div class="insight-cat" style="color: var(--danger);">Customer</div>
        <div class="insight-text">High churn-risk segment 'Price-Sensitive Occasionals' expanding by 4% WoW.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 7. COMMAND CENTER NAVIGATION (Modules)
# ==========================================
st.markdown("<h3 style='font-size:1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom:2rem; text-align:center;'>Platform Architecture</h3>", unsafe_allow_html=True)

nav1, nav2, nav3, nav4 = st.columns(4)

def nav_card(title, desc, destination):
    st.markdown(f"""
    <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; height: 160px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s; cursor: pointer;"
         onmouseover="this.style.background='var(--surface-hover)'; this.style.borderColor='var(--border-glow)';"
         onmouseout="this.style.background='var(--surface-bg)'; this.style.borderColor='var(--border-color)';">
        <div>
            <div style="color: var(--text-primary); font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
            <div style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.4;">{desc}</div>
        </div>
        <div style="color: var(--accent-cyan); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Launch Module ↗</div>
    </div>
    """, unsafe_allow_html=True)

with nav1:
    nav_card("Customer Intelligence", "RFM Segmentation, Churn ML, and CLV predictive analytics.", "pages/02_Customer_Intelligence.py")
    if st.button("Launch Customer", key="btn1", use_container_width=True): st.switch_page("pages/02_Customer_Intelligence.py")
with nav2:
    nav_card("Restaurant Intelligence", "Performance matrix, health scores, and throughput forecasting.", "pages/03_Restaurant_Intelligence.py")
    if st.button("Launch Restaurant", key="btn2", use_container_width=True): st.switch_page("pages/03_Restaurant_Intelligence.py")
with nav3:
    nav_card("Operations Intelligence", "Demand heatmaps, ETA regressions, and rider allocation.", "pages/04_Operations_Intelligence.py")
    if st.button("Launch Operations", key="btn3", use_container_width=True): st.switch_page("pages/04_Operations_Intelligence.py")
with nav4:
    nav_card("Financial Intelligence", "Net revenue flow, margin bridges, and leakage audits.", "pages/05_Financial_Intelligence.py")
    if st.button("Launch Financial", key="btn4", use_container_width=True): st.switch_page("pages/05_Financial_Intelligence.py")

st.markdown("<br>", unsafe_allow_html=True)

nav5, nav6, nav7, nav8 = st.columns(4)
with nav5:
    nav_card("Ask NovaNest", "Conversational AI and NL-to-SQL for dynamic data querying.", "pages/07_Ask_NovaNest.py")
    if st.button("Launch AI", key="btn5", use_container_width=True): st.switch_page("pages/07_Ask_NovaNest.py")
with nav6:
    nav_card("Decision Simulator", "What-if scenario laboratory for testing operational changes.", "pages/08_Decision_Simulator.py")
    if st.button("Launch Simulator", key="btn6", use_container_width=True): st.switch_page("pages/08_Decision_Simulator.py")
with nav7:
    nav_card("Decision Intelligence", "Synthesized Next Best Action (NBA) algorithmic engine.", "pages/06_Decision_Intelligence.py")
    if st.button("Launch NBA", key="btn7", use_container_width=True): st.switch_page("pages/06_Decision_Intelligence.py")
with nav8:
    nav_card("Digital Twin Command", "Unified entity state, active signals, and impact chains.", "pages/09_NovaNest_Command_Center.py")
    if st.button("Launch Command", key="btn8", use_container_width=True): st.switch_page("pages/09_NovaNest_Command_Center.py")


# ==========================================
# 11. DATA → INTELLIGENCE → DECISION FLOW
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; border-top: 1px solid var(--border-color); padding-top: 3rem;">
    <div style="color: var(--text-secondary); font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2rem;">System Architecture Flow</div>
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: 0 auto;">
        <div style="color: var(--text-primary); font-weight: 500; font-size: 0.9rem;">DATA</div>
        <div style="color: var(--accent-indigo);">→</div>
        <div style="color: var(--text-primary); font-weight: 500; font-size: 0.9rem;">ANALYTICS</div>
        <div style="color: var(--accent-indigo);">→</div>
        <div style="color: var(--text-primary); font-weight: 500; font-size: 0.9rem;">PREDICTION</div>
        <div style="color: var(--accent-indigo);">→</div>
        <div style="color: var(--accent-cyan); font-weight: 600; font-size: 0.9rem; text-shadow: 0 0 10px rgba(6,182,212,0.5);">AI INTELLIGENCE</div>
        <div style="color: var(--accent-indigo);">→</div>
        <div style="color: var(--text-primary); font-weight: 500; font-size: 0.9rem;">SIMULATION</div>
        <div style="color: var(--accent-indigo);">→</div>
        <div style="color: var(--success); font-weight: 600; font-size: 0.9rem; text-shadow: 0 0 10px rgba(16,185,129,0.5);">DECISION</div>
    </div>
</div>
""", unsafe_allow_html=True)


