"""
Phase 5 — Hybrid Recommendation Engine
--------------------------------------
Combines collaborative filtering and content-based scores to generate
a unified recommendation list with AI-generated explanations.
"""

import pandas as pd
import logging
from .collaborative_filtering import generate_collaborative_recommendations
from .content_based import generate_content_recommendations
from .recommendation_explanations import generate_explanation

logger = logging.getLogger(__name__)

def get_hybrid_recommendations(customer_id: str, orders_df: pd.DataFrame, 
                               menu_df: pd.DataFrame, top_k: int = 5,
                               cf_weight: float = 0.6, cb_weight: float = 0.4):
    """
    Combines CF and CB recommendations into a final hybrid score.
    """
    try:
        # Get collaborative recommendations
        cf_recs = generate_collaborative_recommendations(customer_id, orders_df, top_k=top_k*2)
        
        # Get content-based recommendations
        cb_recs = generate_content_recommendations(customer_id, orders_df, menu_df, top_k=top_k*2)
        
        if cf_recs.empty and cb_recs.empty:
            # Fallback to popular items if no history
            return get_popular_recommendations(orders_df, menu_df, top_k)
            
        # Merge scores
        if not cf_recs.empty and not cb_recs.empty:
            hybrid_df = pd.merge(cf_recs, cb_recs, on='item_id', how='outer').fillna(0)
        elif not cf_recs.empty:
            hybrid_df = cf_recs.copy()
            hybrid_df['content_score'] = 0
        else:
            hybrid_df = cb_recs.copy()
            hybrid_df['collaborative_score'] = 0
            
        # Calculate hybrid score
        hybrid_df['hybrid_score'] = (
            hybrid_df['collaborative_score'] * cf_weight + 
            hybrid_df['content_score'] * cb_weight
        )
        
        # Sort and take top K
        top_recs = hybrid_df.sort_values(by='hybrid_score', ascending=False).head(top_k)
        
        # Merge with menu details
        result_df = pd.merge(top_recs, menu_df, on='item_id', how='inner')
        
        # Generate explanations
        result_df['ai_explanation'] = result_df.apply(
            lambda row: generate_explanation(row['item_name'], row['collaborative_score'], row['content_score']),
            axis=1
        )
        
        return result_df
        
    except Exception as e:
        logger.error(f"Hybrid recommendation failed: {e}")
        return pd.DataFrame()

def get_popular_recommendations(orders_df: pd.DataFrame, menu_df: pd.DataFrame, top_k: int = 5):
    """Fallback: Recommends globally popular items."""
    popular_items = orders_df['item_id'].value_counts().head(top_k).reset_index()
    popular_items.columns = ['item_id', 'purchase_count']
    
    result_df = pd.merge(popular_items, menu_df, on='item_id', how='inner')
    result_df['hybrid_score'] = 1.0 # Max score for popular items
    result_df['ai_explanation'] = "Highly popular item ordered frequently by other customers."
    return result_df
