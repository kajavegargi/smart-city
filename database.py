import sqlite3

DB_PATH = "smart_city.db"

def get_db():                               #function definition
    conn = sqlite3.connect(DB_PATH)         #opens/creates db file and returns connection object
    conn.row_factory = sqlite3.Row          #row conversion to behave like dictionaries
    return conn                             #return connection

def init_db():
    conn = get_db()
    cur = conn.cursor()       #actually responsible for running SQL commands

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            value REAL,
            unit TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            location_lat REAL,
            location_lng REAL,
            description TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_module TEXT,
                message TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)

    conn.commit()
    conn.close()
    