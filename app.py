import os
import mysql.connector
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for, session, flash
from config import secret_key
import db
from werkzeug.utils import secure_filename
import time

# Create Flask app
app = Flask(__name__, static_folder=".", template_folder="templates")
app.secret_key = secret_key

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.static_folder, 'uploads', 'student_ids'), exist_ok=True)

# Check and fix database tables if needed
try:
    db.fix_menu_items_table()
except Exception as e:
    print(f"Warning: Could not fix database tables: {e}")

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/subscription.html')
def subscription_page():
    """Serve the subscription page"""
    return render_template('subscriptioncode.html')

@app.route('/payment.html')
def payment_page():
    """Serve the payment page"""
    return render_template('payment.html')

@app.route('/subscription-manage.html')
def subscription_manage_page():
    """Serve the subscription management page"""
    if 'logged_in' not in session:
        return redirect('/login.html?error=login_required&redirect=subscription-manage.html')
    return render_template('subscription-manage.html')

@app.route('/api/process-payment', methods=['POST'])
def process_payment():
    """Process subscription payment"""
    if 'logged_in' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    # Get payment details from request
    plan_name = request.form.get('plan_name')
    plan_price = request.form.get('plan_price')
    payment_method = request.form.get('payment_method', 'card')
    
    # In a real app, we would integrate with a payment gateway here
    # For now, we'll just simulate a successful payment
    
    # Record the subscription in the database
    user_id = session.get('user_id')
    try:
        # Create or update user subscription
        success, result = db.create_subscription(user_id, plan_name, plan_price)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Payment processed successfully',
                'subscription_id': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create subscription'
            }), 500
    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({
            'success': False,
            'error': 'Payment processing error'
        }), 500

@app.route('/api/subscriptions/user', methods=['GET'])
def get_user_subscription():
    """Get subscription details for the current user"""
    if 'logged_in' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_id = session.get('user_id')
    try:
        subscription = db.get_user_subscription(user_id)
        if subscription:
            return jsonify({
                'success': True,
                'subscription': subscription
            })
        else:
            return jsonify({
                'success': True,
                'subscription': None,
                'message': 'No active subscription found'
            })
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch subscription details'
        }), 500

@app.route('/api/subscriptions/cancel', methods=['POST'])
def cancel_subscription():
    """Cancel the user's subscription"""
    if 'logged_in' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_id = session.get('user_id')
    try:
        success = db.cancel_subscription(user_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Subscription cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to cancel subscription'
            }), 500
    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to cancel subscription'
        }), 500

@app.route('/admin')
def admin_redirect():
    """Redirect to admin students page for quick testing"""
    if 'logged_in' in session and session.get('account_type') == 'business' and session.get('business_id') == 1:
        return redirect('/admin-students.html')
    else:
        # For testing, we'll just redirect to the page directly without checking
        # In a production environment, this should be properly secured
        return redirect('/admin-students.html')

@app.route('/<path:filename>.html')
def serve_html(filename):
    return render_template(f'{filename}.html')

@app.route('/<path:filename>')
def serve_files(filename):
    # Only serve non-HTML files with send_from_directory
    if not filename.endswith('.html'):
        return send_from_directory('.', filename)
    return redirect(url_for('serve_html', filename=filename))

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    account_type = request.form.get('account_type', 'user')  # Default to user login
    
    if account_type == 'business':
        # Business login
        try:
            success, result = db.validate_business_login(email, password)
            
            if success:
                # Set session data
                session['business_id'] = result['id']
                session['business_email'] = result['email']
                session['business_name'] = result['business_name']
                session['account_type'] = 'business'
                session['logged_in'] = True
                
                # Redirect to business dashboard
                return redirect('/business-dashboard.html')
            else:
                # Login failed - Avoid printing potentially problematic characters
                try:
                    print("Business login failed: Invalid credentials")
                except:
                    pass
                
                # Remove pending check since all businesses are approved now
                return redirect('/login.html?error=invalid_credentials&type=business')
        except Exception as e:
            # Catch any exception that might occur
            try:
                print(f"Exception during business login: {type(e)}")
            except:
                pass
            return redirect('/login.html?error=system_error&type=business')
    else:
        # Regular user login
        try:
            success, result = db.validate_login(email, password)
            
            if success:
                # Set session data
                session['user_id'] = result['id']
                session['user_email'] = result['email']
                session['user_name'] = result['name']
                session['account_type'] = 'user'
                session['logged_in'] = True
                
                # Redirect to explore page
                return redirect('/explorecode.html')
            else:
                # Login failed
                try:
                    print("User login failed: Invalid credentials")
                except:
                    pass
                return redirect('/login.html?error=invalid_credentials')
        except Exception as e:
            # Catch any exception that might occur
            try:
                print(f"Exception during user login: {type(e)}")
            except:
                pass
            return redirect('/login.html?error=system_error')

