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
from components.kpi_cards import render_kpi_grid
from components.charts import plot_line_chart, plot_bar_chart, plot_donut_chart, plot_histogram
from components.tables import render_interactive_table
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Financial Intelligence — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="expanded")

apply_custom_theme()

data, data_source = load_all_datasets()
filters = render_sidebar(data_source)

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="Financial Intelligence", 
        subtitle="Platform P&L Analytics, Margin Performance & Revenue Leakage.",
        icon="💰"
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=f"Updated Today, {last_refresh}")

orders_eng = apply_global_filters(data["orders_engineered"], data["customers"], filters)
promotions_df = data["promotions"]
payments_df = data["payments"]
leakage_df = data.get("revenue_leakage", pd.DataFrame())

# Main Page Tabs
fin_tabs = st.tabs([
    "📊 Financial P&L Overview",
    "🏷️ Campaign Economics",
    "💸 Revenue Leakage Intelligence"
])

# -----------------------------------------------------------------------------
# TAB 1: FINANCIAL P&L OVERVIEW
# -----------------------------------------------------------------------------
with fin_tabs[0]:
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

    kpis = [
        {"title": "GROSS REVENUE (GTV)", "value": format_currency(total_gross_rev), "subtext": "Base menu order amounts"},
        {"title": "NET REVENUE", "value": format_currency(total_net_rev), "subtext": "Value after discounts & fees"},
        {"title": "PLATFORM PROFIT", "value": format_currency(total_est_profit), "subtext": "Est. commission + fees"},
        {"title": "NET MARGIN %", "value": format_percent(profit_margin_pct), "subtext": "Profit / Net Revenue"},
        {"title": "AVERAGE ORDER VALUE", "value": format_currency(aov), "subtext": "Net basket value"},
        {"title": "DISCOUNT SUBSIDIES", "value": format_currency(total_discounts), "subtext": "Promo subsidies"},
    ]

    render_kpi_grid(kpis, 3)

    st.markdown("---")
    st.markdown("### 📈 **Financial & Profitability Trends**")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        if "order_datetime" in orders_eng.columns:
            orders_eng["month"] = pd.to_datetime(orders_eng["order_datetime"]).dt.strftime("%Y-%m")
            monthly_fin = orders_eng.groupby("month").agg(
                Revenue=("final_amount", "sum"),
                Profit=("estimated_profit", "sum")
            ).reset_index()

            fig_fin_trend = plot_line_chart(monthly_fin, "month", "Revenue", "Monthly Platform Net Revenue Trend (₹)")
            st.plotly_chart(fig_fin_trend, use_container_width=True)

    with col_f2:
        if "month" in orders_eng.columns:
            fig_profit_trend = plot_line_chart(monthly_fin, "month", "Profit", "Monthly Platform Estimated Profit Trend (₹)")
            st.plotly_chart(fig_profit_trend, use_container_width=True)

    col_f3, col_f4 = st.columns(2)

    with col_f3:
        payments_merged = payments_df.merge(orders_eng[["order_id", "final_amount"]], on="order_id", how="left")
        pay_rev = payments_merged.groupby("payment_method")["final_amount"].sum().reset_index()
        fig_pay = plot_donut_chart(pay_rev, "payment_method", "final_amount", "Revenue Contribution by Payment Method")
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_f4:
        fig_aov_dist = plot_histogram(orders_eng, "final_amount", "Order Value Distribution (₹)", nbins=30)
        st.plotly_chart(fig_aov_dist, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 **DETAILED ANALYSIS**")
    fin_summary = orders_eng.groupby("city").agg(
        Orders=("order_id", "count"),
        Gross_Revenue=("order_amount", "sum"),
        Discounts=("discount_amount", "sum"),
        Delivery_Fees=("delivery_fee", "sum"),
        Net_Revenue=("final_amount", "sum"),
        Platform_Profit=("estimated_profit", "sum")
    ).reset_index()

    render_interactive_table(fin_summary, "City Financial P&L Master Table", "city_financial_master", key="fin_summary_table")

# -----------------------------------------------------------------------------
# TAB 2: CAMPAIGN ECONOMICS
# -----------------------------------------------------------------------------
with fin_tabs[1]:
    st.markdown("### 🏷️ **Promotional Campaign Overview**")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        promo_type_counts = promotions_df["promo_type"].value_counts().reset_index()
        promo_type_counts.columns = ["promo_type", "count"]
        fig_promo_type = plot_bar_chart(promo_type_counts, "promo_type", "count", "Promotional Campaigns by Type")
        st.plotly_chart(fig_promo_type, use_container_width=True)

    with col_p2:
        promo_budget = promotions_df.groupby("promo_type")["campaign_budget"].sum().reset_index()
        fig_promo_budget = plot_bar_chart(promo_budget, "promo_type", "campaign_budget", "Total Budget Allocated by Promo Type (₹)")
        st.plotly_chart(fig_promo_budget, use_container_width=True)

    render_interactive_table(promotions_df, "Promotional Campaigns Master Table", "promotions_master_table", key="promos_table")

# -----------------------------------------------------------------------------
# TAB 3: REVENUE LEAKAGE INTELLIGENCE
# -----------------------------------------------------------------------------
with fin_tabs[2]:
    st.markdown("### 💸 **Revenue Leakage Intelligence**")
    st.info("ℹ️ **Methodology:** Potential Leakage — Rule-Based Detection (Auditing excessive discounts, waived delivery fees, cancellation losses, and negative margins).")

    if not leakage_df.empty:
        total_leak_amt = leakage_df["potential_leakage_amount"].sum()
        flagged_count = len(leakage_df)
        total_orders = len(orders_eng)
        leakage_rate = (flagged_count / max(1, total_orders)) * 100
        crit_count = (leakage_df["risk_level"] == "Critical Leakage").sum()

        leak_kpis = [
            {"title": "Total Potential Leakage", "value": format_currency(total_leak_amt), "subtext": "Sum of detected subsidy/margin leaks"},
            {"title": "Flagged Orders Count", "value": format_number(flagged_count), "subtext": "Orders breaching leakage rules"},
            {"title": "Platform Leakage Rate %", "value": format_percent(leakage_rate), "subtext": "% of total audited orders"},
            {"title": "Critical Leakage Orders", "value": format_number(crit_count), "subtext": "Severe leakage or negative profit"},
        ]
        render_kpi_grid(leak_kpis, 4)

        col_l1, col_l2 = st.columns(2)

        with col_l1:
            risk_counts = leakage_df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["risk_level", "count"]
            fig_risk = plot_donut_chart(risk_counts, "risk_level", "count", "Revenue Leakage Risk Level Breakdown")
            st.plotly_chart(fig_risk, use_container_width=True)

        with col_l2:
            # Leakage by Reason
            leak_reasons = leakage_df.groupby("leakage_reason")["potential_leakage_amount"].sum().reset_index().sort_values("potential_leakage_amount", ascending=False).head(5)
            fig_reasons = plot_bar_chart(leak_reasons, "leakage_reason", "potential_leakage_amount", "Top Financial Leakage Drivers (₹)")
            st.plotly_chart(fig_reasons, use_container_width=True)

        render_interactive_table(
            leakage_df,
            "Revenue Leakage Master Audit Log",
            "revenue_leakage_master_log",
            key="leakage_master_table"
        )
    else:
        st.success("No financial revenue leakage flagged in the current dataset filter.")
