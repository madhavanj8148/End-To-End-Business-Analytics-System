-- ==================================================
-- NOVANEST PRODUCTION DATABASE SCHEMA
-- Canonical Table Naming: orders
-- Includes Primary Keys, Foreign Keys, Indexes & Decimal Types
-- ==================================================

DROP TABLE IF EXISTS ratings_reviews;
DROP TABLE IF EXISTS app_events;
DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS riders;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS promotions;

-- 1. Customers Table
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 18),
    gender VARCHAR(20),
    city VARCHAR(50) NOT NULL,
    persona VARCHAR(50),
    occupation VARCHAR(100),
    signup_date DATE NOT NULL,
    subscription_type VARCHAR(20),
    acquisition_channel VARCHAR(100),
    INDEX idx_customers_city (city),
    INDEX idx_customers_persona (persona)
);

-- 2. Restaurants Table
CREATE TABLE restaurants (
    restaurant_id VARCHAR(20) PRIMARY KEY,
    restaurant_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    restaurant_type VARCHAR(50),
    cuisine_type VARCHAR(50) NOT NULL,
    opening_year INT,
    avg_rating DECIMAL(3,1),
    delivery_radius_km DECIMAL(4,1),
    commission_percentage INT,
    INDEX idx_restaurants_city (city),
    INDEX idx_restaurants_cuisine (cuisine_type)
);

-- 3. Menu Items Table
CREATE TABLE menu_items (
    item_id VARCHAR(20) PRIMARY KEY,
    restaurant_id VARCHAR(20) NOT NULL,
    cuisine_type VARCHAR(50),
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    preparation_time INT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    INDEX idx_menu_restaurant (restaurant_id)
);

-- 4. Riders Table
CREATE TABLE riders (
    rider_id VARCHAR(20) PRIMARY KEY,
    rider_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50),
    experience_years INT,
    joining_year INT,
    shift_type VARCHAR(50),
    INDEX idx_riders_city (city)
);

-- 5. Orders Table (Canonical Name: orders)
CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_id VARCHAR(20) NOT NULL,
    item_id VARCHAR(20) NOT NULL,
    rider_id VARCHAR(20) NOT NULL,
    order_datetime DATETIME NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    order_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    delivery_fee DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id),
    FOREIGN KEY (rider_id) REFERENCES riders(rider_id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_restaurant (restaurant_id),
    INDEX idx_orders_rider (rider_id),
    INDEX idx_orders_datetime (order_datetime),
    INDEX idx_orders_status (order_status)
);

-- 6. Payments Table
CREATE TABLE payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    INDEX idx_payments_order (order_id)
);

-- 7. Deliveries Table
CREATE TABLE deliveries (
    delivery_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    rider_id VARCHAR(20) NOT NULL,
    distance_km DECIMAL(4,1) NOT NULL,
    delivery_duration INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (rider_id) REFERENCES riders(rider_id),
    INDEX idx_deliveries_order (order_id),
    INDEX idx_deliveries_rider (rider_id)
);

-- 8. App Events Table
CREATE TABLE app_events (
    event_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    INDEX idx_events_customer (customer_id),
    INDEX idx_events_type (event_type)
);

-- 9. Ratings & Reviews Table
CREATE TABLE ratings_reviews (
    review_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_rating INT CHECK (restaurant_rating BETWEEN 1 AND 5),
    delivery_rating INT CHECK (delivery_rating BETWEEN 1 AND 5),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_reviews_order (order_id),
    INDEX idx_reviews_customer (customer_id)
);

-- 10. Promotions Table
CREATE TABLE promotions (
    promo_id VARCHAR(20) PRIMARY KEY,
    promo_name VARCHAR(100) NOT NULL,
    promo_type VARCHAR(100),
    discount_percentage INT,
    campaign_budget DECIMAL(12,2)
);