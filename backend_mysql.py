import mysql.connector
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime  # For session_id generation

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- CRITICAL: UPDATE THESE CONFIGURATION DETAILS WITH YOUR MYSQL SETUP ---
DB_CONFIG = {
    'host': 'localhost',        # Usually 'localhost' or '127.0.0.1'
    'user': 'root',             # Your MySQL username (default: root)
    'password': '@Aruna123',    # CHANGE THIS to your actual MySQL root password (e.g., 'password123')
    'database': 'mockmate'      # Database name—will be created if missing
}
# ----------------------------------------------------

# Global connection function with auto-setup
def get_db_connection():
    try:
        # First, ensure database exists
        temp_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        temp_cursor.close()
        temp_conn.close()
        
        print(f"Database '{DB_CONFIG['database']}' ensured to exist.")
        
        # Now connect to the database and ensure table exists
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create USERS table if not exists (with session_id column)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS USERS (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            target_role VARCHAR(255) NOT NULL,
            target_company VARCHAR(255) NULL,
            session_id VARCHAR(255) UNIQUE NULL,  -- Unique session ID (timestamp_userid)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        
        print("USERS table ensured to exist (with session_id).")
        return conn
        
    except mysql.connector.Error as err:
        print(f"Database Setup/Connection Error: {err}")
        raise

# Serve static files (HTML, CSS, JS)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/interview')
def interview():
    return send_from_directory('.', 'interview.html')

@app.route('/report')
def report():
    return send_from_directory('.', 'report.html')

# API endpoint to add user (POST /api/user) - Generates unique session_id
@app.route('/api/user', methods=['POST'])
def add_user():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Request must be JSON.'}), 400
    
    data = request.json
    print(f"Received POST data: {data}")  # Debug log
    
    # Validate required fields
    username = data.get('username', '').strip()
    target_role = data.get('target_role', '').strip()
    target_company = data.get('target_company', '').strip()
    password_hash = data.get('password_hash', '')  # Expected: 'default_mockmate_hash'
    
    # Handle empty company as None (for SQL NULL)
    if not target_company:
        target_company = None
    
    if not (username and target_role and password_hash):
        return jsonify({'status': 'error', 'message': 'Missing required fields: username, target_role, password_hash.'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert user first (to get user_id)
        sql_insert = "INSERT INTO USERS (username, password_hash, target_role, target_company) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert, (username, password_hash, target_role, target_company))
        user_id = cursor.lastrowid
        conn.commit()
        
        # Generate unique session_id: timestamp + user_id
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        session_id = f"{timestamp}_{user_id}"
        
        # Update the row with session_id
        sql_update = "UPDATE USERS SET session_id = %s WHERE user_id = %s"
        cursor.execute(sql_update, (session_id, user_id))
        conn.commit()
        cursor.close()
        
        print(f"User  inserted successfully. ID: {user_id}, Username: {username}, Session ID: {session_id}")  # Debug log
        return jsonify({'user_id': user_id, 'session_id': session_id, 'status': 'created'}), 201
        
    except mysql.connector.IntegrityError as err:
        print(f"Integrity Error (e.g., duplicate username/session): {err}")
        return jsonify({'status': 'error', 'message': 'Username already exists. Please choose a unique username.'}), 409
    except mysql.connector.Error as err:
        print(f"Database Insertion Error: {err}")
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    except Exception as e:
        print(f"Unexpected Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error.'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# GET endpoint to list users (includes session_id for testing)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT user_id, username, target_role, target_company, session_id, created_at FROM USERS ORDER BY created_at DESC')
        users = cursor.fetchall()
        cursor.close()
        print(f"Fetched {len(users)} users.")  # Debug log
        return jsonify(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'status': 'error', 'message': 'Could not fetch users.'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# Placeholder endpoints (as in original)
@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify({"message": "Question fetching not yet implemented"}), 200

@app.route('/api/rounds', methods=['GET'])
def get_rounds():
    return jsonify({"message": "Round fetching not yet implemented"}), 200

# API endpoint for saving interview data (handles session_id)
@app.route('/api/save', methods=['POST'])
def save_data():
    data = request.json
    session_id = data.get('session_id')  # Expect session_id in payload
    print(f"Saving interview data for session {session_id}: {data}")  # Debug log
    # TODO: Save to DB (e.g., new table linking to session_id)
    return jsonify({'status': 'success', 'data': data, 'session_id': session_id})

if __name__ == '__main__':
    print("Starting MockMate Backend...")
    try:
        # Test initial connection on startup
        get_db_connection()  # This will create DB/table if needed
        print("Database connection successful. Backend ready!")
    except Exception as e:
        print(f"Startup failed - Fix DB issues first: {e}")
        print("Tip: Check MySQL is running and update DB_CONFIG password.")
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)
