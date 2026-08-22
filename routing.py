"""
routing.py — Member 3

Two responsibilities, both from the problem statement:
  1. Rescue pathfinding: a small mock city graph (nodes with coordinates)
     + Dijkstra to compute the fastest path for a rescue team (or other
     emergency resource) to reach a disaster incident. Optional blocked
     nodes can be excluded (e.g. flooded or landslide-cut junctions).
  2. Resource allocation: pick the nearest available resource
     (ambulance, rescue team, shelter, relief supply) and dispatch it
     to an active incident — this is the "recommend the optimal
     allocation of emergency resources" requirement.

Kept deliberately simple (graph travel time, not real road networks)
since this only needs to demo well, not be production-grade.
"""

import sqlite3
import heapq
import math
from database import get_db
from datetime import datetime, timedelta

EVENT_RESOLVE_SECONDS = 10  # events auto-resolve 60s after creation, freeing their resource
DB_PATH = "smart_city.db"

def resolve_expired_events():
    """Mark events older than EVENT_RESOLVE_SECONDS as resolved, and release
    whichever resource was dispatched to each one back to 'available'."""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(seconds=EVENT_RESOLVE_SECONDS)).isoformat()

    expired = conn.execute(
        "SELECT id FROM events WHERE status = 'active' AND timestamp < ?",
        (cutoff,)
    ).fetchall()

    for event in expired:
        event_id = event["id"]
        conn.execute(
            "UPDATE events SET status = 'resolved' WHERE id = ?", (event_id,)
        )
        conn.execute(
            "UPDATE resources SET status = 'available', assigned_event_id = NULL "
            "WHERE assigned_event_id = ?",
            (event_id,)
        )

    conn.commit()
    conn.close()

# Mock incident map — 8 nodes with coordinates (lat, lng), loosely spread
# around a city center so rescue dispatch looks reasonable on the map.
CITY_NODES = {
    "N1": {"name": "City Center",      "lat": 12.9716, "lng": 77.5946},
    "N2": {"name": "Riverside",        "lat": 12.9800, "lng": 77.6050},
    "N3": {"name": "Hillview",         "lat": 12.9600, "lng": 77.5800},
    "N4": {"name": "North District",   "lat": 13.0000, "lng": 77.5900},
    "N5": {"name": "South District",   "lat": 12.9400, "lng": 77.6000},
    "N6": {"name": "East Market",      "lat": 12.9750, "lng": 77.6200},
    "N7": {"name": "West Residential", "lat": 12.9650, "lng": 77.5600},
    "N8": {"name": "Old Town",         "lat": 12.9550, "lng": 77.5950},
}

# Adjacency list with edge weights (mock rescue travel time in minutes)
CITY_EDGES = {
    "N1": {"N2": 6, "N3": 5, "N8": 4},
    "N2": {"N1": 6, "N4": 7, "N6": 5},
    "N3": {"N1": 5, "N7": 6, "N8": 3},
    "N4": {"N2": 7, "N6": 8},
    "N5": {"N8": 5, "N6": 9},
    "N6": {"N2": 5, "N4": 8, "N5": 9},
    "N7": {"N3": 6, "N8": 7},
    "N8": {"N1": 4, "N3": 3, "N5": 5, "N7": 7},
}


def get_route_to_event(start_node_id, end_node_id, blocked_nodes=None):
    """
    Fastest rescue path from a resource's node to an incident node.

    Uses Dijkstra on the mock city graph. `blocked_nodes` is an optional
    iterable of node ids to skip (impassable junctions); defaults to none.

    Returns (list_of_node_ids, total_travel_minutes) or (None, inf)
    if the incident is unreachable.
    """
    blocked = set(blocked_nodes or ())
    if start_node_id in blocked or end_node_id in blocked:
        return None, math.inf

    distances = {node: math.inf for node in CITY_NODES}
    distances[start_node_id] = 0
    previous = {}
    visited = set()
    queue = [(0, start_node_id)]

    while queue:
        current_dist, current_node = heapq.heappop(queue)
        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end_node_id:
            break

        for neighbor, weight in CITY_EDGES.get(current_node, {}).items():
            if neighbor in blocked:
                continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(queue, (new_dist, neighbor))

    if distances[end_node_id] == math.inf:
        return None, math.inf

    rescue_path = [end_node_id]
    while rescue_path[-1] != start_node_id:
        rescue_path.append(previous[rescue_path[-1]])
    rescue_path.reverse()
    return rescue_path, distances[end_node_id]


