import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CRITICAL: VERIFY THESE CONFIGURATION DETAILS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # Ensure this matches your MySQL username
    'password': '@Aruna123',         # Ensure this matches your MySQL password
    'database': 'mockmate'  # Ensure this database exists and is active
}
# ----------------------------------------------------

def get_db_connection():
    try:
        # We return the connection, any failure here will be caught in the API route
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        # Raising the error so Flask can return a 500 status
        raise

@app.route('/')
def home():
    return 'MockMate Flask + MySQL Backend Running!'

@app.route('/api/user', methods=['POST'])
def add_user():
    data = request.json
    
    # CRITICAL: Validate required fields based on the USERS table structure
    username = data.get('username')
    target_role = data.get('target_role')
    target_company = data.get('target_company')
    password_hash = data.get('password_hash') # Sent as 'default_mockmate_hash' from the frontend
    
    # --- FIX 1: Ensure empty strings for target_company are treated as NULL ---
    # Python 'None' maps directly to SQL 'NULL', resolving potential insertion errors.
    if target_company == "":
        target_company = None
    # ------------------------------------------------------------------------
    
    if not (username and target_role and password_hash):
        return jsonify({'status': 'error', 'message': 'Missing required user fields.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "INSERT INTO USERS (username, password_hash, target_role, target_company) VALUES (%s, %s, %s, %s)"
        
        cursor.execute(sql, (
            username,
            password_hash,
            target_role,
            target_company
        ))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({'user_id': user_id, 'status': 'created'}), 201

    except mysql.connector.Error as err:
        # Log the specific database error for debugging
        print(f"Database Insertion Error: {err}")
        return jsonify({'status': 'error', 'message': f'Database error: {err.msg}'}), 500
    except Exception as e:
        # Catch other errors (e.g., connection failure)
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error.'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# Include other necessary endpoints for completeness (optional for the current bug fix)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Select specific columns to avoid errors if new columns were added later
        cursor.execute('SELECT user_id, username, target_role, target_company, created_at FROM USERS')
        users = cursor.fetchall()
        cursor.close()
        return jsonify(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': 'Could not fetch users.'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/questions', methods=['GET'])
def get_questions():
    # Placeholder for future logic
    return jsonify({"message": "Question fetching not yet implemented"}), 200

@app.route('/api/rounds', methods=['GET'])
def get_rounds():
    # Placeholder for future logic
    return jsonify({"message": "Round fetching not yet implemented"}), 200

if __name__ == '__main__':
    app.run(debug=True)
