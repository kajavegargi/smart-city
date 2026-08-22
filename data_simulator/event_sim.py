"""
data_simulator/event_sim.py — Member 3

Two ways to fire an event:
  1. Run this file directly — fires one random disaster event and exits.
     Good for a "Simulate Event" button calling this via subprocess, or
     for quick testing.
  2. Import simulate_disaster_event() from app.py / a route and call it
     on a button click from response.html — this is the recommended
     approach for a live demo (button-triggered, not a background loop).

Also exposes simulate_disaster_event() as the SINGLE function Member 4's
detect_routes.py should call once this file exists, instead of Member 4
inserting into events/alerts directly — see the note in detect_routes.py.

Every event insert also triggers a resource dispatch via routing.py, so
firing an event immediately shows a rescue team/ambulance/shelter being
assigned on the response map.
"""

import sqlite3
import random
from datetime import datetime
from routing import CITY_NODES, dispatch_nearest_resource

DB_PATH = "smart_city.db"

DISASTER_TYPES = ["flood", "landslide", "earthquake", "heatwave"]

DESCRIPTIONS = {
    "flood": "Rising water levels reported, possible evacuation needed",
    "landslide": "Slope failure reported, road access may be blocked",
    "earthquake": "Seismic activity reported, structural damage possible",
    "heatwave": "Extreme heat reported, vulnerable residents at risk",
    "rescue": "Possible stranded people detected, rescue may be needed",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def simulate_disaster_event(disaster_type=None, node_id=None, description_override=None, severity_override=None):
    """
    Inserts one disaster event at a mock city node, inserts a matching
    alert, and dispatches the nearest available resource to it.

    disaster_type: one of DISASTER_TYPES (or 'rescue'), random if not given
    node_id: which mock city node it happens at, random if not given
    description_override / severity_override: used by Member 4's
        detection route to pass in detection-specific details instead
        of the generic canned description/severity.

    Returns the inserted event's id.
    """
    disaster_type = disaster_type or random.choice(DISASTER_TYPES)
    node = CITY_NODES[node_id] if node_id else random.choice(list(CITY_NODES.values()))
    description = description_override or DESCRIPTIONS[disaster_type]
    severity = severity_override or "high"

    conn = get_db()
    now = datetime.now().isoformat(timespec="seconds")

    cur = conn.execute(
        "INSERT INTO events (type, location_lat, location_lng, description, status, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (disaster_type, node["lat"], node["lng"], description, "active", now)
    )
    event_id = cur.lastrowid

    conn.execute(
        "INSERT INTO alerts (source_module, message, severity, timestamp) VALUES (?, ?, ?, ?)",
        ("response", f"{disaster_type.capitalize()} event at {node['name']} — {description}", severity, now)
    )

    conn.commit()
    conn.close()

    # Immediately try to dispatch a resource — this is the "optimal
    # allocation of emergency resources" part of the problem statement.
    dispatch_nearest_resource(event_id, node)

    return event_id


if __name__ == "__main__":
    event_id = simulate_disaster_event()
    print(f"Simulated disaster event #{event_id}")
