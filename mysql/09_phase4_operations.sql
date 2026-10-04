-- ============================================================================
-- NovaNest Phase 4 SQL — Operations & Predictive Intelligence Analytics
-- ============================================================================

USE novanest_db;

-- ----------------------------------------------------------------------------
-- 1. Daily City Demand Forecasting Aggregation View
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_daily_city_demand AS
SELECT 
    DATE(o.order_datetime) AS order_date,
    COALESCE(c.city, 'Unknown') AS city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.final_amount) AS total_revenue,
    SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(SUM(CASE WHEN o.order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(o.order_id), 0), 2) AS cancellation_rate_pct
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
GROUP BY DATE(o.order_datetime), COALESCE(c.city, 'Unknown');


-- ----------------------------------------------------------------------------
-- 2. Delivery SLA & ETA Performance Summary
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_delivery_eta_summary AS
SELECT 
    c.city,
    COUNT(d.delivery_id) AS total_deliveries,
    ROUND(AVG(d.delivery_duration), 1) AS avg_delivery_duration_mins,
    ROUND(AVG(d.distance_km), 2) AS avg_distance_km,
    SUM(CASE WHEN d.delivery_duration <= 45 THEN 1 ELSE 0 END) AS ontime_deliveries,
    ROUND(SUM(CASE WHEN d.delivery_duration <= 45 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(d.delivery_id), 0), 2) AS ontime_rate_pct,
    SUM(CASE WHEN d.delivery_duration > 45 THEN 1 ELSE 0 END) AS delayed_deliveries
FROM deliveries d
JOIN orders o ON d.order_id = o.order_id
LEFT JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city;


-- ----------------------------------------------------------------------------
-- 3. Delivery Rider Workload & Capacity Analysis
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_rider_workload_analytics AS
SELECT 
    r.rider_id,
    r.rider_name,
    r.city,
    r.vehicle_type,
    r.shift_type,
    r.experience_years,
    COUNT(d.delivery_id) AS total_orders_handled,
    ROUND(AVG(d.delivery_duration), 1) AS avg_delivery_time_mins,
    ROUND(SUM(d.distance_km), 1) AS total_distance_covered_km,
    CASE 
        WHEN COUNT(d.delivery_id) >= 20 THEN 'Overloaded'
        WHEN COUNT(d.delivery_id) <= 5 THEN 'Underutilized'
        ELSE 'Optimal'
    END AS workload_tier
FROM riders r
LEFT JOIN deliveries d ON r.rider_id = d.rider_id
GROUP BY r.rider_id, r.rider_name, r.city, r.vehicle_type, r.shift_type, r.experience_years;


-- ----------------------------------------------------------------------------
-- 4. Revenue Leakage & High Discount Subsidies Query
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_revenue_leakage_orders AS
SELECT 
    o.order_id,
    o.customer_id,
    o.restaurant_id,
    o.order_amount,
    o.discount_amount,
    o.delivery_fee,
    o.final_amount,
    ROUND((o.discount_amount / NULLIF(o.order_amount, 0)) * 100, 2) AS discount_pct,
    o.order_status,
    CASE 
        WHEN o.order_status = 'Cancelled' THEN 'Cancelled Order Loss'
        WHEN (o.discount_amount / NULLIF(o.order_amount, 0)) > 0.25 AND o.discount_amount > 200 THEN 'Excessive Discount Subsidy'
        WHEN o.delivery_fee = 0 AND o.order_amount < 300 THEN 'Waived Delivery Fee'
        ELSE 'Normal'
    END AS leakage_category
FROM orders o
WHERE o.order_status = 'Cancelled'
   OR (o.discount_amount / NULLIF(o.order_amount, 0)) > 0.25
   OR (o.delivery_fee = 0 AND o.order_amount < 300);
