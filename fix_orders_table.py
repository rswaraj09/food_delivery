import sys
from db import get_db_connection
from mysql.connector import Error

def fix_orders_table():
    """Fix the orders table by checking and adding the business_id column if it's missing"""
    try:
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to database.")
            return False
            
        cursor = connection.cursor()
        
        # Check the structure of the orders table
        print("Checking orders table structure...")
        cursor.execute("DESCRIBE orders")
        columns = cursor.fetchall()
        print("\nOrders Table Structure:")
        
        has_business_id = False
        for col in columns:
            print(col)
            if col[0] == 'business_id':
                has_business_id = True
        
        if not has_business_id:
            print("\nThe business_id column is missing from orders table. Adding it...")
            
            # Add the business_id column with a default value of 1
            cursor.execute("""
            ALTER TABLE orders 
            ADD COLUMN business_id INT NOT NULL DEFAULT 1
            """)
            
            # Try to add the foreign key constraint
            try:
                cursor.execute("""
                ALTER TABLE orders
                ADD CONSTRAINT fk_order_business
                FOREIGN KEY (business_id) REFERENCES businesses(id)
                """)
                print("Added foreign key constraint for business_id.")
            except Error as e:
                print(f"Warning: Could not add foreign key constraint: {e}")
                print("The column was added but without the foreign key constraint.")
            
            connection.commit()
            
            print("Successfully added business_id column to orders table.")
            
            # Verify the column was added
            cursor.execute("DESCRIBE orders")
            columns = cursor.fetchall()
            print("\nUpdated Orders Table Structure:")
            for col in columns:
                print(col)
        else:
            print("\nThe business_id column already exists in the orders table.")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        error_str = str(e)
        print(f"Error fixing orders table: {error_str}")
        return False

if __name__ == "__main__":
    print("Running database fix script for Swift Serve orders table...")
    success = fix_orders_table()
    if success:
        print("Orders table fix completed successfully.")
    else:
        print("Failed to fix orders table.")
        sys.exit(1) 