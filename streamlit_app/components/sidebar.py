"""
Global Sidebar Navigation & Filter Control Component
"""

import streamlit as st
from config.settings import CITIES, PERSONAS, ORDER_STATUSES
from utils.validation import get_data_quality_status

def render_sidebar(data_source: str):
    """Renders platform branding, data status, and global controls."""
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h1 style="color: var(--primary-color); font-size: 1.8rem; margin-bottom: 0;">🍔 NovaNest</h1>
            <p style="color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">AI Business Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        with st.expander("🎛️ **GLOBAL FILTERS**", expanded=False):
            selected_city = st.selectbox("City", CITIES, key="sb_city")
            selected_persona = st.selectbox("Customer Segment", PERSONAS, key="sb_persona")
            selected_status = st.selectbox("Order Status", ORDER_STATUSES, key="sb_status")

        st.markdown("---")
        
        # System Status Area
        quality_score, health_status, health_msg = get_data_quality_status()
        
        st.markdown("""
        <div style="margin-top: 2rem; padding: 15px; background-color: var(--card-bg); border-radius: 8px; border: 1px solid var(--card-border);">
            <p style="font-size: 0.85rem; color: var(--text-muted); font-weight: 700; margin-bottom: 10px; text-transform: uppercase;">System Status</p>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--success-color);"></div>
                <span style="font-size: 0.85rem;">Data Engine</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--success-color);"></div>
                <span style="font-size: 0.85rem;">AI Engine</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--success-color);"></div>
                <span style="font-size: 0.85rem;">ML Models</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--accent-color);"></div>
                <span style="font-size: 0.85rem;">Digital Twin</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 15px; text-align: center; color: var(--text-muted); font-size: 0.75rem;'>NovaNest v1.0</div>", unsafe_allow_html=True)

    return {
        "city": selected_city,
        "persona": selected_persona,
        "status": selected_status
    }
