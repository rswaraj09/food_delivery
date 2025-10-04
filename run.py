import os
import shutil
import sys
import subprocess
import importlib.util
import webbrowser
import time
import threading

def setup():
    # Create symbolic links or copy files if they don't exist
    if not os.path.exists('swift.css') or os.path.getsize('swift.css') < 100:
        if os.path.exists('swift.csscode.css'):
            print("Copying swift.csscode.css to swift.css...")
            shutil.copy('swift.csscode.css', 'swift.css')
        else:
            print("Warning: swift.csscode.css not found!")
    
    if not os.path.exists('script.js') or os.path.getsize('script.js') < 100:
        if os.path.exists('script.jscode.html'):
            print("Copying script.jscode.html to script.js...")
            # Extract JavaScript content from the HTML file
            with open('script.jscode.html', 'r') as f:
                content = f.read()
            
            # Write to script.js
            with open('script.js', 'w') as f:
                f.write(content)
        else:
            print("Warning: script.jscode.html not found!")

    # Install dependencies if needed
    if not os.path.exists('venv'):
        print("Setting up virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'virtualenv'], check=True)
            subprocess.run([sys.executable, '-m', 'virtualenv', 'venv'], check=True)
            
            # Activate and install requirements
            if os.name == 'nt':  # Windows
                activate_script = os.path.join('venv', 'Scripts', 'activate')
                pip_path = os.path.join('venv', 'Scripts', 'pip')
            else:  # Unix/Linux
                activate_script = os.path.join('venv', 'bin', 'activate')
                pip_path = os.path.join('venv', 'bin', 'pip')
            
            subprocess.run(f"{pip_path} install -r requirements.txt", shell=True, check=True)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error setting up environment: {e}")
            return False
    
    # Initialize the database
    print("Initializing database...")
    try:
        if os.path.exists('init_db.py'):
            spec = importlib.util.spec_from_file_location("init_db", "init_db.py")
            init_db = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(init_db)
            
            # Always call initialize_database which now checks for existing tables
            # before creating new ones, preserving data if tables exist
            print("Connecting to database...")
            init_db.initialize_database(verbose=True)
            
            # Create marker file if it doesn't exist (just for tracking first run)
            if not os.path.exists('.db_initialized'):
                with open('.db_initialized', 'w') as f:
                    f.write('Database initialized')
        else:
            print("Warning: init_db.py not found! Database will not be initialized.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("You can continue but some features might not work correctly.")
    
    return True

def run_app():
    if not setup():
        print("Setup failed. Please resolve the issues and try again.")
        return

    print("Starting the Flask application...")
    try:
        # Function to open browser after a delay
        def open_browser():
            time.sleep(1.5)  # Wait for Flask to start
            print("Opening Chrome browser...")
            url = "http://localhost:5000/explorecode.html"
            # Try to open with Chrome/Chromium
            chrome_path = ""
            if sys.platform.startswith('win'):
                chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
            elif sys.platform.startswith('darwin'):
                chrome_path = 'open -a "Google Chrome" %s'
            elif sys.platform.startswith('linux'):
                chrome_path = '/usr/bin/google-chrome %s'
            
            try:
                if chrome_path:
                    webbrowser.get(chrome_path).open(url)
                else:
                    webbrowser.open(url)
            except webbrowser.Error:
                # Fallback to default browser if Chrome is not available
                webbrowser.open(url)
        
        # Start browser opening in a separate thread
        threading.Thread(target=open_browser).start()
        
        # Run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error running the application: {e}")

if __name__ == "__main__":
    # Check if the user wants to reset the database
    if len(sys.argv) > 1 and sys.argv[1] == "--reset-db":
        if os.path.exists('.db_initialized'):
            os.remove('.db_initialized')
        print("Database reset flag detected. Database will be reset on startup.")
    
    run_app() 