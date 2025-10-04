-- Fix for Error: 1054 (42S22): Unknown column 'business_id' in 'field list'
-- Run this script in your MySQL database to add the missing business_id column

USE swift_serves;

-- Check if business_id column exists in menu_items table
SELECT COUNT(*) AS column_exists
FROM information_schema.columns 
WHERE table_schema = 'swift_serves' 
AND table_name = 'menu_items' 
AND column_name = 'business_id';

-- Add the business_id column if it doesn't exist
ALTER TABLE menu_items
ADD COLUMN business_id INT NOT NULL DEFAULT 1,
ADD CONSTRAINT fk_menu_business
FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE;

-- Update existing menu items to associate with appropriate businesses
-- Replace 1 with actual business IDs as needed
UPDATE menu_items 
SET business_id = 1;

-- Verify the column was added successfully
DESCRIBE menu_items;

-- Select all menu items to verify the business_id was added
SELECT id, item_name, business_id FROM menu_items; 