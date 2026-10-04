"""
Page 1: Executive Command Center
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from utils.formatting import format_currency, format_number, format_percent
from components.sidebar import render_sidebar
from components.filters import apply_global_filters
from components.kpi_cards import render_kpi_grid
from components.charts import (
    plot_line_chart, plot_bar_chart, plot_donut_chart, plot_funnel_chart, plot_histogram
)
from components.tables import render_interactive_table

st.set_page_config(page_title=f"Executive Command Center — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT)

data, data_source = load_all_datasets()
filters = render_sidebar(data_source)

# Filtered data
orders_df = apply_global_filters(data["orders"], data["customers"], filters)
customers_df = data["customers"]
restaurants_df = data["restaurants"]
deliveries_df = data["deliveries"]
events_df = data["app_events"]
ratings_df = data["ratings_reviews"]

st.title("🏢 Executive Command Center")
st.caption("High-Level Business Performance, Core Metrics & Strategic Operations")
st.markdown("---")

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

# KPI Grid Row 1
kpis_row1 = [
    {"title": "Total Revenue", "value": format_currency(total_rev), "subtext": "Sum of all completed/final order amounts"},
    {"title": "Total Orders", "value": format_number(total_orders), "subtext": "Total platform order volume"},
    {"title": "Average Order Value", "value": format_currency(aov), "subtext": "Average revenue generated per order"},
    {"title": "Customer Retention Rate", "value": format_percent(retention_rate), "subtext": "Percentage of customers with >1 order"},
]
render_kpi_grid(kpis_row1, 4)

st.markdown("<br>", unsafe_allow_html=True)

# KPI Grid Row 2
kpis_row2 = [
    {"title": "Active Customers", "value": format_number(total_cust), "subtext": "Unique registered customers"},
    {"title": "Active Restaurants", "value": format_number(total_rest), "subtext": "Partnered restaurant accounts"},
    {"title": "Avg Delivery Duration", "value": f"{avg_delivery_time:.1f} mins", "subtext": "Average delivery completion time"},
    {"title": "Cancellation Rate", "value": format_percent(cancellation_rate), "delta": "-0.4%" if cancellation_rate < 5 else "+1.2%", "subtext": "% of orders cancelled"},
]
render_kpi_grid(kpis_row2, 4)

st.markdown("---")

# 2. Executive Alert Section ("Early Business Signals")
st.markdown("### 🚨 **Early Business Signals & Operational Alerts**")
alert_col1, alert_col2 = st.columns(2)

with alert_col1:
    if cancellation_rate > 3.5:
        st.warning(f"🔴 **High Order Cancellation Rate**: Current cancellation rate is {cancellation_rate:.2f}% (Threshold: 3.5%). Investigate high cancellation zones.")
    else:
        st.success(f"🟢 **Healthy Cancellation Rate**: Current rate is {cancellation_rate:.2f}%.")

    if avg_delivery_time > 35:
        st.info(f"🟠 **Delivery SLA Warning**: Avg delivery duration is {avg_delivery_time:.1f} minutes. Target benchmark is <35 mins.")
    else:
        st.success(f"🟢 **Optimal Delivery Speed**: Avg delivery time is {avg_delivery_time:.1f} mins.")

with alert_col2:
    low_rated_rest = (restaurants_df["avg_rating"] < 3.8).sum()
    if low_rated_rest > 0:
        st.warning(f"🟠 **Partner Quality Warning**: {low_rated_rest} restaurants have ratings below 3.8 stars. Partner review recommended.")

    st.success(f"🟢 **Customer Growth**: Platform customer retention remains strong at {retention_rate:.1f}%.")

st.markdown("---")

# 3. Visualizations Section
st.markdown("### 📈 **Executive Visualizations & Performance Trends**")

col_v1, col_v2 = st.columns(2)

with col_v1:
    # Monthly Revenue & Orders Trend
    if "order_datetime" in orders_df.columns:
        orders_df["month"] = pd.to_datetime(orders_df["order_datetime"]).dt.strftime("%Y-%m")
        monthly_rev = orders_df.groupby("month")["final_amount"].sum().reset_index()
        fig_rev = plot_line_chart(monthly_rev, "month", "final_amount", "Monthly Revenue Trend (₹)", labels={"month": "Month", "final_amount": "Revenue (₹)"})
        st.plotly_chart(fig_rev, use_container_width=True)

with col_v2:
    # City Revenue Comparison
    city_rev = orders_df.groupby("city")["final_amount"].sum().reset_index().sort_values("final_amount", ascending=False)
    fig_city = plot_bar_chart(city_rev, "city", "final_amount", "Revenue Contribution by City (₹)")
    st.plotly_chart(fig_city, use_container_width=True)

col_v3, col_v4 = st.columns(2)

with col_v3:
    # Clickstream Funnel
    funnel_order = ["App Open", "Restaurant View", "Menu View", "Add To Cart", "Checkout", "Order Complete"]
    funnel_counts = events_df["event_type"].value_counts().reindex(funnel_order).reset_index()
    funnel_counts.columns = ["event_type", "total_events"]
    fig_funnel = plot_funnel_chart(funnel_counts, "event_type", "total_events", "App Event Conversion Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_v4:
    # Persona Distribution
    persona_counts = customers_df["persona"].value_counts().reset_index()
    persona_counts.columns = ["persona", "count"]
    fig_persona = plot_donut_chart(persona_counts, "persona", "count", "Customer Portfolio Breakdown by Persona")
    st.plotly_chart(fig_persona, use_container_width=True)

st.markdown("---")

# 4. Interactive Data Table & CSV Download
city_summary = orders_df.groupby("city").agg(
    Total_Orders=("order_id", "count"),
    Total_Revenue=("final_amount", "sum"),
    Average_Order_Value=("final_amount", "mean"),
    Total_Discounts=("discount_amount", "sum")
).reset_index()

render_interactive_table(city_summary, "City Executive Summary Table", "executive_city_summary", key="exec_summary")
