"""
Phase 5 — Content-Based Recommendation Engine
---------------------------------------------
Recommends items based on item attributes (cuisine type, price, etc.)
similar to those the customer has highly rated or frequently purchased.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def build_item_features(menu_df: pd.DataFrame):
    """Builds a feature matrix for menu items."""
    features_df = menu_df[['item_id', 'cuisine_type', 'price', 'preparation_time']].copy()
    
    # One-hot encode cuisine
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    cuisine_encoded = encoder.fit_transform(features_df[['cuisine_type']])
    
    # Scale numeric features
    scaler = MinMaxScaler()
    numeric_scaled = scaler.fit_transform(features_df[['price', 'preparation_time']])
    
    # Combine features
    feature_matrix = np.hstack([cuisine_encoded, numeric_scaled])
    
    return feature_matrix, features_df['item_id'].values

def generate_content_recommendations(customer_id: str, orders_df: pd.DataFrame, 
                                     menu_df: pd.DataFrame, top_k: int = 10):
    """
    Generates top K recommendations using content-based filtering.
    Finds items similar to the customer's most purchased items.
    """
    try:
        # Get customer's top purchased items
        cust_orders = orders_df[orders_df['customer_id'] == customer_id]
        if cust_orders.empty:
            return pd.DataFrame()
            
        top_purchased = cust_orders['item_id'].value_counts().head(5).index.tolist()
        
        # Build features
        feature_matrix, item_ids = build_item_features(menu_df)
        item_to_idx = {item_id: idx for idx, item_id in enumerate(item_ids)}
        
        # Create a customer profile vector (average of top purchased item vectors)
        top_indices = [item_to_idx[item] for item in top_purchased if item in item_to_idx]
        if not top_indices:
            return pd.DataFrame()
            
        customer_profile = feature_matrix[top_indices].mean(axis=0).reshape(1, -1)
        
        # Calculate similarity with all items
        similarities = cosine_similarity(customer_profile, feature_matrix)[0]
        
        # Exclude already purchased items
        purchased_items = cust_orders['item_id'].unique()
        purchased_indices = [item_to_idx[item] for item in purchased_items if item in item_to_idx]
        similarities[purchased_indices] = 0
        
        # Get top K
        top_recs_idx = similarities.argsort()[::-1][:top_k]
        
        recs = []
        for idx in top_recs_idx:
            if similarities[idx] > 0:
                recs.append({
                    'item_id': item_ids[idx],
                    'content_score': round(float(similarities[idx]), 4)
                })
                
        return pd.DataFrame(recs)
    except Exception as e:
        logger.error(f"Content-based filtering failed: {e}")
        return pd.DataFrame()
