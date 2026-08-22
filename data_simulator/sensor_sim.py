"""
data_simulator/sensor_sim.py — Member 2

Runs as its own process in a separate terminal:
    python data_simulator/sensor_sim.py

Pushes fake disaster-risk sensor rows into the `sensors` table every
few seconds. When a value crosses its hardcoded threshold, also inserts
into `alerts` — this is what makes threshold breaches show up in the
shared bell icon.

Sensor types are hazard readings: seismic_activity, river_level,
rainfall, heat_index.
"""

import sqlite3
import random
import time
from datetime import datetime

DB_PATH = "smart_city.db"

# type: (unit, normal_range, alert_threshold, comparison)
SENSOR_CONFIG = {
    "seismic_activity": {"unit": "magnitude", "range": (0.5, 5.0), "threshold": 4.0, "above_is_alert": True},
    "river_level":      {"unit": "cm",        "range": (5, 150),   "threshold": 120, "above_is_alert": True},
    "rainfall":         {"unit": "mm/hr",     "range": (0, 80),    "threshold": 60,  "above_is_alert": True},
    "heat_index":       {"unit": "°C",        "range": (25, 45),   "threshold": 40,  "above_is_alert": True},
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_reading(sensor_type):
    cfg = SENSOR_CONFIG[sensor_type]
    low, high = cfg["range"]
    # occasionally spike above the normal range to simulate a real risk event
    if random.random() < 0.15:
        value = round(random.uniform(cfg["threshold"], high * 1.2), 2)
    else:
        value = round(random.uniform(low, cfg["threshold"] * 0.9), 2)

    is_alert = value >= cfg["threshold"] if cfg["above_is_alert"] else value <= cfg["threshold"]
    status = "alert" if is_alert else "normal"

    return value, cfg["unit"], status


def run_simulator(interval_seconds=5):
    print(f"Sensor simulator running — writing to {DB_PATH} every {interval_seconds}s. Ctrl+C to stop.")
    while True:
        conn = get_db()
        now = datetime.now().isoformat(timespec="seconds")

        for sensor_type in SENSOR_CONFIG:
            value, unit, status = generate_reading(sensor_type)

            conn.execute(
                "INSERT INTO sensors (type, value, unit, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                (sensor_type, value, unit, status, now)
            )

            if status == "alert":
                conn.execute(
                    "INSERT INTO alerts (source_module, message, severity, timestamp) VALUES (?, ?, ?, ?)",
                    ("monitoring", f"{sensor_type.capitalize()} risk threshold breached — reading {value} {unit}", "high", now)
                )

        conn.commit()
        conn.close()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_simulator()
