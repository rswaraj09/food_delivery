import mysql.connector
from mysql.connector import Error
import sys

# Replace these with your actual database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Replace with your actual MySQL password
    'database': 'swift_serves'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def fix_menu_items_table():
    """Fix the menu_items table by adding the business_id column if it's missing"""
    try:
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to database.")
            return False
            
        cursor = connection.cursor()
        
        # Check if business_id column exists
        cursor.execute("""
        SELECT COUNT(*) AS column_exists
        FROM information_schema.columns 
        WHERE table_schema = %s 
        AND table_name = 'menu_items' 
        AND column_name = 'business_id'
        """, (db_config['database'],))
        
        result = cursor.fetchone()
        has_business_id = result[0] > 0
        
        if not has_business_id:
            print("The business_id column is missing from menu_items table. Adding it...")
            
            # Add the business_id column with a default value of 1
            cursor.execute("""
            ALTER TABLE menu_items 
            ADD COLUMN business_id INT NOT NULL DEFAULT 1,
            ADD CONSTRAINT fk_menu_business
            FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
            """)
            connection.commit()
            
            # Update existing menu items to have business_id = 1
            cursor.execute("UPDATE menu_items SET business_id = 1")
            connection.commit()
            
            print("Successfully added business_id column to menu_items table.")
            
            # Verify the column was added
            cursor.execute("DESCRIBE menu_items")
            columns = cursor.fetchall()
            print("\nMenu Items Table Structure:")
            for col in columns:
                print(col)
                
            # Check the data
            cursor.execute("SELECT id, item_name, business_id FROM menu_items")
            items = cursor.fetchall()
            print("\nMenu Items Data:")
            for item in items:
                print(item)
        else:
            print("The business_id column already exists in the menu_items table.")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        error_str = str(e)
        print(f"Error fixing menu_items table: {error_str}")
        return False

if __name__ == "__main__":
    print("Running database fix script for Swift Serve...")
    success = fix_menu_items_table()
    if success:
        print("Database fix completed successfully.")
    else:
        print("Failed to fix database.")
        sys.exit(1) 