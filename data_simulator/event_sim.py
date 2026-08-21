"""
data_simulator/event_sim.py — Member 3

Two ways to use this:
1. Call simulate_event() from a Flask route when the user clicks "Simulate Event" in the UI.
2. Run this file directly to drop one fake event on a loop (optional, for background demo noise).

Also exposes CURRENT_BLOCKED_NODE so the /api/route endpoint can reroute around
whatever node the latest active event is sitting on.
"""

import sqlite3
import random
import time
from datetime import datetime

DB_PATH = "smart_city.db"  # adjust if your database.py uses a different path/const

EVENT_TYPES = ["traffic", "security", "health"]

TRAFFIC_DESCRIPTIONS = [
    "Traffic congestion at Node {node}",
    "Accident reported near Node {node}",
    "Road closure at Node {node}",
]
SECURITY_DESCRIPTIONS = [
    "Suspicious activity reported near Node {node}",
    "Security alert triggered at Node {node}",
]
HEALTH_DESCRIPTIONS = [
    "Medical emergency reported near Node {node}",
    "E-health dispatch requested at Node {node}",
]

# Node ids should match routing.py's NODES keys
NODE_IDS = ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"]

# Module-level state: which node (if any) is currently "blocked" by an active event.
# app.py's /api/route reads this to reroute around it.
CURRENT_BLOCKED_NODE = None


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _severity_for(event_type):
    return {"traffic": "medium", "security": "high", "health": "high"}.get(event_type, "low")


def simulate_event(event_type=None, node_id=None):
    """
    Inserts one fake event row + a matching alert row.
    Call this from a Flask route (button click) or Member 4's YOLO trigger.
    Returns the event dict that was inserted.
    """
    global CURRENT_BLOCKED_NODE

    from routing import node_coords  # local import avoids circulars at module load

    event_type = event_type or random.choice(EVENT_TYPES)
    node_id = node_id or random.choice(NODE_IDS)
    lat, lng = node_coords(node_id)

    if event_type == "traffic":
        description = random.choice(TRAFFIC_DESCRIPTIONS).format(node=node_id)
        CURRENT_BLOCKED_NODE = node_id  # only traffic events block routing
    elif event_type == "security":
        description = random.choice(SECURITY_DESCRIPTIONS).format(node=node_id)
    else:
        description = random.choice(HEALTH_DESCRIPTIONS).format(node=node_id)

    timestamp = datetime.now().isoformat()

    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO events (type, location_lat, location_lng, description, status, timestamp)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event_type, lat, lng, description, "active", timestamp),
    )
    event_id = cur.lastrowid

    cur.execute(
        """INSERT INTO alerts (source_module, message, severity, timestamp)
           VALUES (?, ?, ?, ?)""",
        ("response", description, _severity_for(event_type), timestamp),
    )
    conn.commit()
    conn.close()

    return {
        "id": event_id,
        "type": event_type,
        "location_lat": lat,
        "location_lng": lng,
        "description": description,
        "status": "active",
        "timestamp": timestamp,
        "blocked_node": node_id,
    }


def resolve_event(event_id):
    """Mark an event resolved and clear the routing block if it was the blocking one."""
    global CURRENT_BLOCKED_NODE
    conn = _get_conn()
    conn.execute("UPDATE events SET status = 'resolved' WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    CURRENT_BLOCKED_NODE = None


if __name__ == "__main__":
    # Optional: run standalone to generate background event noise every ~20-40s
    while True:
        e = simulate_event()
        print(f"[event_sim] inserted: {e['description']}")
        time.sleep(random.randint(20, 40))