@app.route('/api/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    is_student = 'is_student' in request.form
    student_id_card = None
    
    # Validation
    if not all([name, email, password, confirm_password]):
        return redirect('/signup.html?error=missing_fields')
    
    if password != confirm_password:
        return redirect('/signup.html?error=password_mismatch')
    
    # Handle student ID card upload if applicable
    if is_student and 'student_id_card' in request.files:
        student_id_file = request.files['student_id_card']
        if student_id_file and student_id_file.filename:
            try:
                # Save the file with a secure filename
                filename = secure_filename(f"{email}_{int(time.time())}_{student_id_file.filename}")
                upload_folder = os.path.join(app.static_folder, 'uploads', 'student_ids')
                
                # Create upload directory if it doesn't exist
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                student_id_file.save(file_path)
                student_id_card = f"uploads/student_ids/{filename}"
                print(f"Student ID card uploaded: {student_id_card}")
            except Exception as e:
                print(f"Error uploading student ID card: {e}")
                # Continue with registration even if the upload fails
    elif is_student:
        print("User marked as student but no file was uploaded")
    
    # Create new user
    success, result = db.create_user(name, email, password, phone, is_student, student_id_card)
    
    if success:
        # Log the user in
        session['user_id'] = result
        session['user_email'] = email
        session['user_name'] = name
        session['logged_in'] = True
        
        # Redirect to explore page instead of user panel
        return redirect('/explorecode.html')
    else:
        # User creation failed
        error_message = result
        print(f"Signup failed: {error_message}")
        
        # Check for specific error types
        if "already exists" in str(error_message).lower() or "duplicate" in str(error_message).lower():
            return redirect('/signup.html?error=email_exists')
        else:
            return redirect('/signup.html?error=db_error')

@app.route('/api/business-signup', methods=['POST'])
def business_signup():
    business_name = request.form.get('business_name')
    owner_name = request.form.get('owner_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    business_type = request.form.get('business_type')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if not all([business_name, owner_name, email, phone, address, business_type, password, confirm_password]):
        return redirect('/signup.html?error=missing_fields&type=business')
    
    if password != confirm_password:
        return redirect('/signup.html?error=password_mismatch&type=business')
    
    # Create new business
    success, result = db.create_business(business_name, owner_name, email, password, phone, address, business_type)
    
    if success:
        # Auto-login the business instead of showing pending message
        session['business_id'] = result
        session['business_email'] = email
        session['business_name'] = business_name
        session['account_type'] = 'business'
        session['logged_in'] = True
        
        # Redirect to business dashboard
        return redirect('/business-dashboard.html')
    else:
        # Business creation failed
        error_message = result
        try:
            print(f"Business signup failed: {error_message}")
        except:
            pass
        
        # Check for specific error types
        if "already exists" in str(error_message).lower() or "duplicate" in str(error_message).lower():
            return redirect('/signup.html?error=email_exists&type=business')
        else:
            return redirect('/signup.html?error=db_error&type=business')

@app.route('/api/logout')
def logout():
    # Clear session
    session.clear()
    return redirect('/')


@app.route('/api/user-data')
def user_data():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        user = db.get_user_by_id(user_id)
        
        if user:
            return jsonify(user)
    
    return jsonify({'error': 'Not logged in'}), 401

# API endpoints
@app.route('/api/contact', methods=['POST'])
def contact():
    # Process contact form submission
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    # Save to database
    success, result = db.save_contact_submission(name, email, phone, subject, message)
    
    if success:
        return jsonify({"status": "success", "message": "Message received!"})
    else:
        return jsonify({"status": "error", "message": result}), 500

@app.route('/api/order', methods=['POST'])
def order():
    # Process order form submission
    data = request.form
    # Here you would process the order
    print(f"Order received: {data}")
    return jsonify({"status": "success", "message": "Order received!"})

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        # Update user in database
        success, result = db.update_user(user_id, name, phone)
        
        if success:
            # Update session data
            if name:
                session['user_name'] = name
            
            return redirect('/user-panel.html')
        else:
            print(f"Profile update failed: {result}")
    
    return redirect('/login.html')

@app.route('/api/business-data')
def business_data():
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        business = db.get_business_by_id(business_id)
        
        if business:
            # Sanitize the output (remove password)
            business.pop('password', None)
            return jsonify(business)
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/menu-items', methods=['GET'])
def get_menu_items():
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        items = db.get_menu_items_by_business(business_id)
        return jsonify(items)
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/menu-items', methods=['POST'])
def add_menu_item():
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        
        # Get form data
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        category = request.form.get('category')
        
        # Validate required fields
        if not all([item_name, price]):
            return jsonify({'error': 'Item name and price are required'}), 400
        
        # Add the menu item
        success, result = db.add_menu_item(business_id, item_name, description, price, image_url, category)
        
        if success:
            return jsonify({'success': True, 'item_id': result})
        else:
            return jsonify({'error': result}), 500
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/menu-items/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        
        # Verify the item belongs to this business
        item = db.get_menu_item_by_id(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
            
        # Skip the business_id check if it doesn't exist in the item
        if 'business_id' in item and item['business_id'] != business_id:
            return jsonify({'error': 'Access denied - item belongs to another business'}), 403
        
        # Get form data
        data = request.json
        
        # Update the menu item
        success, result = db.update_menu_item(
            item_id,
            item_name=data.get('item_name'),
            description=data.get('description'),
            price=data.get('price'),
            image_url=data.get('image_url'),
            is_available=data.get('is_available'),
            category=data.get('category')
        )
        
        if success:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'error': result}), 500
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/menu-items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        
        # Verify the item belongs to this business
        item = db.get_menu_item_by_id(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
            
        # Skip the business_id check if it doesn't exist in the item
        if 'business_id' in item and item['business_id'] != business_id:
            return jsonify({'error': 'Access denied - item belongs to another business'}), 403
        
        # Delete the menu item
        success, result = db.delete_menu_item(item_id)
        
        if success:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'error': result}), 500
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/all-menu-items', methods=['GET'])
def get_all_menu_items():
    """Get all available menu items from all businesses for the explore page"""
    try:
        # Get menu items from all approved businesses
        items = db.get_all_menu_items()
        return jsonify(items)
    except Exception as e:
        print(f"Error fetching all menu items: {e}")
        return jsonify({'error': 'Failed to load menu items'}), 500

