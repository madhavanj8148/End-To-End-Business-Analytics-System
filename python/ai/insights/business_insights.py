"""
Phase 5 — AI Business Insights
------------------------------
Generates AI-driven business insights based on current dataset metrics.
"""

import pandas as pd

def generate_business_insights(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> list:
    """
    Analyzes data and generates a list of key conversational business insights.
    """
    insights = []
    
    if not orders_df.empty:
        total_revenue = orders_df['final_amount'].sum()
        total_orders = len(orders_df)
        avg_order_val = total_revenue / total_orders if total_orders > 0 else 0
        
        insights.append(f"💰 **Revenue Intelligence**: Total revenue generated is ₹{total_revenue:,.2f} across {total_orders:,} orders. The average order value sits at ₹{avg_order_val:,.2f}.")
        
        # Delivery times
        if 'delivery_fee' in orders_df.columns:
            avg_fee = orders_df['delivery_fee'].mean()
            insights.append(f"🛵 **Operations**: The average delivery fee collected per order is ₹{avg_fee:,.2f}.")
            
    if not customers_df.empty:
        total_customers = len(customers_df)
        insights.append(f"👥 **Customer Growth**: NovaNest is currently serving {total_customers:,} registered customers.")
        
    if not insights:
        insights.append("Not enough data to generate business insights at this time.")
        
    return insights
