import sqlite3
import random
import time
from datetime import datetime


def add_sensor(sensor_type, value, unit, threshold):

    # Decide whether the reading is normal or an alert
    status = "alert" if value > threshold else "normal"

    # Connect to database
    conn = sqlite3.connect("smart_city.db")
    cursor = conn.cursor()

    # Store sensor reading
    cursor.execute("""
        INSERT INTO sensor_readings
        (type, value, unit, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        sensor_type,
        value,
        unit,
        status,
        datetime.now().isoformat()
    ))

    # If value is too high, create an alert
    if status == "alert":
        cursor.execute("""
            INSERT INTO alerts
            (source_module, message, severity, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            "monitoring",
            f"High {sensor_type} level detected: {value} {unit}",
            "high",
            datetime.now().isoformat()
        ))

    # Save changes
    conn.commit()
    conn.close()

    print(f"{sensor_type}: {value} {unit} → {status}")


# Keep generating readings
while True:

    energy = random.randint(200, 500)
    water = random.randint(30, 90)
    waste = random.randint(10, 100)
    environment = random.randint(20, 100)

    add_sensor("energy", energy, "kWh", 450)
    add_sensor("water", water, "PSI", 80)
    add_sensor("waste", waste, "%", 75)
    add_sensor("environment", environment, "AQI", 80)

    print("--- New readings generated ---")

    time.sleep(3)