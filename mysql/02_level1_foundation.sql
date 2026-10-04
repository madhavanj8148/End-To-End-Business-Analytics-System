-- LEVEL 1 FOUNDATION ANALYTICS

SELECT *
FROM customers;

SELECT DISTINCT city
FROM customers;

SELECT * FROM customers WHERE city="chennai";

SELECT *
FROM customers
WHERE subscription_type='Premium';

SELECT *
FROM restaurants
ORDER BY avg_rating DESC;

SELECT *
FROM orders
ORDER BY final_amount DESC
LIMIT 10;

SELECT city,
COUNT(*) AS total_customers
FROM customers
GROUP BY city;

SELECT persona,
COUNT(*) AS total_customers
FROM customers
GROUP BY persona;

SELECT cuisine_type,
COUNT(*) AS total_restaurants
FROM restaurants
GROUP BY cuisine_type
ORDER BY total_restaurants DESC;

SELECT order_status,
COUNT(*) AS total_orders
FROM orders
GROUP BY order_status;