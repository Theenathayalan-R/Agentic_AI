-- This is a sample SQL DDL file for testing purposes.
-- It creates a simple 'users' table.

CREATE TABLE public.users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Another sample table for demonstrating multiple statements
CREATE TABLE public.orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (user_id) REFERENCES public.users(user_id)
);
