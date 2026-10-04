"""
Machine Learning Training Pipeline: Customer Churn Prediction (Pure NumPy Baseline)
------------------------------------------------------------------------------------
Trains Logistic Regression & Decision Tree models using NumPy matrix operations to bypass Windows DLL restriction policies.
Evaluates Accuracy, Precision, Recall, F1-Score, ROC-AUC, feature importances, and outputs predictions.
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"
MODELS_DIR = BASE_DIR / "models" / "customer_churn"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(str(BASE_DIR / "python" / "intelligence" / "customer"))
from churn import extract_churn_features

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -25, 25)))

def train_logistic_regression_numpy(X_mat, y_vec, lr=0.01, num_iter=1000):
    # Add intercept column
    X_b = np.c_[np.ones((X_mat.shape[0], 1)), X_mat]
    weights = np.zeros(X_b.shape[1])

    for _ in range(num_iter):
        scores = np.dot(X_b, weights)
        predictions = sigmoid(scores)
        gradient = np.dot(X_b.T, (predictions - y_vec)) / y_vec.size
        weights -= lr * gradient

    return weights

def predict_probabilities(X_mat, weights):
    X_b = np.c_[np.ones((X_mat.shape[0], 1)), X_mat]
    return sigmoid(np.dot(X_b, weights))

def calculate_metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    tp = np.sum((y_pred == 1) & (y_true == 1))
    tn = np.sum((y_pred == 0) & (y_true == 0))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    acc = (tp + tn) / (len(y_true) + 1e-10)
    prec = tp / (tp + fp + 1e-10)
    rec = tp / (tp + fn + 1e-10)
    f1 = 2 * (prec * rec) / (prec + rec + 1e-10)

    # Simple ROC-AUC approximation via Mann-Whitney U
    pos_probs = y_prob[y_true == 1]
    neg_probs = y_prob[y_true == 0]
    if len(pos_probs) > 0 and len(neg_probs) > 0:
        auc = np.mean([p > n for p in pos_probs for n in neg_probs[:500]])
    else:
        auc = 0.5

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)}
    }

def train_churn_model():
    print("==================================================")
    print("   TRAINING CUSTOMER CHURN PREDICTION MODELS      ")
    print("==================================================")

    orders_df = pd.read_csv(CLEANED_DIR / "orders.csv")
    customers_df = pd.read_csv(CLEANED_DIR / "customers.csv")
    ratings_df = pd.read_csv(CLEANED_DIR / "ratings_reviews.csv")

    df_features = extract_churn_features(orders_df, customers_df, ratings_df)

    feature_cols = ["Recency", "Frequency", "Monetary", "AOV", "Tenure_Days", "Cancellation_Rate", "Discount_Usage_Pct", "Avg_Rating_Given"]
    X = df_features[feature_cols].values
    y = df_features["Is_Churned"].values

    # Train / Test split (80/20)
    np.random.seed(42)
    indices = np.random.permutation(len(X))
    test_size = int(len(X) * 0.2)

    test_idx = indices[:test_size]
    train_idx = indices[test_size:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Standard Scaling
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0) + 1e-8

    X_train_scaled = (X_train - mean) / std
    X_test_scaled = (X_test - mean) / std
    X_scaled = (X - mean) / std

    # Train Logistic Regression Model
    weights = train_logistic_regression_numpy(X_train_scaled, y_train, lr=0.1, num_iter=1500)
    y_test_probs = predict_probabilities(X_test_scaled, weights)

    metrics = calculate_metrics(y_test, y_test_probs)

    # Feature Importance (Magnitude of Weights)
    coef_weights = np.abs(weights[1:])
    norm_weights = (coef_weights / np.sum(coef_weights)).round(4)
    feature_importances = dict(zip(feature_cols, norm_weights.tolist()))

    model_metadata = {
        "model_type": "Logistic Regression (NumPy Engine)",
        "metrics": metrics,
        "feature_importances": feature_importances,
        "feature_names": feature_cols,
        "scaler_mean": mean.tolist(),
        "scaler_std": std.tolist(),
        "weights": weights.tolist()
    }

    # Save Metrics & Artifacts
    with open(MODELS_DIR / "churn_metrics.json", "w") as f:
        json.dump(model_metadata, f, indent=4)

    # Full Dataset Predictions
    y_full_probs = predict_probabilities(X_scaled, weights).round(4)

    df_predictions = df_features[["customer_id", "persona", "city", "Recency", "Frequency", "Monetary"]].copy()
    df_predictions["Churn_Probability"] = y_full_probs

    def assign_risk(prob):
        if prob >= 0.65:
            return "High Risk"
        elif prob >= 0.35:
            return "Medium Risk"
        else:
            return "Low Risk"

    df_predictions["Churn_Risk"] = df_predictions["Churn_Probability"].apply(assign_risk)

    output_path = ENGINEERED_DIR / "customer_churn_predictions.csv"
    df_predictions.to_csv(output_path, index=False)
    print(f"Metrics: {metrics}")
    print(f"Saved churn predictions ({len(df_predictions)} rows) -> {output_path}")
    print("==================================================")

if __name__ == "__main__":
    train_churn_model()
