import sys
from db import get_db_connection
from mysql.connector import Error

def complete_orders_table():
    """Add all missing columns to make orders table match the schema"""
    try:
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to database.")
            return False
            
        cursor = connection.cursor()
        
        # Get current table structure
        print("Checking orders table structure...")
        cursor.execute("DESCRIBE orders")
        existing_columns = cursor.fetchall()
        print("\nCurrent Orders Table Structure:")
        
        # Create a set of existing column names for easy lookup
        existing_column_names = set()
        for col in existing_columns:
            column_name = col[0]
            existing_column_names.add(column_name)
            print(col)
        
        # Define all columns that should be in the orders table
        required_columns = {
            'customer_name': "ADD COLUMN customer_name VARCHAR(100) NOT NULL DEFAULT 'Customer'",
            'customer_phone': "ADD COLUMN customer_phone VARCHAR(20) NOT NULL DEFAULT '0000000000'",
            'customer_email': "ADD COLUMN customer_email VARCHAR(100) NOT NULL DEFAULT 'customer@example.com'",
            'payment_method': "ADD COLUMN payment_method VARCHAR(50) DEFAULT 'Cash on Delivery'",
            'special_instructions': "ADD COLUMN special_instructions TEXT",
            'delivery_address': "ADD COLUMN delivery_address TEXT"
        }
        
        # Add any missing columns
        added_columns = []
        for column_name, alter_statement in required_columns.items():
            if column_name not in existing_column_names:
                print(f"\nAdding missing column: {column_name}")
                
                try:
                    cursor.execute(f"ALTER TABLE orders {alter_statement}")
                    added_columns.append(column_name)
                    print(f"Added {column_name} column.")
                except Error as e:
                    print(f"Error adding {column_name}: {e}")
        
        if added_columns:
            print(f"\nAdded {len(added_columns)} columns: {', '.join(added_columns)}")
            connection.commit()
            
            # Verify the updated structure
            cursor.execute("DESCRIBE orders")
            updated_columns = cursor.fetchall()
            print("\nUpdated Orders Table Structure:")
            for col in updated_columns:
                print(col)
        else:
            print("\nNo missing columns were found. The table is complete.")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        error_str = str(e)
        print(f"Error updating orders table: {error_str}")
        return False

if __name__ == "__main__":
    print("Running orders table completion script for Swift Serve...")
    success = complete_orders_table()
    if success:
        print("Orders table update completed successfully.")
    else:
        print("Failed to update orders table.")
        sys.exit(1) 