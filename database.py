import sqlite3

DB_PATH = "smart_city.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
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
    print("Database created successfully!")

if __name__ == "__main__":
    init_db()