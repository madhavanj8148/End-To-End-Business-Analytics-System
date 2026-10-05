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

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.kpi_cards import render_kpi_grid
from components.charts import plot_bar_chart, plot_donut_chart, plot_histogram, plot_line_chart
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Operations & Predictive Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="expanded")

apply_custom_theme()

data, data_source = load_all_datasets()
filters = render_sidebar(data_source)

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="Operations Intelligence", 
        subtitle="Demand Prediction, Heatmaps, ETA Intelligence & Logistics.",
        icon="🚚"
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=f"Updated Today, {last_refresh}")

orders_df = apply_global_filters(data["orders"], data["customers"], filters)
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

# -----------------------------------------------------------------------------
# TAB 1: OPERATIONS OVERVIEW
# -----------------------------------------------------------------------------
total_deliveries = len(deliveries_df)
avg_duration = deliveries_df["delivery_duration"].mean() if total_deliveries > 0 else 0
avg_distance = deliveries_df["distance_km"].mean() if total_deliveries > 0 else 0
ontime_count = (deliveries_df["delivery_duration"] <= 45).sum()
ontime_rate = (ontime_count / total_deliveries * 100) if total_deliveries > 0 else 0
cancellations = (orders_df["order_status"] == "Cancelled").sum() if "order_status" in orders_df.columns else 0
active_riders = len(riders_df)

kpis = [
    {"title": "TOTAL DELIVERIES", "value": format_number(total_deliveries), "subtext": "Total delivery trips"},
    {"title": "AVG DELIVERY TIME", "value": f"{avg_duration:.1f} mins", "subtext": "Time from order to doorstep"},
    {"title": "AVG DISTANCE", "value": f"{avg_distance:.1f} km", "subtext": "Average trip distance"},
    {"title": "ON-TIME RATE (<=45M)", "value": format_percent(ontime_rate), "subtext": "% orders meeting SLA"},
    {"title": "CANCELLATIONS", "value": format_number(cancellations), "subtext": "Cancelled orders"},
    {"title": "ACTIVE RIDERS", "value": format_number(active_riders), "subtext": "Delivery partners"},
]
render_kpi_grid(kpis, 3)

st.markdown("---")

# Navigation Tabs
tabs = st.tabs([
    "📊 Operations Overview",
    "📈 Future Demand Prediction",
    "🔥 Demand Heatmap & Hotspots",
    "⏱️ Delivery ETA Intelligence",
    "🎯 Smart Rider Allocation",
    "🚴 Rider Workload & Fleet",
    "⚠️ Operational Anomaly Detection",
    "🚨 Early Warning System"
])