def _nearest_node(lat, lng):
    """Snap an arbitrary lat/lng to the closest mock map node."""
    best_node, best_dist = None, math.inf
    for node_id, node in CITY_NODES.items():
        dist = math.hypot(node["lat"] - lat, node["lng"] - lng)
        if dist < best_dist:
            best_node, best_dist = node_id, dist
    return best_node


def dispatch_nearest_resource(event_id, event_node):
    """
    Finds the nearest AVAILABLE emergency resource to the incident,
    marks it 'dispatched' and assigns it to this event. Called
    automatically by event_sim.py whenever a new disaster incident
    is created.
    """
    conn = get_db()
    resources = conn.execute(
        "SELECT * FROM resources WHERE status = 'available'"
    ).fetchall()

    if not resources:
        conn.close()
        return None

    event_node_id = _nearest_node(event_node["lat"], event_node["lng"])

    best_resource, best_dist = None, math.inf
    for resource in resources:
        resource_node_id = _nearest_node(resource["location_lat"], resource["location_lng"])
        _, dist = get_route_to_event(resource_node_id, event_node_id)
        if dist < best_dist:
            best_resource, best_dist = resource, dist

    if best_resource is not None:
        conn.execute(
            "UPDATE resources SET status = 'dispatched', assigned_event_id = ? WHERE id = ?",
            (event_id, best_resource["id"])
        )
        conn.commit()

    conn.close()
    return dict(best_resource) if best_resource is not None else None


def get_current_routes():
    """
    For every dispatched resource with an active assigned incident,
    compute its rescue path as a list of {lat, lng} points. This is
    what /api/route returns for the response map to draw.
    """
    conn = get_db()
    dispatched = conn.execute(
        "SELECT * FROM resources WHERE status = 'dispatched' AND assigned_event_id IS NOT NULL"
    ).fetchall()

    rescue_routes = []
    for resource in dispatched:
        event = conn.execute(
            "SELECT * FROM events WHERE id = ? AND status = 'active'",
            (resource["assigned_event_id"],)
        ).fetchone()
        if event is None:
            continue

        start_node_id = _nearest_node(resource["location_lat"], resource["location_lng"])
        end_node_id = _nearest_node(event["location_lat"], event["location_lng"])
        rescue_path, _ = get_route_to_event(start_node_id, end_node_id)

        if rescue_path is None:
            continue

        rescue_routes.append({
            "resource_id": resource["id"],
            "resource_name": resource["name"],
            "event_id": event["id"],
            "event_type": event["type"],
            "path": [{"lat": CITY_NODES[n]["lat"], "lng": CITY_NODES[n]["lng"], "name": CITY_NODES[n]["name"]} for n in rescue_path]
        })

    conn.close()
    return rescue_routes


def seed_resources_if_empty():
    """
    Populates the resources table with a starter fleet, spread across
    a few map nodes, so rescue dispatch has something to assign the
    moment the app starts. Safe to call every startup — only inserts
    if the table is empty.
    """
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) as c FROM resources").fetchone()["c"]
    if count > 0:
        conn.close()
        return

    from datetime import datetime
    now = datetime.now().isoformat(timespec="seconds")

    starter_fleet = [
        ("ambulance", "Ambulance 1", "N1"),
        ("ambulance", "Ambulance 2", "N4"),
        ("rescue_team", "Rescue Team Alpha", "N3"),
        ("rescue_team", "Rescue Team Bravo", "N6"),
        ("shelter", "North Shelter", "N4"),
        ("shelter", "South Shelter", "N5"),
        ("relief_supply", "Relief Truck 1", "N8"),
    ]

    for r_type, name, node_id in starter_fleet:
        node = CITY_NODES[node_id]
        conn.execute(
            "INSERT INTO resources (type, name, location_lat, location_lng, status, assigned_event_id, timestamp) "
            "VALUES (?, ?, ?, ?, 'available', NULL, ?)",
            (r_type, name, node["lat"], node["lng"], now)
        )

    conn.commit()
    conn.close()
