"""
Page 5: Financial Intelligence & Unit Economics
-----------------------------------------------
Phase 4 upgraded with Revenue Leakage Intelligence & Subsidies Audit
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.charts import plot_line_chart, plot_bar_chart, plot_donut_chart, plot_histogram
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Financial Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

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
        title="Financial Intelligence Core", 
        subtitle="Platform P&L Analytics, Margin Performance & Revenue Leakage",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

orders_eng = data["orders_engineered"]
promotions_df = data["promotions"]
payments_df = data["payments"]
leakage_df = data.get("revenue_leakage", pd.DataFrame())

# ==========================================
# FINANCIAL P&L OVERVIEW
# ==========================================
total_gross_rev = orders_eng["order_amount"].sum() if "order_amount" in orders_eng.columns else orders_eng["final_amount"].sum()
total_discounts = orders_eng["discount_amount"].sum()
total_net_rev = orders_eng["final_amount"].sum()
total_delivery_fees = orders_eng["delivery_fee"].sum()
aov = orders_eng["final_amount"].mean() if len(orders_eng) > 0 else 0

if "estimated_profit" in orders_eng.columns:
    total_est_profit = orders_eng["estimated_profit"].sum()
else:
    total_est_profit = total_net_rev * 0.20

profit_margin_pct = (total_est_profit / total_net_rev * 100) if total_net_rev > 0 else 0

st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Global Financial Metrics</h3>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
metrics_orbit = [
    ("GROSS REVENUE (GTV)", format_currency(total_gross_rev), ""),
    ("NET REVENUE", format_currency(total_net_rev), "var(--accent-cyan)"),
    ("PLATFORM PROFIT", format_currency(total_est_profit), "var(--success)"),
    ("NET MARGIN %", format_percent(profit_margin_pct), "var(--accent-indigo)")
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

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# REVENUE LEAKAGE INTELLIGENCE
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--danger); border-bottom:1px solid rgba(239, 68, 68, 0.5); padding-bottom:0.5rem; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);'>Revenue Leakage Audit (CRITICAL)</h3>", unsafe_allow_html=True)

if not leakage_df.empty:
    total_leak_amt = leakage_df["potential_leakage_amount"].sum()
    flagged_count = len(leakage_df)
    total_orders = len(orders_eng)
    leakage_rate = (flagged_count / max(1, total_orders)) * 100
    crit_count = (leakage_df["risk_level"] == "Critical Leakage").sum()
    
    st.markdown(f"""
    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
        <div style="flex: 1; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 1.25rem; text-align: center; box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);">
            <div style="font-size: 0.65rem; color: var(--danger); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">Total Detected Leakage</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: var(--danger); text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);">{format_currency(total_leak_amt)}</div>
        </div>
        <div style="flex: 1; background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 0.65rem; color: var(--warning); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">Critical Incidents</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: var(--warning);">{format_number(crit_count)}</div>
        </div>
        <div style="flex: 1; background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 0.65rem; color: var(--text-secondary); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">Leakage Rate</div>
            <div style="font-size: 1.7rem; font-weight: 700; color: var(--text-primary);">{format_percent(leakage_rate)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        risk_counts = leakage_df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["risk_level", "count"]
        fig_risk = plot_donut_chart(risk_counts, "risk_level", "count", "")
        fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col_l2:
        leak_reasons = leakage_df.groupby("leakage_reason")["potential_leakage_amount"].sum().reset_index().sort_values("potential_leakage_amount", ascending=False).head(5)
        fig_reasons = plot_bar_chart(leak_reasons, "leakage_reason", "potential_leakage_amount", "")
        fig_reasons.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig_reasons, use_container_width=True)

else:
    st.markdown("<div style='background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success); padding: 1rem; border-radius: 0 8px 8px 0; color: var(--text-primary); font-size: 0.9rem;'>No financial revenue leakage flagged. System nominal.</div>", unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# PROFITABILITY TRENDS
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Financial & Profitability Trends</h3>", unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2, gap="large")

with col_f1:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Monthly Platform Net Revenue Trend</div>", unsafe_allow_html=True)
    if "order_datetime" in orders_eng.columns:
        orders_eng["month"] = pd.to_datetime(orders_eng["order_datetime"]).dt.strftime("%Y-%m")
        monthly_fin = orders_eng.groupby("month").agg(
            Revenue=("final_amount", "sum"),
            Profit=("estimated_profit", "sum")
        ).reset_index()

        fig_fin_trend = plot_line_chart(monthly_fin, "month", "Revenue", "")
        fig_fin_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig_fin_trend, use_container_width=True)

with col_f2:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Monthly Platform Estimated Profit Trend</div>", unsafe_allow_html=True)
    if "month" in orders_eng.columns:
        fig_profit_trend = plot_line_chart(monthly_fin, "month", "Profit", "")
        fig_profit_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
        st.plotly_chart(fig_profit_trend, use_container_width=True)

col_f3, col_f4 = st.columns(2, gap="large")

with col_f3:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Revenue Contribution by Payment Method</div>", unsafe_allow_html=True)
    payments_merged = payments_df.merge(orders_eng[["order_id", "final_amount"]], on="order_id", how="left")
    pay_rev = payments_merged.groupby("payment_method")["final_amount"].sum().reset_index()
    fig_pay = plot_donut_chart(pay_rev, "payment_method", "final_amount", "")
    fig_pay.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_pay, use_container_width=True)

with col_f4:
    st.markdown("<div style='font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;'>Order Value Distribution</div>", unsafe_allow_html=True)
    fig_aov_dist = plot_histogram(orders_eng, "final_amount", "Order Value Distribution (₹)", nbins=30)
    fig_aov_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_aov_dist, use_container_width=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
