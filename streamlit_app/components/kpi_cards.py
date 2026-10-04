"""
Reusable KPI Cards Component
"""

import streamlit as st
from utils.formatting import format_currency, format_number, format_percent

def render_kpi_card(title: str, value: str, subtext: str = None, delta: str = None):
    """Renders a single styled KPI card metric."""
    st.metric(label=title, value=value, delta=delta, help=subtext)

def render_kpi_grid(kpis: list, cols_count: int = 4):
    """
    Renders a grid of KPI metrics.
    kpis format: list of dicts [{'title': '...', 'value': '...', 'delta': '...', 'subtext': '...'}]
    """
    cols = st.columns(cols_count)
    for idx, kpi in enumerate(kpis):
        col = cols[idx % cols_count]
        with col:
            st.metric(
                label=kpi.get("title", ""),
                value=kpi.get("value", "0"),
                delta=kpi.get("delta", None),
                help=kpi.get("subtext", None)
            )
