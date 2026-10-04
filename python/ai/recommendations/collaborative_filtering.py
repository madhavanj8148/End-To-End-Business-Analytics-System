"""
Phase 5 — Collaborative Filtering Recommendation Engine
-------------------------------------------------------
Implements item-item or user-user collaborative filtering based on customer
order history (interaction strength = purchase count).
"""

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def build_interaction_matrix(orders_df: pd.DataFrame):
    """Builds a sparse customer-item interaction matrix based on purchase count."""
    # Count orders per customer per item
    interaction_df = orders_df.groupby(['customer_id', 'item_id']).size().reset_index(name='purchase_count')
    
    # Create mappings
    customers = interaction_df['customer_id'].unique()
    items = interaction_df['item_id'].unique()
    
    customer_to_idx = {c: i for i, c in enumerate(customers)}
    item_to_idx = {i_d: j for j, i_d in enumerate(items)}
    idx_to_item = {j: i_d for j, i_d in enumerate(items)}
    
    row = interaction_df['customer_id'].map(customer_to_idx)
    col = interaction_df['item_id'].map(item_to_idx)
    data = interaction_df['purchase_count'].astype(float)
    
    # Create sparse matrix
    matrix = csr_matrix((data, (row, col)), shape=(len(customers), len(items)))
    
    return matrix, customer_to_idx, item_to_idx, idx_to_item

def compute_item_similarity(interaction_matrix):
    """Computes item-item cosine similarity."""
    # Item-item similarity (transpose of interaction matrix)
    item_sim = cosine_similarity(interaction_matrix.T, dense_output=False)
    return item_sim

def generate_collaborative_recommendations(customer_id: str, orders_df: pd.DataFrame, 
                                           top_k: int = 10):
    """
    Generates top K item recommendations for a given customer using item-item CF.
    """
    try:
        matrix, customer_to_idx, item_to_idx, idx_to_item = build_interaction_matrix(orders_df)
        
        if customer_id not in customer_to_idx:
            return pd.DataFrame()
            
        cust_idx = customer_to_idx[customer_id]
        cust_profile = matrix[cust_idx]
        
        # Multiply customer profile by item similarity matrix
        item_sim = compute_item_similarity(matrix)
        scores = cust_profile.dot(item_sim).toarray()[0]
        
        # Exclude items already purchased
        purchased_indices = cust_profile.indices
        scores[purchased_indices] = 0
        
        # Get top K indices
        top_indices = scores.argsort()[::-1][:top_k]
        
        recs = []
        for idx in top_indices:
            if scores[idx] > 0:
                recs.append({
                    'item_id': idx_to_item[idx],
                    'collaborative_score': round(float(scores[idx]), 4)
                })
                
        # Normalize scores to 0-1
        if recs:
            max_score = max(r['collaborative_score'] for r in recs)
            if max_score > 0:
                for r in recs:
                    r['collaborative_score'] = round(r['collaborative_score'] / max_score, 4)
                    
        return pd.DataFrame(recs)
    except Exception as e:
        logger.error(f"Collaborative filtering failed: {e}")
        return pd.DataFrame()
