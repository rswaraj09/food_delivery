import mysql.connector
from mysql.connector import Error
import hashlib
from config import db_config

# Function to get a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# User-related database functions
def create_user(name, email, password, phone, is_student=False, student_id_card=None):
    """Create a new user in the database"""
    try:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Email already exists"
            
        # Insert new user
        if is_student and student_id_card:
            # Student with ID card - needs verification
            query = """
            INSERT INTO users (name, email, password, phone, is_student, student_id_card, is_verified, discount_eligible)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, hashed_password, phone, True, student_id_card, False, False))
        elif is_student and not student_id_card:
            # Student without ID card
            query = """
            INSERT INTO users (name, email, password, phone, is_student)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, hashed_password, phone, True))
        else:
            # Regular user
            query = """
            INSERT INTO users (name, email, password, phone)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, hashed_password, phone))
            
        connection.commit()
        
        # Get the user ID
        user_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return True, user_id
    except Error as e:
        print(f"Error creating user: {e}")
        return False, str(e)

def validate_login(email, password):
    """Validate user login credentials"""
    try:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to find user with matching email and password
        query = """
        SELECT id, name, email, phone
        FROM users
        WHERE email = %s AND password = %s
        """
        cursor.execute(query, (email, hashed_password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            return True, user
        else:
            return False, "Invalid email or password"
    except Error as e:
        # Safely convert MySQL error to string
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error validating login: {error_str}")
        return False, "Database error"

def get_user_by_id(user_id):
    """Retrieve user by ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, name, email, phone, is_student, is_verified, discount_eligible
        FROM users
        WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return user
    except Error as e:
        print(f"Error retrieving user: {e}")
        return None

def update_user(user_id, name=None, phone=None):
    """Update user profile information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Build update query dynamically based on provided fields
        update_parts = []
        params = []
        
        if name:
            update_parts.append("name = %s")
            params.append(name)
        
        if phone:
            update_parts.append("phone = %s")
            params.append(phone)
        
        if not update_parts:
            return True, "No changes to make"
        
        query = f"UPDATE users SET {', '.join(update_parts)} WHERE id = %s"
        params.append(user_id)
        
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Profile updated successfully"
    except Error as e:
        print(f"Error updating user: {e}")
        return False, str(e)

def save_contact_submission(name, email, phone, subject, message):
    """Save a contact form submission to the database"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO contact_submissions (name, email, phone, subject, message)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, phone, subject, message))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Message saved successfully"
    except Error as e:
        print(f"Error saving contact submission: {e}")
        return False, str(e)

# Business-related database functions
def create_business(business_name, owner_name, email, password, phone, address, business_type):
    """Create a new business account in the database"""
    try:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM businesses WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Email already exists"
            
        # Insert new business
        query = """
        INSERT INTO businesses (business_name, owner_name, email, password, phone, address, business_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (business_name, owner_name, email, hashed_password, phone, address, business_type))
        connection.commit()
        
        # Get the business ID
        business_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return True, business_id
    except Error as e:
        print(f"Error creating business account: {e}")
        return False, str(e)

def validate_business_login(email, password):
    """Validate business login credentials"""
    try:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to find business with matching email and password
        query = """
        SELECT id, business_name, owner_name, email, phone, address, business_type, status
        FROM businesses
        WHERE email = %s AND password = %s
        """
        cursor.execute(query, (email, hashed_password))
        business = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if business:
            # Removed approval check - all businesses can login regardless of status
            return True, business
        else:
            return False, "Invalid email or password"
    except Error as e:
        # Safely convert MySQL error to string
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error validating business login: {error_str}")
        return False, "Database error"

def get_business_by_id(business_id):
    """Retrieve business by ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, business_name, owner_name, email, phone, address, business_type, status
        FROM businesses
        WHERE id = %s
        """
        cursor.execute(query, (business_id,))
        business = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return business
    except Error as e:
        print(f"Error retrieving business: {e}")
        return None

def update_business(business_id, business_name=None, owner_name=None, phone=None, address=None, business_type=None):
    """Update business profile information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Build update query dynamically based on provided fields
        update_parts = []
        params = []
        
        if business_name:
            update_parts.append("business_name = %s")
            params.append(business_name)
        
        if owner_name:
            update_parts.append("owner_name = %s")
            params.append(owner_name)
        
        if phone:
            update_parts.append("phone = %s")
            params.append(phone)
            
        if address:
            update_parts.append("address = %s")
            params.append(address)
            
        if business_type:
            update_parts.append("business_type = %s")
            params.append(business_type)
        
        if not update_parts:
            return True, "No changes to make"
        
        query = f"UPDATE businesses SET {', '.join(update_parts)} WHERE id = %s"
        params.append(business_id)
        
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Business profile updated successfully"
    except Error as e:
        print(f"Error updating business: {e}")
        return False, str(e)
        
