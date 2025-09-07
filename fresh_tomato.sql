-- fresh_tomato.sql

CREATE DATABASE IF NOT EXISTS fresh_tomato;
USE fresh_tomato;

-- Users table (farmers, customers, admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'customer', 'admin') NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    registration_date DATE,
    is_approved BOOLEAN DEFAULT FALSE
);

-- Products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(255),
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    farmer_id INT,
    rating INT DEFAULT 5,
    FOREIGN KEY (farmer_id) REFERENCES users(id)
);

-- Orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    customer_id INT,
    farmer_id INT,
    status ENUM('pending', 'accepted', 'delivered', 'rejected') DEFAULT 'pending',
    order_date DATE,
    delivery_date DATE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (farmer_id) REFERENCES users(id)
);

-- Pending users table (for admin approval, optional if you want to keep separate)
CREATE TABLE pending_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    role ENUM('farmer', 'customer') NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    registration_date DATE
);

-- Admin default user (optional, you can insert via app or here)
INSERT INTO users (username, password, role, is_approved)
VALUES ('Admin', 'Admin', 'admin', TRUE)
ON DUPLICATE KEY UPDATE username=username;
