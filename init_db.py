import mysql.connector
from mysql.connector import Error
import os
import hashlib
from config import db_config
import logging

# Configure logging to file instead of console
logging.basicConfig(
    filename='db_init.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_database(verbose=False):
    """Initialize the food_website database and tables"""
    connection = None
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
            if verbose:
                print(f"Database '{db_config['database']}' checked/created successfully")
            logging.info(f"Database '{db_config['database']}' checked/created successfully")
            
            # Switch to the food_website database
            cursor.execute(f"USE {db_config['database']}")
            
            # Check if tables already exist (check for users table as indicator)
            cursor.execute("SHOW TABLES LIKE 'users'")
            tables_exist = cursor.fetchone() is not None
            
            if not tables_exist:
                # Only execute SQL setup if tables don't exist
                logging.info("Tables don't exist. Creating new tables.")
                if verbose:
                    print("Tables don't exist. Creating new tables.")
                
                # Read SQL from file and execute
                with open('database_setup.sql', 'r') as sql_file:
                    sql_script = sql_file.read()
                
                # Split SQL script into individual statements
                statements = sql_script.split(';')
                
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        try:
                            cursor.execute(statement + ';')
                            if verbose:
                                print(f"Executed: {statement[:50]}...")
                            logging.info(f"Executed: {statement[:50]}...")
                        except Error as e:
                            if verbose:
                                print(f"Error executing statement: {statement[:50]}...\nError: {e}")
                            logging.error(f"Error executing statement: {statement[:50]}...\nError: {e}")
                
                connection.commit()
                if verbose:
                    print("Database tables created successfully")
                logging.info("Database tables created successfully")
                
                # Add a test user for development - password is '123456'
                hashed_password = hashlib.sha256('123456'.encode()).hexdigest()
                try:
                    cursor.execute("""
                    INSERT INTO users (name, email, password, phone)
                    VALUES (%s, %s, %s, %s)
                    """, ('Test User', 'test@example.com', hashed_password, '+91 9876543210'))
                    connection.commit()
                    if verbose:
                        print("Test user added (email: test@example.com, password: 123456)")
                    logging.info("Test user added (email: test@example.com, password: 123456)")
                except Error as e:
                    if verbose:
                        print(f"Error adding test user: {e}")
                    logging.error(f"Error adding test user: {e}")
                    # If it's a duplicate entry error, user already exists
                    if e.errno == 1062:  # MySQL duplicate entry error code
                        if verbose:
                            print("Test user already exists, skipping.")
                        logging.info("Test user already exists, skipping.")
            else:
                if verbose:
                    print("Tables already exist. Skipping table creation.")
                logging.info("Tables already exist. Skipping table creation.")
            
    except Error as e:
        if verbose:
            print(f"Error: {e}")
        logging.error(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            if verbose:
                print("MySQL connection closed")
            logging.info("MySQL connection closed")

def reset_database(verbose=False):
    """Reset the database completely for testing"""
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
            if verbose:
                print(f"Database '{db_config['database']}' dropped")
            logging.info(f"Database '{db_config['database']}' dropped")
            connection.close()
        
        # Recreate everything
        initialize_database(verbose)
        
    except Error as e:
        if verbose:
            print(f"Error resetting database: {e}")
        logging.error(f"Error resetting database: {e}")

if __name__ == "__main__":
    # Ask the user if they want to reset the database
    choice = input("Do you want to reset the database completely? This will delete all data. (yes/no): ")
    if choice.lower() in ['yes', 'y']:
        reset_database(verbose=True)
    else:
        initialize_database(verbose=True)
    print("Database initialization complete") 