"""
Page 4: Operations & Predictive Intelligence Platform
------------------------------------------------------
Phase 4 Operations Intelligence covering Future Demand Prediction, City Demand Heatmaps,
Delivery ETA Intelligence, Smart Rider Allocation, Rider Workload Analytics,
Operational Anomaly Detection, and Operational Early Warnings.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.charts import plot_bar_chart, plot_donut_chart, plot_histogram, plot_line_chart
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Operations & Predictive Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

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
        title="Operations Dispatch Console", 
        subtitle="Live Supply Chain Logistics & Fleet Optimization Radar",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

orders_df = data["orders"]
deliveries_df = data["deliveries"]
riders_df = data["riders"]
customers_df = data["customers"]
restaurants_df = data["restaurants"]

demand_forecasts_df = data.get("demand_forecasts", pd.DataFrame())
demand_heatmap_df = data.get("demand_heatmap", pd.DataFrame())
eta_predictions_df = data.get("eta_predictions", pd.DataFrame())
rider_allocation_df = data.get("rider_allocation", pd.DataFrame())
anomalies_df = data.get("operational_anomalies", pd.DataFrame())
alerts_df = data.get("operational_alerts", pd.DataFrame())

# ==========================================
# OPERATIONS INTELLIGENCE CONSOLE - TOP KPIs
# ==========================================
total_deliveries = len(deliveries_df)
avg_duration = deliveries_df["delivery_duration"].mean() if total_deliveries > 0 else 0
avg_distance = deliveries_df["distance_km"].mean() if total_deliveries > 0 else 0
ontime_count = (deliveries_df["delivery_duration"] <= 45).sum()
ontime_rate = (ontime_count / total_deliveries * 100) if total_deliveries > 0 else 0
active_riders = len(riders_df)

k1, k2, k3, k4, k5 = st.columns(5)
metrics_orbit = [
    ("FLEET DISPATCHED", format_number(total_deliveries), ""),
    ("ACTIVE DRIVERS", format_number(active_riders), "var(--accent-cyan)"),
    ("AVG TRANSIT TIME", f"{avg_duration:.1f}m", "var(--success)"),
    ("ON-TIME RATE", format_percent(ontime_rate), "var(--accent-indigo)"),
    ("LOGISTICS BOTTLENECKS", format_number(len(anomalies_df)) if not anomalies_df.empty else "0", "var(--warning)" if (not anomalies_df.empty and len(anomalies_df) > 0) else "var(--success)")
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
# LIVE DISPATCH RADAR
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Live Dispatch Radar (Distance vs. Duration)</h3>", unsafe_allow_html=True)

if not deliveries_df.empty:
    deliveries_df["Delivery_Status"] = np.where(deliveries_df["delivery_duration"] > 45, "Delayed", "On-Time")
    
    fig_radar = px.scatter(
        deliveries_df.head(1000), 
        x="distance_km", 
        y="delivery_duration", 
        color="Delivery_Status",
        color_discrete_map={"On-Time": "#10b981", "Delayed": "#ef4444"},
        hover_data=["delivery_id", "rider_id"],
        opacity=0.6,
        size_max=8
    )
    fig_radar.add_shape(
        type="line", line=dict(dash="dash", color="#f59e0b", width=2),
        x0=0, x1=deliveries_df["distance_km"].max(), y0=45, y1=45,
    )
    fig_radar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#94a3b8'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Distance (km)", zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Delivery Duration (mins)", zerolinecolor='rgba(255,255,255,0.1)'),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.warning("Delivery radar offline. Insufficient data.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SUPPLY CHAIN HEATMAP & FORECASTS
# ==========================================
c_mid_left, c_mid_right = st.columns([1, 1], gap="large")

with c_mid_left:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Supply Chain Heatmap (Orders by City & Day)</h3>", unsafe_allow_html=True)
    merged_city = orders_df.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")
    merged_city["day_of_week"] = pd.to_datetime(merged_city["order_datetime"]).dt.day_name()
    heatmap_dw = merged_city.groupby(["city", "day_of_week"]).size().unstack(fill_value=0)
    
    fig_heat = px.imshow(
        heatmap_dw,
        color_continuous_scale="magma",
        aspect="auto"
    )
    fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

with c_mid_right:
    st.markdown("<h3 style='font-size:0.9rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Fleet Workload Distribution</h3>", unsafe_allow_html=True)
    rider_perf = deliveries_df.groupby("rider_id").agg(Total_Deliveries=("delivery_id", "count")).reset_index()
    mean_load = rider_perf["Total_Deliveries"].mean()
    rider_perf["Workload_Status"] = rider_perf["Total_Deliveries"].apply(
        lambda n: "Overloaded" if n > mean_load * 1.3 else ("Underutilized" if n < mean_load * 0.7 else "Optimal")
    )
    wk_counts = rider_perf["Workload_Status"].value_counts().reset_index()
    wk_counts.columns = ["Workload_Status", "count"]
    
    fig_wk = plot_donut_chart(wk_counts, "Workload_Status", "count", "")
    fig_wk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
    st.plotly_chart(fig_wk, use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# ==========================================
# EARLY WARNING & LOGISTICS BOTTLENECKS
# ==========================================
st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;'>Logistics Command Alerts</h3>", unsafe_allow_html=True)

if not alerts_df.empty:
    col_alerts1, col_alerts2 = st.columns(2)
    cols = [col_alerts1, col_alerts2]
    
    for i, (_, alert) in enumerate(alerts_df.iterrows()):
        sev = alert.get("Severity", "Healthy")
        bg_color = "var(--danger)" if "Critical" in sev else ("var(--warning)" if "Warning" in sev else "var(--success)")
        
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background: var(--surface-bg); border-left: 3px solid {bg_color}; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <span style="color: {bg_color}; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">[{sev}] {alert.get('Entity')}</span>
                    <span style="color: var(--text-secondary); font-size: 0.7rem;">{alert.get('Category')}</span>
                </div>
                <div style="color: var(--text-primary); font-size: 0.85rem; margin-bottom: 0.5rem;">{alert.get('Metric')} = {alert.get('Current_Value')} (Threshold: {alert.get('Threshold')})</div>
                <div style="color: var(--accent-cyan); font-size: 0.8rem; font-weight: 500;">Action: {alert.get('Recommended_Action')}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("<div style='color: var(--text-secondary); font-size: 0.9rem;'>All logistics and dispatch systems are operating nominally.</div>", unsafe_allow_html=True)

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
