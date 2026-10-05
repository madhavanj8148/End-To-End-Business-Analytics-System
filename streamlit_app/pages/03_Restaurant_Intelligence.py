"""
Page 3: Advanced Restaurant Intelligence, Health Score, Risk Engine & ML Forecasting
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "python" / "intelligence" / "restaurant"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.charts import plot_bar_chart, plot_donut_chart, plot_histogram
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

from health_score import calculate_restaurant_health_score
from risk_detection import detect_restaurant_risks
from benchmarking import calculate_restaurant_benchmarks
from early_warning import generate_restaurant_early_warnings

st.set_page_config(page_title=f"Restaurant Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

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
        title="Restaurant Intelligence Console", 
        subtitle="Partner Health Tracking, Risk Detection & Peer Benchmarking",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

orders_df = data["orders"]
restaurants_df = data["restaurants"]
ratings_df = data["ratings_reviews"]

# Compute Phase 3 Restaurant Intelligence
health_df = calculate_restaurant_health_score(restaurants_df, orders_df, ratings_df)
risk_df = detect_restaurant_risks(health_df)
bench_df = calculate_restaurant_benchmarks(risk_df)
alerts = generate_restaurant_early_warnings(bench_df)

# Load ML Predictions if available
pred_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "engineered" / "restaurant_predictions.csv"
if pred_path.exists():
    pred_df = pd.read_csv(pred_path)
else:
    pred_df = bench_df[["restaurant_id"]].copy()
    pred_df["Predicted_Next_Month_Orders"] = 100

# ==========================================
# RESTAURANT INTELLIGENCE CONSOLE - TOP KPIs
# ==========================================
total_rest = len(restaurants_df)
avg_health = bench_df["Health_Score"].mean()
critical_count = (bench_df["Risk_Category"] == "Critical").sum()
at_risk_count = (bench_df["Risk_Category"] == "At Risk").sum()
top_percentile_count = (bench_df["Overall_Percentile"] >= 75.0).sum()

k1, k2, k3, k4, k5 = st.columns(5)
metrics_orbit = [
    ("PARTNER NETWORK", format_number(total_rest), ""),
    ("AVERAGE HEALTH", f"{avg_health:.1f}", "var(--success)"),
    ("TOP 25% PARTNERS", format_number(top_percentile_count), "var(--accent-indigo)"),
    ("ELEVATED RISK", format_number(at_risk_count), "var(--warning)"),
    ("CRITICAL STATUS", format_number(critical_count), "var(--danger)")
]
for col, (title, val, color) in zip([k1, k2, k3, k4, k5], metrics_orbit):
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
# PERFORMANCE MAP (BUBBLE CHART)
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Restaurant Performance Matrix</h3>", unsafe_allow_html=True)

# Build a performance bubble map
bench_df["Bubble_Size"] = bench_df["Health_Score"].clip(lower=10) # Prevent tiny bubbles
fig_bubble = px.scatter(
    bench_df, 
    x="Total_Revenue", 
    y="Total_Orders", 
    size="Bubble_Size",
    color="Risk_Category",
    hover_name="restaurant_name",
    hover_data={"Total_Revenue": ":$,.0f", "Total_Orders": ":,", "Health_Score": ":.1f", "Bubble_Size": False},
    color_discrete_map={"Healthy": "#10b981", "Stable": "#3b82f6", "At Risk": "#f59e0b", "Critical": "#ef4444"},
    opacity=0.8,
    log_x=True, 
    log_y=True
)
fig_bubble.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font=dict(color='#94a3b8'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Total Revenue (Log)"),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Total Orders (Log)"),
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# INTELLIGENCE VISUALIZATION LAYER
# ==========================================
c_bot_left, c_bot_right = st.columns([1, 1], gap="large")

with c_bot_left:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Partner Risk Engine Distribution</h3>", unsafe_allow_html=True)
    risk_counts = bench_df["Risk_Category"].value_counts().reset_index()
    risk_counts.columns = ["Risk_Category", "Count"]
    fig_risk = plot_donut_chart(risk_counts, "Risk_Category", "Count", "")
    fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_risk, use_container_width=True)

with c_bot_right:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Health Score Distribution Component</h3>", unsafe_allow_html=True)
    fig_health_dist = plot_histogram(bench_df, "Health_Score", "", nbins=20)
    fig_health_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_health_dist, use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# EARLY WARNING ALERT SYSTEM & ML FORECASTING
# ==========================================
col_alerts, col_pred = st.columns([1, 1], gap="large")

with col_alerts:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Active Early Warnings</h3>", unsafe_allow_html=True)
    if not alerts:
        st.markdown("<div style='color: var(--text-secondary); font-size: 0.9rem;'>No active warnings detected.</div>", unsafe_allow_html=True)
    else:
        for alert in alerts[:6]:
            severity = alert["severity"]
            bg_color = "var(--danger)" if "Critical" in severity else "var(--warning)"
            st.markdown(f"""
            <div style="background: var(--surface-bg); border-left: 3px solid {bg_color}; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <span style="color: {bg_color}; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">[{severity}] {alert['entity_name']}</span>
                    <span style="color: var(--text-secondary); font-size: 0.7rem;">{alert['city']}</span>
                </div>
                <div style="color: var(--text-primary); font-size: 0.85rem; margin-bottom: 0.5rem;">{alert['metric']}: {alert['current_value']} (Bench: {alert['benchmark']})</div>
                <div style="color: var(--accent-cyan); font-size: 0.8rem; font-weight: 500;">Action: {alert['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

with col_pred:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>ML Order Throughput Forecast (Next 30D)</h3>", unsafe_allow_html=True)
    pred_merged = bench_df.merge(pred_df[["restaurant_id", "Predicted_Next_Month_Orders"]], on="restaurant_id", how="left")
    top_pred = pred_merged.sort_values("Predicted_Next_Month_Orders", ascending=False).head(8)
    fig_pred = plot_bar_chart(top_pred, "restaurant_name", "Predicted_Next_Month_Orders", "", color_col="Predicted_Next_Month_Orders")
    fig_pred.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_pred, use_container_width=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
