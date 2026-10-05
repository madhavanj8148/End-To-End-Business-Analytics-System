import streamlit as st
import os

def apply_custom_theme():
    """Injects premium, cinematic, dark-themed custom CSS for NovaNest."""
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* CSS Variables - Premium Dark Theme */
        :root {
            --bg-base: #050505;
            --bg-gradient: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #050505 70%);
            --surface-bg: rgba(20, 20, 25, 0.6);
            --surface-hover: rgba(30, 30, 40, 0.8);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(6, 182, 212, 0.3);
            
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-tertiary: #64748b;
            
            --accent-cyan: #06b6d4;
            --accent-indigo: #4f46e5;
            --accent-violet: #8b5cf6;
            
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            
            --font-main: 'Inter', sans-serif;
        }

        /* Global App Styling */
        html, body, [class*="css"]  {
            font-family: var(--font-main) !important;
        }
        
        .stApp {
            background: var(--bg-base);
            background-image: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-primary);
        }

        /* Hide Default Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Remove top padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px;
        }

        /* Premium Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 10, 15, 0.95) !important;
            border-right: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
        }
        
        [data-testid="stSidebar"] .css-17lntkn {
            color: var(--text-secondary);
        }

        /* Metric Styling (KPI Cards) */
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.02em;
            text-shadow: 0 0 20px rgba(255,255,255,0.1);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.25rem;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }
        
        /* Glassmorphism Cards */
        div.stMetric, .stAlert, div[data-testid="stExpander"] {
            background: var(--surface-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 1.25rem;
            box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        div.stMetric:hover {
            background: var(--surface-hover) !important;
            border-color: var(--border-glow) !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 32px -4px rgba(6, 182, 212, 0.15);
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 6px 6px 0px 0px;
            gap: 1px;
            padding: 0 16px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(6, 182, 212, 0.1) !important;
            border-bottom: 2px solid var(--accent-cyan) !important;
            color: var(--accent-cyan) !important;
            text-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, var(--accent-indigo), var(--accent-cyan));
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
            width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
            transform: translateY(-1px);
            border-color: transparent;
            color: white;
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            background: var(--surface-bg);
        }
        
        /* Typography overrides */
        h1, h2, h3 {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
        }
        
        /* Custom UI Components */
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 0.2rem;
            line-height: 1.1;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--accent-cyan);
            font-weight: 400;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 2rem;
        }
        
        .insight-card {
            background: var(--surface-bg);
            border-left: 3px solid var(--accent-cyan);
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        .insight-card:hover {
            background: var(--surface-hover);
            transform: translateX(4px);
        }
        .insight-cat {
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--accent-violet);
            font-weight: 600;
            letter-spacing: 0.1em;
            margin-bottom: 0.25rem;
        }
        .insight-text {
            font-size: 0.95rem;
            color: var(--text-primary);
            line-height: 1.5;
        }
        
        /* Progress bars */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--accent-indigo), var(--accent-cyan));
        }
        
        /* Dividers */
        hr {
            border-color: var(--border-color) !important;
            margin: 2rem 0 !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, icon: str = ""):
    """Renders a cinematic, premium page header."""
    st.markdown(f"""
    <div style="padding-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); margin-bottom: 2.5rem;">
        <h1 style="margin-bottom: 0.5rem; font-size: 2rem; font-weight: 600; color: #F8FAFC; letter-spacing: -0.02em;">
            {title}
        </h1>
        <p style="color: var(--accent-cyan); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 500; margin-top: 0;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_status_bar(data_connected: bool, last_refresh: str):
    """Renders a minimalist top right status indicator."""
    status_color = "var(--success)" if data_connected else "var(--warning)"
    status_text = "LIVE" if data_connected else "FALLBACK"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px; padding-top: 10px;">
        <div style="display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {status_color}; box-shadow: 0 0 8px {status_color};"></div>
            <span style="color: var(--text-primary); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.1em;">{status_text}</span>
        </div>
        <div style="color: var(--text-secondary); font-size: 0.75rem; letter-spacing: 0.05em; font-variant-numeric: tabular-nums;">
            SYNC {last_refresh}
        </div>
    </div>
    """, unsafe_allow_html=True)

