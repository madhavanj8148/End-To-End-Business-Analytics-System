"""
Page 1: Executive Command Center
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.charts import (
    plot_line_chart, plot_bar_chart, plot_donut_chart, plot_funnel_chart, plot_histogram
)
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Executive Command Center — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

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
        title="Executive Mission Control", 
        subtitle="Global Platform KPIs & Financial Command",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

# Filtered data
orders_df = data["orders"]
customers_df = data["customers"]
restaurants_df = data["restaurants"]
deliveries_df = data["deliveries"]
events_df = data["app_events"]
ratings_df = data["ratings_reviews"]

# 1. Executive Metrics Calculation
total_cust = len(customers_df)
total_rest = len(restaurants_df)
total_orders = len(orders_df)
total_rev = orders_df["final_amount"].sum()
aov = orders_df["final_amount"].mean() if total_orders > 0 else 0
total_delivery_fees = orders_df["delivery_fee"].sum()
avg_delivery_time = deliveries_df["delivery_duration"].mean() if len(deliveries_df) > 0 else 0

# Retention Rate
repeat_cust = orders_df.groupby("customer_id").size()
retention_rate = (repeat_cust[repeat_cust > 1].count() / len(repeat_cust) * 100) if len(repeat_cust) > 0 else 0

# Cancellation Rate
cancellations = (orders_df["order_status"] == "Cancelled").sum()
cancellation_rate = (cancellations / total_orders * 100) if total_orders > 0 else 0

# Avg Rating
avg_rating = ratings_df["restaurant_rating"].mean() if len(ratings_df) > 0 else 0

# ==========================================
# EXECUTIVE METRICS ORBIT
# ==========================================

# Massive Glowing Revenue Metric
st.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="color: var(--text-secondary); letter-spacing: 0.1em; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 1rem;">Platform Gross Revenue</div>
    <div style="display: inline-block; padding: 2rem 4rem; border-radius: 12px; background: linear-gradient(145deg, rgba(79, 70, 229, 0.1), rgba(6, 182, 212, 0.05)); border: 1px solid var(--border-glow); box-shadow: 0 0 30px rgba(79, 70, 229, 0.2);">
        <div style="font-size: 4rem; font-weight: 700; color: var(--accent-cyan); text-shadow: 0 0 15px rgba(6,182,212,0.5); line-height: 1;">{format_currency(total_rev)}</div>
        <div style="color: var(--success); font-size: 1rem; margin-top: 0.5rem; font-weight: 500;">▲ 8.4% vs Previous Period</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Secondary Core KPIs
k1, k2, k3, k4 = st.columns(4)
metrics_orbit = [
    ("PLATFORM ORDERS", format_number(total_orders), "var(--accent-indigo)"),
    ("AVERAGE ORDER VALUE", format_currency(aov), "var(--text-primary)"),
    ("USER RETENTION", format_percent(retention_rate), "var(--success)"),
    ("ACTIVE PARTNERS", format_number(total_rest), "var(--accent-cyan)")
]
for col, (title, val, color) in zip([k1, k2, k3, k4], metrics_orbit):
    with col:
        c_str = f"color: {color};"
        border_top = f"border-top: 2px solid {color};"
        st.markdown(f"""
        <div style="background: var(--surface-bg); border: 1px solid var(--border-color); {border_top} border-radius: 8px; padding: 1.25rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="font-size: 0.65rem; color: var(--text-secondary); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">{title}</div>
            <div style="font-size: 1.5rem; font-weight: 600; {c_str}">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# LIVE BUSINESS SIGNALS (ALERTS)
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Live Business Intelligence Signals</h3>", unsafe_allow_html=True)

sig_col1, sig_col2, sig_col3 = st.columns(3)

# Signal 1: Cancellation
with sig_col1:
    if cancellation_rate > 3.5:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--danger); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--danger); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Critical] Operations Alert</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">Order Cancellation Rate elevated at {cancellation_rate:.2f}% (Threshold: 3.5%).</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--success); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Nominal] Operations Signal</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">Healthy Order Cancellation Rate at {cancellation_rate:.2f}%.</div>
        </div>
        """, unsafe_allow_html=True)

# Signal 2: Delivery Speed
with sig_col2:
    if avg_delivery_time > 35:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--warning); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--warning); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Warning] SLA Breach Risk</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">Fleet average delivery is {avg_delivery_time:.1f}m. Target is <35m.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--success); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Nominal] SLA Signal</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">Fleet speed optimal at {avg_delivery_time:.1f}m average.</div>
        </div>
        """, unsafe_allow_html=True)

# Signal 3: Partner Quality
with sig_col3:
    low_rated_rest = (restaurants_df["avg_rating"] < 3.8).sum()
    if low_rated_rest > 0:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--warning); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--warning); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Warning] Partner Quality</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">{low_rated_rest} partners operating below 3.8 average rating.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success); padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="color: var(--success); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">[Nominal] Partner Quality</div>
            <div style="color: var(--text-primary); font-size: 0.9rem;">Network maintaining high rating standards.</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# PERFORMANCE TRENDS
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Platform Analytics Matrix</h3>", unsafe_allow_html=True)

col_v1, col_v2 = st.columns(2, gap="large")

with col_v1:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Financial Growth Velocity</div>", unsafe_allow_html=True)
    if "order_datetime" in orders_df.columns:
        orders_df["month"] = pd.to_datetime(orders_df["order_datetime"]).dt.strftime("%Y-%m")
        monthly_rev = orders_df.groupby("month")["final_amount"].sum().reset_index()
        fig_rev = plot_line_chart(monthly_rev, "month", "final_amount", "")
        fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig_rev, use_container_width=True)

with col_v2:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Regional Revenue Contribution</div>", unsafe_allow_html=True)
    city_rev = orders_df.groupby("city")["final_amount"].sum().reset_index().sort_values("final_amount", ascending=False)
    fig_city = plot_bar_chart(city_rev, "city", "final_amount", "")
    fig_city.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_city, use_container_width=True)

col_v3, col_v4 = st.columns(2, gap="large")

with col_v3:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>User Acquisition Funnel</div>", unsafe_allow_html=True)
    funnel_order = ["App Open", "Restaurant View", "Menu View", "Add To Cart", "Checkout", "Order Complete"]
    funnel_counts = events_df["event_type"].value_counts().reindex(funnel_order).reset_index()
    funnel_counts.columns = ["event_type", "total_events"]
    fig_funnel = plot_funnel_chart(funnel_counts, "event_type", "total_events", "")
    fig_funnel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_v4:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Customer Portfolio</div>", unsafe_allow_html=True)
    persona_counts = customers_df["persona"].value_counts().reset_index()
    persona_counts.columns = ["persona", "count"]
    fig_persona = plot_donut_chart(persona_counts, "persona", "count", "")
    fig_persona.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_persona, use_container_width=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)

