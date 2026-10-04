"""
Page 7: Ask NovaNest AI — Conversational Business Intelligence
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "streamlit_app"))
sys.path.append(str(BASE_DIR / "python" / "ai" / "conversational"))
sys.path.append(str(BASE_DIR / "python" / "ai" / "insights"))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from query_router import route_query
from nl_to_sql import generate_sql
from sql_validator import validate_sql
from query_executor import execute_query
from answer_generator import generate_answer
from business_insights import generate_business_insights
import re
sys.path.append(str(BASE_DIR / "python"))
from decision_simulation.scenario_engine import run_scenario

st.set_page_config(page_title=f"Ask NovaNest AI — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT)

st.title("🤖 Ask NovaNest AI")
st.caption("Conversational Decision Intelligence, NL2SQL, and Automated Business Insights")

# Load data (for insights)
data, _ = load_all_datasets()
orders_df = data.get("orders", pd.DataFrame())
customers_df = data.get("customers", pd.DataFrame())

tab_chat, tab_insights = st.tabs(["💬 Chat with NovaNest AI", "📈 AI Business Insights"])

with tab_chat:
    st.markdown("### Conversational Analytics")
    st.info("Ask questions like: 'Show me top 5 restaurants', 'Revenue by city', or 'Why did revenue drop?'")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am NovaNest AI. How can I help you analyze your food delivery data today?"})
        
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # React to user input
    if prompt := st.chat_input("Ask a business question..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Determine intent
        intent = route_query(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                final_response = ""
                
                if intent == "NL2SQL":
                    sql_query = generate_sql(prompt)
                    if sql_query:
                        if validate_sql(sql_query):
                            st.write(f"*(Executing generated SQL)*: `{sql_query}`")
                            df_result = execute_query(sql_query)
                            final_response = generate_answer(prompt, intent, sql_result=df_result, sql_query=sql_query)
                        else:
                            final_response = "The generated SQL query failed safety validation (only read operations are permitted)."
                    else:
                        final_response = "I couldn't generate a confident SQL query for that question. Try asking for 'revenue by city' or 'top 5 restaurants'."
                elif intent == "SIMULATION":
                    st.write("*(Running Decision Simulator)*")
                    # Simple regex to extract percentages
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
                        
                    sim_result = run_scenario("Ask NovaNest Scenario", params, data)
                    final_response = generate_answer(prompt, intent, simulation_result=sim_result)
                else:
                    final_response = generate_answer(prompt, intent)
                    
                st.markdown(final_response)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": final_response})

with tab_insights:
    st.markdown("### Automated Business Insights")
    st.write("NovaNest AI continuously monitors your data to surface important trends.")
    
    with st.spinner("Generating insights..."):
        insights = generate_business_insights(orders_df, customers_df)
        
    for insight in insights:
        st.success(insight)
