import mysql.connector
from mysql.connector import Error
from config import db_config
import os

def alter_tables():
    """Add student verification fields to the users table and discount fields to the orders table"""
    connection = None
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if is_student column already exists in users table
            cursor.execute("SHOW COLUMNS FROM users LIKE 'is_student'")
            is_student_exists = cursor.fetchone() is not None
            
            # Check if discount_applied column already exists in orders table
            cursor.execute("SHOW COLUMNS FROM orders LIKE 'discount_applied'")
            discount_applied_exists = cursor.fetchone() is not None
            
            # Only add columns if they don't exist
            if not is_student_exists:
                print("Adding student verification fields to users table...")
                # Add student verification fields to users table
                cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN is_student BOOLEAN DEFAULT FALSE,
                ADD COLUMN student_id_card VARCHAR(255) DEFAULT NULL,
                ADD COLUMN is_verified BOOLEAN DEFAULT FALSE,
                ADD COLUMN discount_eligible BOOLEAN DEFAULT FALSE
                """)
                print("Student verification fields added successfully!")
            else:
                print("Student verification fields already exist in users table.")
                
            if not discount_applied_exists:
                print("Adding discount fields to orders table...")
                # Add discount fields to orders table
                cursor.execute("""
                ALTER TABLE orders
                ADD COLUMN discount_applied BOOLEAN DEFAULT FALSE,
                ADD COLUMN discount_percentage DECIMAL(5, 2) DEFAULT 0.00
                """)
                print("Discount fields added successfully!")
            else:
                print("Discount fields already exist in orders table.")
            
            connection.commit()
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    alter_tables() 