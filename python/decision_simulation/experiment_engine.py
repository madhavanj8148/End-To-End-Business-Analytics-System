"""
Phase 6 — Experiment Engine (A/B Testing)
-----------------------------------------
Evaluates experiments between Control and Treatment groups.
"""

def evaluate_experiment(control_metrics: dict, treatment_metrics: dict, sample_size: int = 1000) -> dict:
    """
    Evaluates simulated business performance of a treatment vs control.
    """
    
    # Calculate simple relative lifts
    c_rev = control_metrics.get("revenue_per_user", 1.0)
    t_rev = treatment_metrics.get("revenue_per_user", 1.0)
    rev_lift = ((t_rev - c_rev) / c_rev) if c_rev > 0 else 0
    
    c_conv = control_metrics.get("conversion_rate", 0.05)
    t_conv = treatment_metrics.get("conversion_rate", 0.05)
    conv_lift = ((t_conv - c_conv) / c_conv) if c_conv > 0 else 0
    
    # Very naive mock of significance check
    is_significant = abs(conv_lift) > 0.02 and sample_size > 500
    
    return {
        "Control": control_metrics,
        "Treatment": treatment_metrics,
        "Absolute_Difference": {
            "revenue_per_user": t_rev - c_rev,
            "conversion_rate": t_conv - c_conv
        },
        "Relative_Lift": {
            "revenue_per_user": rev_lift,
            "conversion_rate": conv_lift
        },
        "Statistically_Significant": is_significant,
        "Recommendation": "Deploy Treatment" if (is_significant and rev_lift > 0) else "Keep Control"
    }
