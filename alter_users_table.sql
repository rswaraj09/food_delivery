-- Add student verification fields to the users table
ALTER TABLE users 
ADD COLUMN is_student BOOLEAN DEFAULT FALSE,
ADD COLUMN student_id_card VARCHAR(255) DEFAULT NULL,
ADD COLUMN is_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN discount_eligible BOOLEAN DEFAULT FALSE;

-- Add discount fields to the orders table
ALTER TABLE orders
ADD COLUMN discount_applied BOOLEAN DEFAULT FALSE,
ADD COLUMN discount_percentage DECIMAL(5, 2) DEFAULT 0.00; 