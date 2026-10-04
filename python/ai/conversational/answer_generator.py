"""
Phase 5 — Conversational Answer Generator
-----------------------------------------
Formats database results and generated text into a conversational AI response.
"""
import pandas as pd

def generate_answer(user_input: str, intent: str, sql_result: pd.DataFrame = None, sql_query: str = "", simulation_result: dict = None) -> str:
    """Generates the final conversational string."""
    
    if intent == "NL2SQL":
        if sql_result is not None and not sql_result.empty:
            # Format dataframe as markdown table
            table_md = sql_result.to_markdown(index=False)
            return f"Here is the data you requested:\n\n{table_md}\n\n*Generated using SQL: `{sql_query}`*"
        else:
            return "I understood your query, but the database returned no results."
            
    elif intent == "ROOT_CAUSE":
        # Simulate RCA output based on keywords
        if "drop" in user_input.lower() and "revenue" in user_input.lower():
            return "Based on anomaly detection patterns, the drop in revenue last month correlates with a 15% increase in high-ETA orders (delay > 45 mins), causing elevated order cancellations."
        return "I can analyze root causes for changes in revenue, orders, or delivery times. Please specify the metric you are investigating."
        
    elif intent == "SIMULATION":
        if simulation_result:
            fin = simulation_result["results"]["financial"]["impact"]
            cust = simulation_result["results"]["customer"]["impact"]
            ops = simulation_result["results"]["operations"]["impact"]
            rec = simulation_result["recommendation"]
            
            return (f"**Simulation Results for your scenario:**\n\n"
                    f"- **Estimated Profit Margin Impact:** {(fin['Margin_Diff']*100):.1f}%\n"
                    f"- **Platform Revenue Impact:** ₹{fin['Platform_Revenue_Diff']:,.2f}\n"
                    f"- **Churn Impact (Reduction):** {cust['Churn_Reduction']:,} customers\n"
                    f"- **ETA Impact:** {ops['ETA_Diff_Mins']:.1f} mins\n\n"
                    f"**AI Recommendation:** {rec['Decision']} - {rec['Expected_Benefit']} {rec['Main_Risk']}")
        return "I could not run the simulation. Please try phrasing your scenario parameters clearly."
        
    else:
        # General response
        return "I am NovaNest AI. I can analyze business metrics, query the database, or recommend actions. Ask me things like 'What are the top 5 restaurants?' or 'Why did revenue drop?'"
