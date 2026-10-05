# 🍔 NovaNest — AI-Powered Food Delivery Analytics, Decision Intelligence & Digital Twin Platform

An end-to-end, enterprise-grade **Food Delivery Analytics & Intelligence Platform** built to analyze customer purchasing behavior, restaurant performance, delivery operations, clickstream behavior, and financial health using **Python, Streamlit, Plotly, Scikit-Learn, MySQL, SQL, and Power BI**.

**NovaNest** transforms raw data into an interactive 360° Decision Intelligence Ecosystem, processing transactions across 50,000 orders, 5,000 customers, 1,500 restaurants, 4,000 riders, and 100,000 app events.

---

## 📌 Project Overview

Food delivery platforms generate massive volumes of transactional and behavioral data across multiple dimensions. **NovaNest** provides interactive decision support & predictive intelligence:

* **Executive Command Center**: High-level P&L, city benchmarks, conversion funnels, and early operational signals.
* **Customer Intelligence & 360**: Advanced 9-Segment RFM, Customer Lifetime Value (CLV) Tiers, Cohort Retention Heatmap, ML Customer Churn Prediction (ROC-AUC: 1.000, F1-Score: 0.970), and Customer 360 Digital Twin profiles.
* **Restaurant Intelligence & Health Score**: 2x2 portfolio matrix, partner leaderboards, rule-based Health Scores (0-100), Risk Engine (`Critical`, `At Risk`), ML Order Throughput Forecast (R²: 0.8559, MAE: 2.15 orders), Peer Percentile Benchmarks, and Early Warning Signals.
* **Operations & Predictive Intelligence**: Daily city demand forecasting (R²: 0.8123, MAE: 4.14 orders/day), City × Day × Hour demand intensity heatmaps, Delivery ETA regressor (MAE: 10.06 mins), Smart Rider Allocation scoring engine, Fleet Workload Analytics, Statistical Anomaly Detection (Z-Score & IQR), Revenue Leakage Intelligence, and Operational Early Warnings.
* **Financial Intelligence & Unit Economics**: Gross vs Net Revenue, discount leakage, delivery fee secondary revenue, potential revenue leakage audit, and dynamic commission platform margins.
* **Decision Intelligence Engine**: Next Best Action (NBA) rule-based intervention engine synthesizing Customer, Restaurant, Operations, and Revenue triggers.

---

## 🏗️ System Architecture

```text
       ┌──────────────────────────────────────────────────────────┐
       │                SYNTHETIC DATA GENERATORS                 │
       │    (Faker & Realism Logic: Cities, Funnels, Constraints)  │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │             RAW DATASTORE (datasets/raw/)                │
       │  customers, restaurants, menu_items, riders, orders,     │
       │  payments, deliveries, app_events, promotions, reviews    │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │               DATA CLEANING & VALIDATION                 │
       │  (clean_data.py -> datasets/cleaned/)                    │
       │  (validate_master_data.py -> Quality Score: 100/100)     │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │              FEATURE ENGINEERING PIPELINE                │
       │  (feature_engineering.py -> datasets/engineered/)        │
       │  Dynamic Platform Profit, Churn Features, Demand, ETA,   │
       │  Anomalies, Revenue Leakage & Prediction CSVs            │
       └────────────────────────────┬─────────────────────────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               ▼                    ▼                    ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│    MYSQL RELATIONAL DB      │ │   STREAMLIT WEB PLATFORM    │ │     POWER BI DASHBOARDS     │
│ Canonical Schema: orders    │ │ (streamlit_app/app.py)      │ │ Customer, Restaurant, Ops & │
│ PK/FKs, Indexes, Decimals   │ │ 6 Modules, Interactive UI   │ │ Financial Intelligence      │
└─────────────────────────────┘ └─────────────────────────────┘ └─────────────────────────────┘
```

---

## 📊 Project Status

### Phase Status Summary

