import sqlite3
import hashlib
import pandas as pd

DB_NAME = "financeify_pro.db"

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def initialize_db():
    """Creates the necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            description TEXT,
            amount REAL,
            category TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database and Tables initialized successfully!")

# --- AUTHENTICATION LOGIC ---

def hash_password(password):
    """Simple SHA-256 hashing for password security."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registers a new user into the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists

def login_user(username, password):
    """Verifies credentials and returns user_id if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT user_id FROM users WHERE username = ? AND password_hash = ?", (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# --- DATA MANAGEMENT LOGIC ---

def update_user_data(user_id, df):
    """Wipes old data and inserts a fresh import, handling case-insensitive columns."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Normalize column names to Title Case (Description, Amount, etc.)
    # This ensures it works even if the CSV has 'amount' or 'AMOUNT'
    df.columns = [c.strip().title() for c in df.columns]
    
    # 2. Clear existing data for this user
    cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    
    # 3. Insert new data
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO transactions (user_id, description, amount, category, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 
              row.get('Description', 'N/A'), 
              row.get('Amount', 0), 
              row.get('Category', 'Others'), 
              row.get('Date', 'N/A')))
    
    conn.commit()
    conn.close()
    return True

def fetch_user_data(user_id):
    """Fetches data and uses ALIASES to match the capital letters in your app.py code."""
    conn = get_connection()
    # Using 'AS' in SQL forces the DataFrame to use the names your app.py expects
    query = """
        SELECT 
            description AS Description, 
            amount AS Amount, 
            category AS Category, 
            date AS Date 
        FROM transactions 
        WHERE user_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df