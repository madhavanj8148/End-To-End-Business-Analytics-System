-- ==================================================
-- PHASE 3 ADVANCED INTELLIGENCE QUERIES
-- CLV, RFM, Cohort Retention & Partner Benchmarks
-- ==================================================

-- Query 1: Analytical Customer Lifetime Value (CLV) Calculation
SELECT
    customer_id,
    COUNT(*) AS total_orders,
    SUM(final_amount) AS total_revenue,
    ROUND(AVG(final_amount), 2) AS avg_order_value,
    DATEDIFF(MAX(order_datetime), MIN(order_datetime)) AS tenure_days,
    ROUND(SUM(final_amount) + (AVG(final_amount) * (COUNT(*) / GREATEST(DATEDIFF(MAX(order_datetime), MIN(order_datetime)), 30) * 365)), 2) AS estimated_clv
FROM orders
GROUP BY customer_id
ORDER BY estimated_clv DESC
LIMIT 20;

-- Query 2: Advanced RFM Scores
WITH rfm_base AS (
    SELECT
        customer_id,
        DATEDIFF(CURDATE(), MAX(order_datetime)) AS recency,
        COUNT(*) AS frequency,
        SUM(final_amount) AS monetary
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
FROM rfm_base;

-- Query 3: Cohort Retention Breakdown
WITH first_order AS (
    SELECT customer_id, DATE_FORMAT(MIN(order_datetime), '%Y-%m') AS cohort_month
    FROM orders
    GROUP BY customer_id
)
SELECT
    f.cohort_month,
    DATE_FORMAT(o.order_datetime, '%Y-%m') AS order_month,
    COUNT(DISTINCT o.customer_id) AS active_customers,
    SUM(o.final_amount) AS cohort_revenue
FROM first_order f
JOIN orders o ON f.customer_id = o.customer_id
GROUP BY f.cohort_month, order_month
ORDER BY f.cohort_month, order_month;

-- Query 4: Restaurant Peer Percentile Benchmarks
SELECT
    r.restaurant_id,
    r.restaurant_name,
    r.city,
    r.cuisine_type,
    COUNT(o.order_id) AS total_orders,
    SUM(o.final_amount) AS total_revenue,
    PERCENT_RANK() OVER (PARTITION BY r.city ORDER BY SUM(o.final_amount)) AS city_revenue_percentile,
    PERCENT_RANK() OVER (PARTITION BY r.cuisine_type ORDER BY SUM(o.final_amount)) AS cuisine_revenue_percentile
FROM restaurants r
LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id
GROUP BY r.restaurant_id, r.restaurant_name, r.city, r.cuisine_type;