@app.route('/api/menu-item/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get details of a specific menu item"""
    try:
        item = db.get_menu_item_by_id(item_id)
        if item:
            # Get business name for this item if business_id exists
            if 'business_id' in item and item['business_id']:
                business = db.get_business_by_id(item['business_id'])
                if business:
                    item['business_name'] = business['business_name']
                else:
                    item['business_name'] = 'Unknown Business'
            else:
                # If business_id is not available, set a default business name
                item['business_name'] = 'Unknown Business'
            return jsonify(item)
        else:
            return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        print(f"Error fetching menu item: {e}")
        return jsonify({'error': 'Failed to load item details'}), 500

@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Create a new order"""
    try:
        # Get form data
        menu_item_id = request.form.get('menu_item_id')
        quantity = int(request.form.get('quantity', 1))
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        customer_email = request.form.get('customer_email')
        delivery_address = request.form.get('delivery_address')
        payment_method = request.form.get('payment_method', 'Cash on Delivery')
        special_instructions = request.form.get('special_instructions')
        
        # Validate required fields
        if not all([menu_item_id, customer_name, customer_phone, customer_email, delivery_address]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get menu item details
        menu_item = db.get_menu_item_by_id(menu_item_id)
        if not menu_item:
            return jsonify({'error': 'Menu item not found'}), 404
        
        # Calculate total amount
        total_amount = float(menu_item['price']) * quantity
        
        # Get user ID from session (or use guest ID if not logged in)
        user_id = session.get('user_id', 1)  # Default to ID 1 for guests
        
        # Get business_id from menu_item if it exists
        business_id = None
        if 'business_id' in menu_item:
            business_id = menu_item['business_id']
        
        # If business_id is not in the menu_item, we need to query it from the database
        if business_id is None:
            try:
                connection = db.get_db_connection()
                cursor = connection.cursor(dictionary=True)
                
                # Query to get the business_id for this menu item
                query = """
                SELECT business_id 
                FROM menu_items 
                WHERE id = %s
                """
                cursor.execute(query, (menu_item_id,))
                result = cursor.fetchone()
                
                if result and 'business_id' in result:
                    business_id = result['business_id']
                else:
                    # If still no business_id, default to 1
                    business_id = 1
                    print("Warning: Could not find business_id for menu_item_id. Using default business_id=1.")
                
                cursor.close()
                connection.close()
            except Exception as e:
                print(f"Error fetching business_id: {e}")
                # Default to business ID 1 if we couldn't get the business_id
                business_id = 1
                print("Warning: Error looking up business_id. Using default business_id=1.")
        
        # Create the order
        success, result = db.create_order(
            user_id, 
            business_id,
            menu_item_id,
            quantity,
            total_amount,
            customer_name,
            customer_phone,
            customer_email,
            delivery_address,
            payment_method,
            special_instructions
        )
        
        if success:
            return jsonify({
                'success': True, 
                'order_id': result,
                'message': 'Order placed successfully!'
            })
        else:
            return jsonify({'error': result}), 500
            
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({'error': 'Failed to place order'}), 500

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    """Get all orders for the logged-in user"""
    if 'logged_in' in session and session['logged_in']:
        user_id = session['user_id']
        orders = db.get_orders_by_user(user_id)
        return jsonify(orders)
    
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/business/orders', methods=['GET'])
def get_business_orders():
    """Get all orders for the logged-in business"""
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        orders = db.get_orders_by_business(business_id)
        return jsonify(orders)
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/api/order/update-status', methods=['POST'])
def update_order_status():
    """Update the status of an order"""
    if 'logged_in' in session and session.get('account_type') == 'business':
        business_id = session['business_id']
        
        order_id = request.form.get('order_id')
        status = request.form.get('status')
        
        # Validate inputs
        if not all([order_id, status]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Make sure the status is valid
        valid_statuses = ['pending', 'accepted', 'preparing', 'out_for_delivery', 'delivered', 'cancelled']
        if status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
            
        # Update the order status
        success, result = db.update_order_status(order_id, status)
        
        if success:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'error': result}), 500
    
    return jsonify({'error': 'Not logged in or not a business account'}), 401

@app.route('/business-dashboard.html')
def business_dashboard():
    if 'logged_in' in session and session.get('account_type') == 'business':
        return render_template('business-dashboard.html')
    else:
        return redirect('/login.html?error=not_logged_in&type=business')

@app.route('/api/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get details for a specific order"""
    # Check if user is logged in or if viewing a shared order link
    # This could be enhanced with proper security checks
    
    order = db.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order)