| Phase | Module / Capability | Status | Description |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Data Engineering & Quality** | ✅ **Complete** | Standardized 3-tier folder structure, raw generators, domain cleaning, 100/100 quality score, feature engineering, and production MySQL schema. |
| **Phase 2** | **Streamlit Analytics Platform** | ✅ **Complete** | 6-page interactive web application platform with MySQL connection, CSV fallback, Plotly charts, global filters, and CSV exports. |
| **Phase 3** | **Advanced Customer & Restaurant Intelligence** | ✅ **Complete** | CLV, 9-segment RFM, Cohort Retention Heatmap, ML Churn Model (F1: 0.9701), Customer 360 & Digital Twin, Restaurant Health Score (0-100), Risk Engine, ML Order Forecast (R²: 0.8559), Peer Benchmarking, Early Warning System & Next Best Action Engine. |
| **Phase 4** | **Operations & Predictive Intelligence** | ✅ **Complete** | Demand Forecasting (R²: 0.8123), City Demand Heatmaps, Delivery ETA Model (MAE: 10.06m), Smart Rider Allocation, Rider Workload Analytics, Statistical Anomaly Detection (Z-Score/IQR), Revenue Leakage Intelligence, Operational Early Warnings & NBA Integration. |
| **Phase 5** | **AI Intelligence & Conversational Analytics** | ✅ **Complete** | Collaborative & Content-Based Recommendation Engine, Conversational Business Intelligence, NL2SQL engine, and AI Insights generation. |
| **Phase 6** | **Decision Intelligence & Simulation** | ✅ **Complete** | What-if scenario simulator for pricing, commissions, operations, A/B experiment evaluation engine, and business impact ranking. |
| **Phase 7** | **Digital Twin & NovaNest Command Center** | ✅ **Complete** | Unified analytical Digital Twin aggregating Customer, Restaurant, Operations, and Financial states. Executive control tower dashboard with Top KPIs, active Business Alerts, Impact Chain modeling, and centralized Decision Simulation access. |
| **Phase 8** | **Testing, Security & Deployment** | ✅ **Complete** | Full project compilation validation, SQL safety validators preventing destructive commands, Digital Twin gracefully bypassing empty dataframes, deployment readiness evaluation, and architecture finalization. |
| **Phase 9** | **Premium UI/UX Redesign** | ✅ **Complete** | Comprehensive overhaul of the Streamlit application into an enterprise-grade command center. Global theme setup, standardized page headers, dynamic status bars, compact sidebar design, and visually cohesive KPI grids. |

---

## 🤖 Machine Learning & Predictive Models

### 1. Customer Churn Prediction Model (Phase 3)
* **Script**: `python/ml/train_customer_churn.py`
* **Artifacts**: `models/customer_churn/churn_metrics.json`, `datasets/engineered/customer_churn_predictions.csv`
* **Algorithm**: Logistic Regression (Pure NumPy Engine)
* **Metrics**: Accuracy: **99.50%** | F1-Score: **0.9701** | ROC-AUC: **1.000**
* **Features**: `Recency`, `Frequency`, `Monetary`, `AOV`, `Tenure_Days`, `Cancellation_Rate`, `Discount_Usage_Pct`, `Avg_Rating_Given`.

### 2. Restaurant Performance Prediction Model (Phase 3)
* **Script**: `python/ml/train_restaurant_prediction.py`
* **Artifacts**: `models/restaurant_prediction/restaurant_metrics.json`, `datasets/engineered/restaurant_predictions.csv`
* **Algorithm**: Linear Regression OLS (Pure NumPy Engine)
* **Metrics**: R² Score: **0.8559** | MAE: **2.15 orders** | RMSE: **2.52 orders**
* **Features**: `avg_rating`, `delivery_radius_km`, `commission_percentage`, `Total_Orders`, `Total_Revenue`, `Cancellation_Rate`, `AOV`.

### 3. Future Demand Prediction Model (Phase 4)
* **Script**: `python/ml/train_demand_forecast.py`
* **Artifacts**: `models/demand_forecast/demand_metrics.json`, `datasets/engineered/demand_forecasts.csv`
* **Algorithm**: Pure NumPy OLS Time-Series Regressor
* **Metrics**: R² Score: **0.8123** | MAE: **4.14 orders/day** | RMSE: **5.26 orders/day** | MAPE: **18.06%**
* **Features**: `day_of_week`, `is_weekend`, `lag_1d`, `lag_7d`, `rolling_mean_7d`. Time-aware 80/20 train/validation split.

### 4. Delivery ETA Prediction Model (Phase 4)
* **Script**: `python/ml/train_eta_model.py`
* **Artifacts**: `models/eta_prediction/eta_metrics.json`, `datasets/engineered/eta_predictions.csv`
* **Algorithm**: Pure NumPy OLS Multi-Feature Regressor
* **Metrics**: MAE: **10.06 minutes** | RMSE: **12.13 minutes** | R² Score: **0.3796**
* **Features**: `distance_km`, `hour`, `day_of_week`, `is_weekend`, `experience_years`, `city_onehot`.
* **Disclaimer**: *Traffic conditions are not directly modeled because live traffic data is unavailable.*

### 5. Smart Rider Allocation & Workload Engine (Phase 4)
* **Script**: `python/intelligence/operations/rider_allocation.py`
* **Artifacts**: `datasets/engineered/rider_allocation.csv`
* **Scoring Framework**: **Smart Rider Allocation — Rule-Based**
  * City Match: **40%**
  * Workload Capacity: **25%**
  * SLA Performance: **20%**
  * Rider Experience: **15%**

### 6. Operational Anomaly & Revenue Leakage Engine (Phase 4)
* **Script**: `python/intelligence/operations/anomaly_detection.py` & `revenue_leakage.py`
* **Artifacts**: `datasets/engineered/operational_anomalies.csv`, `revenue_leakage.csv`, `operational_alerts.csv`
* **Detection Methods**: Z-Score (>2.5 std) & IQR bounds for delivery SLA delays, cancellation spikes, excessive discounts (>25% or >₹200 subsidy), waived delivery fees, and negative order profit margins.

---

## 🖥️ Streamlit Analytics Platform (`streamlit_app/`)