def update_business_status(business_id, status):
    """Update business approval status (for admin use)"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "UPDATE businesses SET status = %s WHERE id = %s"
        cursor.execute(query, (status, business_id))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, f"Business status updated to {status}"
    except Error as e:
        print(f"Error updating business status: {e}")
        return False, str(e)
        
def get_all_businesses(status=None):
    """Get all businesses, optionally filtered by status"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if status:
            query = """
            SELECT id, business_name, owner_name, email, phone, address, business_type, status, created_at
            FROM businesses
            WHERE status = %s
            ORDER BY created_at DESC
            """
            cursor.execute(query, (status,))
        else:
            query = """
            SELECT id, business_name, owner_name, email, phone, address, business_type, status, created_at
            FROM businesses
            ORDER BY created_at DESC
            """
            cursor.execute(query)
            
        businesses = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return businesses
    except Error as e:
        print(f"Error retrieving businesses: {e}")
        return []

# Menu Items related functions
def add_menu_item(business_id, item_name, description, price, image_url=None, category=None):
    """Add a new menu item for a business"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO menu_items (business_id, item_name, description, price, image_url, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (business_id, item_name, description, price, image_url, category))
        connection.commit()
        
        # Get the item ID
        item_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return True, item_id
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error adding menu item: {error_str}")
        return False, "Database error"

def get_menu_items_by_business(business_id):
    """Get all menu items for a specific business"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, item_name, description, price, image_url, is_available, category
        FROM menu_items
        WHERE business_id = %s
        ORDER BY category, item_name
        """
        cursor.execute(query, (business_id,))
        items = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return items
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving menu items: {error_str}")
        return []

def update_menu_item(item_id, item_name=None, description=None, price=None, image_url=None, is_available=None, category=None):
    """Update a menu item"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Build update query dynamically based on provided fields
        update_parts = []
        params = []
        
        if item_name:
            update_parts.append("item_name = %s")
            params.append(item_name)
        
        if description:
            update_parts.append("description = %s")
            params.append(description)
        
        if price:
            update_parts.append("price = %s")
            params.append(price)
            
        if image_url:
            update_parts.append("image_url = %s")
            params.append(image_url)
            
        if is_available is not None:
            update_parts.append("is_available = %s")
            params.append(is_available)
            
        if category:
            update_parts.append("category = %s")
            params.append(category)
        
        if not update_parts:
            return True, "No changes to make"
        
        query = f"UPDATE menu_items SET {', '.join(update_parts)} WHERE id = %s"
        params.append(item_id)
        
        cursor.execute(query, params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Menu item updated successfully"
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error updating menu item: {error_str}")
        return False, "Database error"

def delete_menu_item(item_id):
    """Delete a menu item"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "DELETE FROM menu_items WHERE id = %s"
        cursor.execute(query, (item_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Menu item deleted successfully"
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error deleting menu item: {error_str}")
        return False, "Database error"

def get_menu_item_by_id(item_id):
    """Get a specific menu item by ID"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if the menu_items table has the business_id column
        cursor.execute("SHOW COLUMNS FROM menu_items LIKE 'business_id'")
        has_business_id = cursor.fetchone() is not None
        
        if has_business_id:
            query = """
            SELECT id, business_id, item_name, description, price, image_url, is_available, category
            FROM menu_items
            WHERE id = %s
            """
        else:
            # Fallback query without business_id if the column doesn't exist
            query = """
            SELECT id, item_name, description, price, image_url, is_available, category
            FROM menu_items
            WHERE id = %s
            """
        
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return item
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving menu item: {error_str}")
        return None

def get_all_menu_items():
    """Get all available menu items from all approved businesses for the explore page"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT m.id, m.business_id, b.business_name, m.item_name, m.description, 
               m.price, m.image_url, m.is_available, m.category
        FROM menu_items m
        JOIN businesses b ON m.business_id = b.id
        WHERE m.is_available = TRUE
        AND b.status = 'approved'
        ORDER BY RAND()
        """
        cursor.execute(query)
        items = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return items
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving all menu items: {error_str}")
        return []

# Order-related functions
def create_order(user_id, business_id, menu_item_id, quantity, total_amount, 
                customer_name, customer_phone, customer_email, delivery_address,
                payment_method='Cash on Delivery', special_instructions=None):
    """Create a new order with the specified items"""
    try:
        # Check if user is eligible for student discount
        discount_applied = False
        discount_percentage = 0.00
        original_amount = total_amount
        
        if is_user_eligible_for_discount(user_id):
            discount_applied = True
            discount_percentage = 50.00  # 50% discount for verified students
            total_amount = total_amount * 0.5  # Apply 50% discount
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First, get the menu item details
        menu_item_query = """
        SELECT item_name, price
        FROM menu_items
        WHERE id = %s
        """
        cursor.execute(menu_item_query, (menu_item_id,))
        menu_item = cursor.fetchone()
        
        if not menu_item:
            cursor.close()
            connection.close()
            return False, "Menu item not found"
        
        # Create the order record
        order_query = """
        INSERT INTO orders (user_id, business_id, total_amount, delivery_address, 
                           customer_name, customer_phone, customer_email, 
                           payment_method, special_instructions, discount_applied, discount_percentage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(order_query, (
            user_id, business_id, total_amount, delivery_address,
            customer_name, customer_phone, customer_email, 
            payment_method, special_instructions, discount_applied, discount_percentage
        ))
        
        # Get the new order ID
        order_id = cursor.lastrowid
        
        # Add the order item
        order_item_query = """
        INSERT INTO order_items (order_id, menu_item_id, item_name, quantity, price)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(order_item_query, (
            order_id, menu_item_id, menu_item[0], quantity, menu_item[1]
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True, order_id
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error creating order: {error_str}")
        return False, error_str

def get_orders_by_business(business_id):
    """Get all orders for a specific business"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all orders for this business - update query to include discount info
        query = """
        SELECT o.id, o.user_id, o.order_date, o.status, o.total_amount, o.delivery_address,
               o.customer_name, o.customer_phone, o.customer_email, o.payment_method,
               o.special_instructions, o.discount_applied, o.discount_percentage
        FROM orders o
        WHERE o.business_id = %s
        ORDER BY o.order_date DESC
        """
        cursor.execute(query, (business_id,))
        orders = cursor.fetchall()
        
        # For each order, get its items
        for order in orders:
            items_query = """
            SELECT oi.id, oi.menu_item_id, oi.item_name, oi.quantity, oi.price
            FROM order_items oi
            WHERE oi.order_id = %s
            """
            cursor.execute(items_query, (order['id'],))
            order['items'] = cursor.fetchall()
            
            # Add original price info if discount applied
            if order.get('discount_applied'):
                discount_percentage = float(order.get('discount_percentage', 0))
                current_amount = float(order['total_amount'])
                if discount_percentage > 0:
                    original_amount = current_amount * 100 / (100 - discount_percentage)
                    order['original_amount'] = round(original_amount, 2)
        
        cursor.close()
        connection.close()
        
        return orders
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving orders: {error_str}")
        return []

def get_orders_by_user(user_id):
    """Get all orders for a specific user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all orders for this user
        query = """
        SELECT o.id, o.business_id, b.business_name, o.order_date, o.status, 
               o.total_amount, o.delivery_address, o.payment_method,
               o.discount_applied, o.discount_percentage
        FROM orders o
        JOIN businesses b ON o.business_id = b.id
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
        """
        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()
        
        # For each order, get its items
        for order in orders:
            items_query = """
            SELECT oi.id, oi.item_name, oi.quantity, oi.price
            FROM order_items oi
            WHERE oi.order_id = %s
            """
            cursor.execute(items_query, (order['id'],))
            order['items'] = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return orders
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving user orders: {error_str}")
        return []

def update_order_status(order_id, status):
    """Update the status of an order"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "UPDATE orders SET status = %s WHERE id = %s"
        cursor.execute(query, (status, order_id))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True, "Order status updated successfully"
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error updating order status: {error_str}")
        return False, "Database error"

def get_order_by_id(order_id):
    """Get detailed information about a specific order"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get the order details
        query = """
        SELECT o.id, o.user_id, o.business_id, b.business_name, o.order_date, o.status, 
               o.total_amount, o.delivery_address, o.customer_name, o.customer_phone, 
               o.customer_email, o.payment_method, o.special_instructions,
               o.discount_applied, o.discount_percentage
        FROM orders o
        JOIN businesses b ON o.business_id = b.id
        WHERE o.id = %s
        """
        cursor.execute(query, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            connection.close()
            return None
            
        # Get the order items
        items_query = """
        SELECT id, menu_item_id, item_name, quantity, price
        FROM order_items
        WHERE order_id = %s
        """
        cursor.execute(items_query, (order_id,))
        order['items'] = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return order
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error retrieving order details: {error_str}")
        return None

def fix_menu_items_table():
    """Check and fix the menu_items table if business_id column is missing"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if business_id column exists
        cursor.execute("SHOW COLUMNS FROM menu_items LIKE 'business_id'")
        has_business_id = cursor.fetchone() is not None
        
        if not has_business_id:
            print("The business_id column is missing from menu_items table. Attempting to add it...")
            
            # Add the business_id column with a default value of 1
            cursor.execute("""
            ALTER TABLE menu_items 
            ADD COLUMN business_id INT NOT NULL DEFAULT 1,
            ADD CONSTRAINT fk_menu_business
            FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
            """)
            connection.commit()
            print("Successfully added business_id column to menu_items table.")
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        error_str = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Error fixing menu_items table: {error_str}")
        return False

def verify_student(user_id, verified=True):
    """Verify a student's ID card and make them eligible for discount"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print(f"==== STUDENT VERIFICATION ====")
        print(f"Verifying student ID for user {user_id}, setting verified to {verified}")
        
        # First update user verification status
        # Changed to allow verifying users not already marked as students
        query = """
        UPDATE users 
        SET is_student = TRUE, is_verified = %s, discount_eligible = %s
        WHERE id = %s
        """
        cursor.execute(query, (verified, verified, user_id))
        print(f"Updated user verification status. Rows affected: {cursor.rowcount}")
        
        # If verifying (not rejecting), update any existing orders to apply the discount
        if verified:
            print(f"Applying discount to existing orders for user {user_id}")
            # Get all pending and accepted orders for this user - don't limit by status
            orders_query = """
            SELECT id, total_amount, discount_applied 
            FROM orders 
            WHERE user_id = %s
            """
            cursor.execute(orders_query, (user_id,))
            orders = cursor.fetchall()
            
            print(f"Found {len(orders)} orders to update")
            
            total_updated = 0
            # Apply 50% discount to each order
            for order in orders:
                order_id = order[0]
                original_amount = float(order[1])
                discount_already_applied = order[2] if len(order) > 2 else False
                
                print(f"Processing order {order_id}: Amount: {original_amount}, Discount applied: {discount_already_applied}")
                
                if discount_already_applied:
                    print(f"Order {order_id} already has a discount applied - skipping")
                    continue
                
                # Apply 50% discount if not already applied
                discounted_amount = original_amount * 0.5
                print(f"Updating order {order_id}: Original amount: {original_amount}, Discounted: {discounted_amount}")
                
                update_query = """
                UPDATE orders 
                SET discount_applied = TRUE, 
                    discount_percentage = 50.0,
                    total_amount = %s
                WHERE id = %s
                """
                cursor.execute(update_query, (discounted_amount, order_id))
                updated_rows = cursor.rowcount
                if updated_rows > 0:
                    total_updated += 1
                print(f"Order {order_id} update attempted. Rows affected: {updated_rows}")
            
            print(f"Total orders updated with discount: {total_updated} out of {len(orders)}")
                
        connection.commit()
        print(f"Changes committed to database")
        
        cursor.close()
        connection.close()
        
        return True, "Student verification updated successfully"
            
    except Error as e:
        print(f"Error verifying student: {e}")
        return False, str(e)

def get_student_verification_requests():
    """Get all users who have submitted student ID cards but are not verified yet"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, name, email, phone, student_id_card, created_at
        FROM users
        WHERE is_student = TRUE AND student_id_card IS NOT NULL AND is_verified = FALSE
        ORDER BY created_at DESC
        """
        cursor.execute(query)
        requests = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return requests
    except Error as e:
        print(f"Error getting student verification requests: {e}")
        return []

def is_user_eligible_for_discount(user_id):
    """Check if a user is eligible for student discount"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT is_student, is_verified, discount_eligible
        FROM users
        WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            # Check if the user is a verified student or otherwise eligible for discount
            return user.get('discount_eligible', False) or (user.get('is_student', False) and user.get('is_verified', False))
        
        return False
    except Error as e:
        print(f"Error checking discount eligibility: {e}")
        return False

# Subscription management functions
def create_subscription(user_id, plan_name, plan_price):
    """Create or update a user's subscription"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if subscription table exists, create if not
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                plan_name VARCHAR(100) NOT NULL,
                plan_price DECIMAL(10, 2) NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NULL,
                status VARCHAR(20) DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            connection.commit()
        except Error as e:
            print(f"Error creating subscriptions table: {e}")
        
        # Check if user already has a subscription
        cursor.execute("SELECT id FROM subscriptions WHERE user_id = %s AND status = 'active'", (user_id,))
        existing_subscription = cursor.fetchone()
        
        if existing_subscription:
            # Update existing subscription
            subscription_id = existing_subscription[0]
            query = """
            UPDATE subscriptions
            SET plan_name = %s, plan_price = %s, start_date = CURRENT_TIMESTAMP, status = 'active'
            WHERE id = %s
            """
            cursor.execute(query, (plan_name, plan_price, subscription_id))
        else:
            # Create new subscription
            query = """
            INSERT INTO subscriptions (user_id, plan_name, plan_price)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, plan_name, plan_price))
            subscription_id = cursor.lastrowid
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True, subscription_id
    except Error as e:
        print(f"Error creating subscription: {e}")
        return False, str(e)

def get_user_subscription(user_id):
    """Get the active subscription for a user"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, plan_name, plan_price, start_date, end_date, status
        FROM subscriptions
        WHERE user_id = %s AND status = 'active'
        ORDER BY start_date DESC
        LIMIT 1
        """
        cursor.execute(query, (user_id,))
        subscription = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Format dates for JSON serialization
        if subscription and 'start_date' in subscription:
            subscription['start_date'] = subscription['start_date'].isoformat() if subscription['start_date'] else None
        if subscription and 'end_date' in subscription:
            subscription['end_date'] = subscription['end_date'].isoformat() if subscription['end_date'] else None
        
        return subscription
    except Error as e:
        print(f"Error fetching subscription: {e}")
        return None

def cancel_subscription(user_id):
    """Cancel a user's active subscription"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
        UPDATE subscriptions
        SET status = 'cancelled', end_date = CURRENT_TIMESTAMP
        WHERE user_id = %s AND status = 'active'
        """
        cursor.execute(query, (user_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
    except Error as e:
        print(f"Error cancelling subscription: {e}")
        return False

def get_all_active_subscriptions():
    """Get all active subscriptions with user details"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT s.id, s.plan_name, s.plan_price, s.start_date, s.status,
               u.id as user_id, u.name as user_name, u.email as user_email
        FROM subscriptions s
        JOIN users u ON s.user_id = u.id
        WHERE s.status = 'active'
        ORDER BY s.start_date DESC
        """
        cursor.execute(query)
        subscriptions = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Format dates for JSON serialization
        for subscription in subscriptions:
            if 'start_date' in subscription:
                subscription['start_date'] = subscription['start_date'].isoformat() if subscription['start_date'] else None
        
        return subscriptions
    except Error as e:
        print(f"Error fetching active subscriptions: {e}")
        return [] 