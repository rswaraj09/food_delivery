# Database configuration settings
import secrets

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # Enter your MySQL password here
    'database': 'swift_serves'
}

# Flask Configuration
secret_key = secrets.token_hex(16) 