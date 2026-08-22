"""
database.py — Member 1

SQLite connection helper + table creation. Run once on startup (called
from app.py). Schema is adapted from the original smart-city plan to the
actual hackathon problem statement: "Smart Disaster Management and
Decision Support System".

Key changes from the generic version:
  - sensors.type now holds disaster-risk signals: 'flood', 'heatwave',
    'earthquake', 'landslide' (instead of energy/water/waste/environment)
  - events.type holds the same disaster categories, plus 'rescue' for
    situational-awareness triggers from Member 4's detection module
  - a new `resources` table tracks emergency resources (rescue teams,
    ambulances, shelters, relief supplies) and their dispatch status —
    this directly answers the problem statement's requirement to
    "recommend the optimal allocation of emergency resources"

Everyone should use get_db() from this file rather than opening their
own sqlite3 connections, so there's a single place that owns the schema.
"""

import sqlite3

DB_PATH = "smart_city.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["value"]
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,          -- 'flood', 'heatwave', 'earthquake', 'landslide'
            value REAL,
            unit TEXT,
            status TEXT,        -- 'normal' or 'alert'
            timestamp TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,          -- 'flood', 'landslide', 'heatwave', 'earthquake', 'rescue'
            location_lat REAL,
            location_lng REAL,
            description TEXT,
            status TEXT,        -- 'active' or 'resolved'
            timestamp TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_module TEXT, -- 'monitoring', 'response', 'detection'
            message TEXT,
            severity TEXT,      -- 'low', 'medium', 'high'
            timestamp TEXT
        )
    """)

    # New table vs. the original generic plan — needed for the
    # "optimal allocation of emergency resources" requirement.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,              -- 'ambulance', 'rescue_team', 'shelter', 'relief_supply'
            name TEXT,
            location_lat REAL,
            location_lng REAL,
            status TEXT,            -- 'available' or 'dispatched'
            assigned_event_id INTEGER,  -- NULL until dispatched to an event
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