Launch NovaNest's interactive Web Application:

```bash
streamlit run streamlit_app/app.py
```

### Multipage Intelligence Modules

1. **`01_Executive_Command_Center.py`**: Continuous scroll executive briefing. High-level platform KPIs, revenue/order trends, city performance benchmarks, conversion funnels, early business warning signals in premium glassmorphic containers.
2. **`02_Customer_Intelligence.py`**: Sleek Customer Intelligence Matrix. 9-Segment RFM, CLV Tiers, Cohort Retention Heatmap, ML Churn Risk Table, Customer 360 & Digital Twin Profile Viewer.
3. **`03_Restaurant_Intelligence.py`**: Partner Intelligence Network. 5-Component Partner Health Scores (0-100), 2x2 Portfolio Matrix, Risk Engine (`Critical`, `At Risk`), ML Order Throughput Forecast, Peer Benchmarking Percentiles, Early Warning Alerts.
4. **`04_Operations_Intelligence.py`**: Logistics Dispatch Control. Operations Overview, Future Demand Prediction, City Demand Heatmaps, Delivery ETA Intelligence, Smart Rider Allocation, Rider Workload & Fleet Performance, Operational Anomaly Detection, Operational Early Warnings.
5. **`05_Financial_Intelligence.py`**: Financial Command & Control. Gross vs Net Revenue, AOV trends, campaign budget breakdown, Revenue Leakage Intelligence master audit log with critical neon alerts.
6. **`06_Decision_Intelligence.py`**: AI Decision Engine. Synthesized Next Best Action (NBA) engine generating "AI Verdicts" formatted as futuristic terminal commands for prioritized Customer, Restaurant, Operations, and Revenue interventions.
7. **`07_Ask_NovaNest.py`**: Core Intelligence Link. Conversational Business Intelligence, NL2SQL engine, and AI Insights generation wrapped in a cinematic JARVIS-like interface.
8. **`08_Decision_Simulator.py`**: War Game Simulator. What-if deterministic scenario modeling with a styled Parameter Control Module and centralized Simulation Impact Matrix.

---

## ⚙️ Installation & Setup

### 1. Clone & Setup Environment

```bash
git clone https://github.com/your-username/NovaNest.git
cd NovaNest
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Machine Learning & Operations Pipelines

```bash
python python/ml/train_customer_churn.py
python python/ml/train_restaurant_prediction.py
python python/ml/train_demand_forecast.py
python python/ml/train_eta_model.py
python python/ml/train_anomaly_model.py
```

### 4. Run Streamlit Analytics Platform

    ```bash
    streamlit run streamlit_app/app.py
    ```

    ---

    # Deployment

    NovaNest is **prepared for deployment** to Linux-based cloud hosting environments (such as Streamlit Community Cloud, AWS, or GCP).
    *Deployment readiness has been verified locally; cloud deployment itself must still be tested.*

    ### 1. GitHub Repository Setup
    Ensure the repository is pushed to GitHub. The `.gitignore` is correctly configured to omit secrets, while leaving required `datasets/` intact for the fallback mode.

    ### 2. Streamlit Community Cloud Deployment
    1. Connect your GitHub repository to Streamlit Community Cloud.
    2. Set the main file path to: `streamlit_app/app.py`.
    3. Input the Required Environment variables (see below).
    4. Deploy.

    ### 3. Main File Path
    `streamlit_app/app.py`

    ### 4. Required Environment Variables
    Configuration is managed via `.env` (or Cloud Secrets). A secure template is provided in `.env.example`.
    ```text
    DB_HOST=your_host
    DB_PORT=3306
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_NAME=novanest
    ```

    ### 5. MySQL Configuration
    If you have a live cloud MySQL instance, ensure the schema is loaded via the `mysql/` folder scripts. The application will connect automatically using the environment variables provided.

    ### 6. CSV Fallback Behavior
    NovaNest natively supports robust failure handling. If the MySQL connection fails (or no variables are supplied in the cloud environment), the application gracefully defaults to **CSV Fallback** mode, utilizing the local data caches located in the `datasets/` tree.

    ### 7. How to Run Locally
    ```bash
    git clone <repository_url>
    cd NovaNest
    pip install -r requirements.txt
    streamlit run streamlit_app/app.py
    ```

    ---

    ## 👨‍💻 Author

**Sulthan Baasith Z**  
B.Tech Computer Science & Engineering  
VIT-AP University  

## High-Level Architecture Target

```text
                         NOVANEST
                            │
              ┌─────────────┴─────────────┐
              │                           │
        DATA FOUNDATION             ANALYTICS
              │                           │
              └─────────────┬─────────────┘
                            ↓
                 CUSTOMER / RESTAURANT
                     INTELLIGENCE
                            ↓
                   OPERATIONS AI/ML
                            ↓
                    FINANCIAL AI
                            ↓
                    AI INTELLIGENCE
                            ↓
                DECISION SIMULATION
                            ↓
                    DIGITAL TWIN
                            ↓
              NOVANEST COMMAND CENTER
                            ↓
                    BUSINESS DECISION
```
