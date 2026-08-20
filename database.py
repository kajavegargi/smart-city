import sqlite3

DB_NAME = "smart_city.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table for sensor readings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            value REAL,
            unit TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    # Table for alerts
    cursor.execute("""
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