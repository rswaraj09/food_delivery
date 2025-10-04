def fix_menu_items_table():
    """Fix the menu_items table by adding the business_id column if it's missing"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if business_id column exists
        cursor.execute("""
        SELECT COUNT(*) AS column_exists
        FROM information_schema.columns 
        WHERE table_schema = DATABASE()
        AND table_name = 'menu_items' 
        AND column_name = 'business_id'
        """)
        
        result = cursor.fetchone()
        has_business_id = result[0] > 0
        
        if not has_business_id:
            print("The business_id column is missing from menu_items table. Adding it...")
            
            # First check if there are any existing menu items
            cursor.execute("SELECT COUNT(*) FROM menu_items")
            has_items = cursor.fetchone()[0] > 0
            
            # Add the business_id column with a default value of 1
            cursor.execute("""
            ALTER TABLE menu_items 
            ADD COLUMN business_id INT NOT NULL DEFAULT 1
            """)
            
            # Add the foreign key constraint after setting the default value
            cursor.execute("""
            ALTER TABLE menu_items
            ADD CONSTRAINT fk_menu_business
            FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
            """)
            
            connection.commit()
            print("Successfully added business_id column to menu_items table.")
        else:
            print("The business_id column already exists in the menu_items table.")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error fixing menu_items table: {error_str}")
        return False 