import sqlite3

def setup_database():
    conn = sqlite3.connect('bus_reservation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            phone_number TEXT,
            gender TEXT,
            balance REAL DEFAULT 0.0,
            name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY,
            bus_number TEXT NOT NULL,
            route TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            time TEXT,
            price REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER,
            username TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            seats_reserved INTEGER NOT NULL,
            plan TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (bus_id) REFERENCES buses (id)
        )
    ''')
    
    conn.commit()
    conn.close()