@app.route('/api/admin/verify-student/<int:user_id>', methods=['POST'])
def verify_student(user_id):
    """Admin route to verify student ID and enable discount"""
    if 'logged_in' in session and session.get('account_type') == 'business' and session.get('business_id') == 1:
        # Only the main admin business account (ID 1) can verify students
        try:
            verified = request.form.get('verified', 'true').lower() == 'true'
            print(f"Verification request received for user {user_id}, verified={verified}")
            
            # Additional check to make sure user exists
            user = db.get_user_by_id(user_id)
            if not user:
                print(f"User {user_id} not found")
                return jsonify({'error': 'User not found'}), 404
                
            success, message = db.verify_student(user_id, verified)
            
            if success:
                # Force refresh of orders data
                print(f"Verification successful: {message}")
                return jsonify({'success': True, 'message': message})
            else:
                print(f"Verification failed: {message}")
                return jsonify({'error': message}), 500
        except Exception as e:
            print(f"Exception during student verification: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@app.route('/api/admin/student-verification-requests', methods=['GET'])
def get_student_verification_requests():
    """Get all pending student verification requests"""
    if 'logged_in' in session and session.get('account_type') == 'business' and session.get('business_id') == 1:
        # Only the main admin business account (ID 1) can see verification requests
        requests = db.get_student_verification_requests()
        return jsonify(requests)
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@app.route('/api/user/submit-student-id', methods=['POST'])
def submit_student_id():
    """Allow users to submit their student ID after registration"""
    if 'logged_in' in session and session.get('account_type') == 'user':
        user_id = session['user_id']
        
        if 'student_id_card' in request.files:
            student_id_file = request.files['student_id_card']
            if student_id_file and student_id_file.filename:
                # Save the file with a secure filename
                email = session['user_email']
                filename = secure_filename(f"{email}_{int(time.time())}_{student_id_file.filename}")
                upload_folder = os.path.join(app.static_folder, 'uploads', 'student_ids')
                
                # Create upload directory if it doesn't exist
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                student_id_file.save(file_path)
                student_id_card = f"uploads/student_ids/{filename}"
                
                # Update user record to indicate they're a student with pending verification
                connection = db.get_db_connection()
                cursor = connection.cursor()
                
                query = """
                UPDATE users 
                SET is_student = TRUE, student_id_card = %s, is_verified = FALSE
                WHERE id = %s
                """
                cursor.execute(query, (student_id_card, user_id))
                connection.commit()
                
                cursor.close()
                connection.close()
                
                return redirect('/user-panel.html?message=student_id_submitted')
            
        return redirect('/user-panel.html?error=no_file')
    else:
        return redirect('/login.html')

@app.route('/student-verification.html')
def student_verification_page():
    """Alias for admin-students.html for better naming in dashboard"""
    # Check if the user is logged in as a business admin
    if 'logged_in' in session and session.get('account_type') == 'business' and session.get('business_id') == 1:
        return send_from_directory('templates', 'admin-students.html')
    else:
        return redirect('/admin-login.html?error=not_logged_in')

@app.route('/admin-students.html')
def admin_students_page():
    """Serve the admin page for student verification"""
    # Check if the user is logged in as a business admin
    if 'logged_in' in session and session.get('account_type') == 'business' and session.get('business_id') == 1:
        return send_from_directory('templates', 'admin-students.html')
    else:
        return redirect('/admin-login.html?error=not_logged_in')

@app.route('/order-details.html')
def order_details_page():
    """Serve the order details page"""
    return send_from_directory('templates', 'order-details.html')

@app.route('/track-order-details.html')
def track_order_details_page():
    """Serve the detailed order tracking page with OpenStreetMap integration"""
    return render_template('track-order-details.html')

@app.route('/test-student-upload')
def test_student_upload():
    """A simple route for testing the student ID upload form"""
    return send_from_directory('.', 'test-student-upload.html')

@app.route('/admin-login.html')
def admin_login_page():
    """Serve the admin login page"""
    return send_from_directory('.', 'admin-login.html')

@app.route('/api/restart-app', methods=['POST'])
def restart_app():
    """Endpoint to restart the Flask app (development only)"""
    # This doesn't actually restart the app, but we'll return success anyway
    return jsonify({"success": True, "message": "App restart initiated"})

@app.route('/templates/track-order-details.html')
def templates_track_order_details_page():
    """Handle legacy URLs that might still include /templates/ prefix"""
    return render_template('track-order-details.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 