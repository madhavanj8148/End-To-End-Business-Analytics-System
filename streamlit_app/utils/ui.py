import streamlit as st
import os

def apply_custom_theme():
    """Injects custom CSS for the modern NovaNest UI."""
    css = """
    <style>
        /* CSS Variables */
        :root {
            --primary-color: #4F46E5; /* Indigo */
            --accent-color: #06B6D4; /* Cyan */
            --success-color: #10B981; /* Green */
            --warning-color: #F59E0B; /* Amber */
            --critical-color: #EF4444; /* Red */
            --neutral-bg: #0F172A; /* Slate 900 */
            --card-bg: #1E293B; /* Slate 800 */
            --card-border: #334155; /* Slate 700 */
            --text-main: #F8FAFC; /* Slate 50 */
            --text-muted: #94A3B8; /* Slate 400 */
        }
        
        /* Global App Styling */
        .stApp {
            background-color: var(--neutral-bg);
            color: var(--text-main);
        }
        
        /* Hide Default Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--card-bg) !important;
            border-right: 1px solid var(--card-border);
        }
        
        /* Metric Styling (KPI Cards) */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: var(--primary-color) !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.85rem !important;
        }
        
        /* Custom Cards */
        div.stMetric, .css-1r6slb0, .css-1y4p8pa {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div.stMetric:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(79, 70, 229, 0.1) !important;
            border-bottom: 2px solid var(--primary-color) !important;
            color: var(--primary-color) !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #4338CA;
            color: white;
            border-color: transparent;
        }
        .stButton>button:focus {
            box-shadow: 0 0 0 2px rgba(79,70,229,0.5);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--card-border);
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, icon: str = ""):
    """Renders a consistent, premium page header."""
    st.markdown(f"""
    <div style="padding-bottom: 1rem; border-bottom: 1px solid var(--card-border); margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.2rem; font-size: 2.5rem; font-weight: 800; color: #F8FAFC; display: flex; align-items: center; gap: 10px;">
            <span>{icon}</span> {title}
        </h1>
        <p style="color: #94A3B8; font-size: 1.1rem; margin-top: 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_status_bar(data_connected: bool, last_refresh: str):
    """Renders a top right status indicator (called within columns typically)."""
    status_color = "var(--success-color)" if data_connected else "var(--warning-color)"
    status_text = "Data Connected" if data_connected else "Local Fallback"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px; padding-top: 15px;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {status_color};"></div>
            <span style="color: var(--text-muted); font-size: 0.85rem; font-weight: 600;">{status_text}</span>
        </div>
        <div style="color: var(--text-muted); font-size: 0.85rem;">
            ⏱️ {last_refresh}
        </div>
    </div>
    """, unsafe_allow_html=True)