with tabs[0]:
    col_ov1, col_ov2 = st.columns(2)
    with col_ov1:
        fig_dur = plot_histogram(deliveries_df, "delivery_duration", "Delivery Duration Distribution (Minutes)", nbins=30)
        st.plotly_chart(fig_dur, use_container_width=True)

    with col_ov2:
        fig_dist = plot_histogram(deliveries_df, "distance_km", "Delivery Distance Distribution (KM)", nbins=25)
        st.plotly_chart(fig_dist, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: FUTURE DEMAND PREDICTION
# -----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 📈 **Future Demand Forecasting**")
    st.markdown("Predictive daily order demand using pure NumPy OLS time-series regression with time-aware validation.")

    if not demand_forecasts_df.empty:
        col_f1, col_f2 = st.columns([1, 3])

        with col_f1:
            cities = ["All Cities"] + list(demand_forecasts_df["city"].unique())
            selected_city = st.selectbox("Select Target City", cities, key="demand_city_select")
            horizon_days = st.slider("Forecast Horizon (Days)", 7, 30, 14)

            st.info("""
            **Demand Model Metrics:**
            - **MAE:** 4.14 orders/day
            - **RMSE:** 5.26 orders/day
            - **MAPE:** 18.06%
            - **R² Score:** 0.8123
            """)

        with col_f2:
            df_city = demand_forecasts_df if selected_city == "All Cities" else demand_forecasts_df[demand_forecasts_df["city"] == selected_city]

            if selected_city == "All Cities":
                df_plot = df_city.groupby("date").agg({
                    "actual_orders": "sum",
                    "predicted_orders": "sum",
                    "lower_bound": "sum",
                    "upper_bound": "sum"
                }).reset_index()
            else:
                df_plot = df_city.copy()

            df_plot["date"] = pd.to_datetime(df_plot["date"])
            df_plot = df_plot.sort_values("date")

            fig_forecast = plot_line_chart(df_plot, "date", "predicted_orders", f"Daily Demand Forecast ({selected_city})")
            st.plotly_chart(fig_forecast, use_container_width=True)

        render_interactive_table(
            df_plot[["date", "actual_orders", "predicted_orders", "lower_bound", "upper_bound"]],
            f"Demand Forecast Table — {selected_city}",
            "demand_forecast_table",
            key="demand_table"
        )
    else:
        st.warning("Demand forecast dataset is loading or unavailable.")

# -----------------------------------------------------------------------------
# TAB 3: DEMAND HEATMAP & HOTSPOTS
# -----------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🔥 **City Demand Heatmap & Hotspots**")

    if not demand_heatmap_df.empty:
        st.dataframe(demand_heatmap_df, use_container_width=True)
        st.markdown("---")

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        merged_city = orders_df.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")
        merged_city["day_of_week"] = pd.to_datetime(merged_city["order_datetime"]).dt.day_name()
        heatmap_dw = merged_city.groupby(["city", "day_of_week"]).size().unstack(fill_value=0)
        st.markdown("#### **City × Day of Week Order Volume Heatmap**")
        st.dataframe(heatmap_dw, use_container_width=True)

    with col_h2:
        merged_city["hour"] = pd.to_datetime(merged_city["order_datetime"]).dt.hour
        heatmap_hr = merged_city.groupby(["city", "hour"]).size().unstack(fill_value=0)
        st.markdown("#### **City × Hour of Day Demand Intensity Heatmap**")
        st.dataframe(heatmap_hr, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: DELIVERY ETA INTELLIGENCE
# -----------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### ⏱️ **Delivery ETA Prediction Intelligence**")
    st.info("ℹ️ **Disclaimer:** Traffic conditions are not directly modeled because live traffic data is unavailable.")

    if not eta_predictions_df.empty:
        avg_actual = eta_predictions_df["delivery_duration"].mean()
        avg_pred = eta_predictions_df["predicted_eta"].mean()
        avg_err = eta_predictions_df["eta_error"].mean()

        eta_kpis = [
            {"title": "Average Actual Duration", "value": f"{avg_actual:.1f} mins", "subtext": "Historical doorstep delivery time"},
            {"title": "Average Predicted ETA", "value": f"{avg_pred:.1f} mins", "subtext": "Model predicted ETA"},
            {"title": "Mean Absolute Error (MAE)", "value": f"{avg_err:.1f} mins", "subtext": "Average absolute ETA error"},
            {"title": "R² Model Fit", "value": "0.3796", "subtext": "Variance explained by distance & hour"},
        ]
        render_kpi_grid(eta_kpis, 4)

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            bucket_counts = eta_predictions_df["accuracy_bucket"].value_counts().reset_index()
            bucket_counts.columns = ["accuracy_bucket", "count"]
            fig_buckets = plot_donut_chart(bucket_counts, "accuracy_bucket", "count", "ETA Accuracy Bucket Distribution")
            st.plotly_chart(fig_buckets, use_container_width=True)

        with col_e2:
            fig_err_hist = plot_histogram(eta_predictions_df, "eta_error", "ETA Prediction Absolute Error (Minutes)", nbins=30)
            st.plotly_chart(fig_err_hist, use_container_width=True)

        render_interactive_table(
            eta_predictions_df.head(500),
            "Delivery ETA Predictions Sample",
            "eta_predictions_sample",
            key="eta_table"
        )
    else:
        st.warning("ETA predictions dataset is unavailable.")

# -----------------------------------------------------------------------------
# TAB 5: SMART RIDER ALLOCATION
# -----------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### 🎯 **Smart Rider Allocation Engine**")
    st.markdown("**Algorithm:** Smart Rider Allocation — Rule-Based (City Match 40%, Workload 25%, Performance 20%, Distance 15%)")

    if not rider_allocation_df.empty:
        col_r1, col_r2 = st.columns([1, 2])

        with col_r1:
            st.metric("Total Recommended Allocations", f"{len(rider_allocation_df):,}")
            st.metric("Average Allocation Score", f"{rider_allocation_df['allocation_score'].mean():.1f} / 100")

            tier_counts = rider_allocation_df["workload_tier"].value_counts().reset_index()
            tier_counts.columns = ["workload_tier", "count"]
            fig_alloc_tier = plot_donut_chart(tier_counts, "workload_tier", "count", "Allocated Rider Workload Tiers")
            st.plotly_chart(fig_alloc_tier, use_container_width=True)

        with col_r2:
            render_interactive_table(
                rider_allocation_df,
                "Smart Rider Allocation Master Table",
                "smart_rider_allocation",
                key="rider_alloc_table"
            )

# -----------------------------------------------------------------------------
# TAB 6: RIDER WORKLOAD & FLEET PERFORMANCE
# -----------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 🚴 **Rider Workload Analytics & Fleet Performance**")

    rider_perf = deliveries_df.groupby("rider_id").agg(
        Total_Deliveries=("delivery_id", "count"),
        Avg_Delivery_Time=("delivery_duration", "mean"),
        Total_Distance_KM=("distance_km", "sum")
    ).reset_index()

    rider_full = riders_df.merge(rider_perf, on="rider_id", how="left").fillna(0)
    rider_full["Avg_Delivery_Time"] = rider_full["Avg_Delivery_Time"].round(1)

    mean_load = rider_full["Total_Deliveries"].mean()
    rider_full["Workload_Status"] = rider_full["Total_Deliveries"].apply(
        lambda n: "Overloaded" if n > mean_load * 1.3 else ("Underutilized" if n < mean_load * 0.7 else "Optimal")
    )

    col_w1, col_w2 = st.columns(2)

    with col_w1:
        wk_counts = rider_full["Workload_Status"].value_counts().reset_index()
        wk_counts.columns = ["Workload_Status", "count"]
        fig_wk = plot_bar_chart(wk_counts, "Workload_Status", "count", "Fleet Workload Distribution Status", color_col="Workload_Status")
        st.plotly_chart(fig_wk, use_container_width=True)

    with col_w2:
        top_riders = rider_full.sort_values("Total_Deliveries", ascending=False).head(10)
        fig_top = plot_bar_chart(top_riders, "rider_name", "Total_Deliveries", "Top 10 Delivery Riders", color_col="Total_Deliveries")
        st.plotly_chart(fig_top, use_container_width=True)

    render_interactive_table(
        rider_full[["rider_id", "rider_name", "city", "vehicle_type", "shift_type", "experience_years", "Total_Deliveries", "Avg_Delivery_Time", "Workload_Status"]],
        "Rider Workload Fleet Master Table",
        "rider_workload_master",
        key="rider_wk_table"
    )

# -----------------------------------------------------------------------------
# TAB 7: OPERATIONAL ANOMALY DETECTION
# -----------------------------------------------------------------------------
with tabs[6]:
    st.markdown("### ⚠️ **Statistical Operational Anomaly Detection**")
    st.markdown("Detecting statistical outliers across delivery duration, cancellation rates, and promotional subsidies (Z-Score & IQR bounds).")

    if not anomalies_df.empty:
        col_an1, col_an2 = st.columns([1, 2])

        with col_an1:
            st.metric("Total Flagged Anomalies", f"{len(anomalies_df):,}")
            crit_count = (anomalies_df["Severity"] == "Critical").sum()
            st.metric("Critical Anomalies", f"{crit_count:,}")

            sev_counts = anomalies_df["Severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "count"]
            fig_sev = plot_donut_chart(sev_counts, "Severity", "count", "Anomaly Severity Breakdown")
            st.plotly_chart(fig_sev, use_container_width=True)

        with col_an2:
            render_interactive_table(
                anomalies_df,
                "Operational Anomalies Master Audit",
                "operational_anomalies_table",
                key="anom_table"
            )
    else:
        st.success("No statistical operational anomalies detected.")

# -----------------------------------------------------------------------------
# TAB 8: OPERATIONAL EARLY WARNING SYSTEM
# -----------------------------------------------------------------------------
with tabs[7]:
    st.markdown("### 🚨 **Operational Early Warning Engine**")

    if not alerts_df.empty:
        for _, alert in alerts_df.iterrows():
            sev = alert.get("Severity", "🟢 Healthy")
            box_type = st.error if "Critical" in sev else (st.warning if "Warning" in sev else st.success)

            box_type(f"""
            **{sev} | Category: {alert.get('Category')} — {alert.get('Entity')}**
            - **Metric:** {alert.get('Metric')} = `{alert.get('Current_Value')}` (Threshold: `{alert.get('Threshold')}`)
            - **Explanation:** {alert.get('Explanation')}
            - **Recommended Action:** 👉 {alert.get('Recommended_Action')}
            """)
    else:
        st.success("All operational early warning metrics are operating normally.")
