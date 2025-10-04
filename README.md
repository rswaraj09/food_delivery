# Swift Serve - Food Delivery Web Application

A web application for food delivery service with a Flask backend and MySQL database.


1. Make sure you have MySQL installed and running on your system.

2. Modify the database configuration in `config.py` to match your MySQL credentials:
   ```python
   db_config = {
       'host': 'localhost',
       'user': 'root',  # Replace with your MySQL username
       'password': '',  # Replace with your MySQL password
       'database': 'food_website'
   }
   ```

3. Install Python requirements:
   ```
   pip install -r requirements.txt
   ```

4. Run the application using the run script (which will create the database and tables automatically):
   ```
   python run.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Default Test User

A test user is automatically created in the database:
- Email: test@example.com
- Password: 123456

## Feature

- Responsive frontend with multiple pages
- User authentication (login/signup)
- User profile management
- Backend API for form submissions
- Contact form with backend processing
- Order form with backend processing
- MySQL database integration

## Project Structure

- `index.html` - Main frontend page
- `login.html` - User login page
- `signup.html` - User registration page
- `user-panel.html` - User dashboard
- `app.py` - Flask backend application
- `db.py` - Database helper functions
- `config.py` - Configuration settings
- `init_db.py` - Database initialization script
- `database_setup.sql` - SQL schema
- `run.py` - Application runner script
- `swift.css` - CSS styling
- `script.js` - JavaScript functionality 
