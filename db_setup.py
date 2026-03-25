import sqlite3

def create_database():
    # Connect to (or create) the finance database file
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # 1. Users Table (New)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT UNIQUE)''')

    # 2. Categories Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE)''')

    # 3. Budgets Table (New - Connects Category to a Limit)
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_id INTEGER,
                        monthly_limit REAL,
                        FOREIGN KEY (category_id) REFERENCES categories (id))''')

    # 4. Transactions Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        description TEXT,
                        amount REAL,
                        category_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (category_id) REFERENCES categories (id))''')

    # Add some starter data so the tables aren't empty for the demo
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('Student_User', 'student@cvraman.edu')")
    
    starter_categories = [('Food',), ('Transport',), ('Bills',), ('Shopping',)]
    cursor.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', starter_categories)

    conn.commit()
    conn.close()
    print("✅ Day 1 Full Success: All 4 tables (Users, Categories, Budgets, Transactions) are ready!")

if __name__ == "__main__":
    create_database()