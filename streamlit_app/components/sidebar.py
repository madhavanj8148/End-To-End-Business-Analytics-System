"""
Global Sidebar Navigation & Filter Control Component
"""

import streamlit as st
from config.settings import CITIES, PERSONAS, ORDER_STATUSES
from utils.validation import get_data_quality_status

def render_sidebar(data_source: str):
    """Renders platform branding, data status, and global controls."""
    with st.sidebar:
        st.markdown("## 🍔 **NovaNest**")
        st.caption("AI-Powered Food Delivery Analytics & Decision Intelligence Platform")
        st.markdown("---")

        st.markdown("### 🎛️ **Global Filters**")

        selected_city = st.selectbox("Select City", CITIES)
        selected_persona = st.selectbox("Select Customer Persona", PERSONAS)
        selected_status = st.selectbox("Select Order Status", ORDER_STATUSES)

        st.markdown("---")
        st.markdown("### 📊 **System Status**")

        quality_score, health_status, health_msg = get_data_quality_status()

        st.info(f"**Data Source:** {data_source}")
        st.metric(label="Data Quality Score", value=f"{quality_score}/100", delta=health_status)

        st.markdown("---")
        st.caption("NovaNest v2.0 | Phase 2 Analytics Platform")

    return {
        "city": selected_city,
        "persona": selected_persona,
        "status": selected_status
    }
