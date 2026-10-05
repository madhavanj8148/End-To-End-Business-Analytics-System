"""
Page 7: Ask NovaNest AI — Conversational Business Intelligence
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import datetime

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python" / "ai" / "conversational"))
sys.path.append(str(BASE_DIR / "python" / "ai" / "insights"))
sys.path.append(str(BASE_DIR / "python"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from query_router import route_query
from nl_to_sql import generate_sql
from sql_validator import validate_sql
from query_executor import execute_query
from answer_generator import generate_answer
from business_insights import generate_business_insights
import re
from decision_simulation.scenario_engine import run_scenario
from utils.ui import apply_custom_theme, render_page_header, render_status_bar

st.set_page_config(page_title=f"Ask NovaNest AI — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

apply_custom_theme()

# Hide Sidebar for cinematic feel
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
        /* Custom Chat Styling */
        .ai-message {
            background: rgba(6, 182, 212, 0.05);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 4px 8px 8px 4px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.1);
        }
        .user-message {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-right: 3px solid var(--text-secondary);
            border-radius: 8px 4px 4px 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            text-align: right;
        }
        .ai-header {
            color: var(--accent-cyan);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .user-header {
            color: var(--text-secondary);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Load data (for insights)
data, data_source = load_all_datasets()
orders_df = data.get("orders", pd.DataFrame())
customers_df = data.get("customers", pd.DataFrame())

# Header Section
col1, col2 = st.columns([2, 1])
with col1:
    render_page_header(
        title="NovaNest Core Intelligence", 
        subtitle="Conversational NL2SQL & Autonomous Business Analytics",
        icon=""
    )
with col2:
    is_connected = data_source == "MySQL Database"
    last_refresh = datetime.datetime.now().strftime("%I:%M %p")
    render_status_bar(data_connected=is_connected, last_refresh=last_refresh)

st.markdown("<h3 style='font-size:1.1rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom: 1.5rem;'>Communication Link Established</h3>", unsafe_allow_html=True)

col_main, col_side = st.columns([2.5, 1], gap="large")

with col_side:
    st.markdown("""
    <div style="background: var(--surface-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <div style="color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;">System Capabilities</div>
        <div style="font-size: 0.85rem; color: var(--text-primary); margin-bottom: 0.75rem;">> Natural Language to SQL generation</div>
        <div style="font-size: 0.85rem; color: var(--text-primary); margin-bottom: 0.75rem;">> Automated Insight detection</div>
        <div style="font-size: 0.85rem; color: var(--text-primary); margin-bottom: 0.75rem;">> Operational simulation routing</div>
        <div style="font-size: 0.85rem; color: var(--text-primary);">> Real-time database querying</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;'>Automated Insights (Background)</div>", unsafe_allow_html=True)
    with st.spinner("Scanning core metrics..."):
        insights = generate_business_insights(orders_df, customers_df)
    
    for insight in insights:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); border-left: 2px solid var(--success); padding: 0.75rem; border-radius: 0 4px 4px 0; margin-bottom: 0.75rem; font-size: 0.8rem; color: var(--text-primary);">
            {insight}
        </div>
        """, unsafe_allow_html=True)

with col_main:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Link established. I am the NovaNest core intelligence. Awaiting operational queries."})
        
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f"""
            <div class="ai-message">
                <div class="ai-header">CORE_INTELLIGENCE // RESPONSE</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="user-message">
                <div class="user-header">EXECUTIVE // COMMAND</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
    # React to user input
    if prompt := st.chat_input("Enter command or query (e.g. 'Show me revenue by city')..."):
        # Display user message
        st.markdown(f"""
        <div class="user-message">
            <div class="user-header">EXECUTIVE // COMMAND</div>
            <div>{prompt}</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Determine intent
        intent = route_query(prompt)
        
        final_response = ""
        with st.spinner("Processing cognitive routing..."):
            if intent == "NL2SQL":
                sql_query = generate_sql(prompt)
                if sql_query:
                    if validate_sql(sql_query):
                        st.markdown(f"<div style='font-family: monospace; font-size: 0.8rem; color: var(--accent-cyan); margin-bottom: 1rem;'>[Executing Query: {sql_query}]</div>", unsafe_allow_html=True)
                        df_result = execute_query(sql_query)
                        final_response = generate_answer(prompt, intent, sql_result=df_result, sql_query=sql_query)
                    else:
                        final_response = "Access denied. SQL query failed safety validation."
                else:
                    final_response = "Unable to map natural language to structured query format. Please rephrase."
            elif intent == "SIMULATION":
                st.markdown(f"<div style='font-family: monospace; font-size: 0.8rem; color: var(--accent-indigo); margin-bottom: 1rem;'>[Engaging Simulation Matrix]</div>", unsafe_allow_html=True)
                match = re.search(r'(-?\d+)\s*%', prompt)
                val = float(match.group(1)) if match else 0
                
                params = {}
                if "demand" in prompt.lower():
                    params["demand_change_pct"] = val
                elif "discount" in prompt.lower():
                    if "reduce" in prompt.lower(): val = -val
                    params["discount_change_pct"] = val
                elif "capacity" in prompt.lower():
                    params["rider_capacity_change_pct"] = val
                    
                sim_result = run_scenario("Executive Scenario Request", params, data)
                final_response = generate_answer(prompt, intent, simulation_result=sim_result)
            else:
                final_response = generate_answer(prompt, intent)
                
            st.markdown(f"""
            <div class="ai-message">
                <div class="ai-header">CORE_INTELLIGENCE // RESPONSE</div>
                <div>{final_response}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": final_response})

st.markdown("<br><br><div style='text-align: center;'><a href='/' target='_self' style='color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 500;'>← Return to Main Platform Hub</a></div>", unsafe_allow_html=True)
