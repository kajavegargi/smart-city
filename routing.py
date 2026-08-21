"""
routing.py — Member 3
Small mock city graph (8 nodes with lat/lng) + Dijkstra shortest path.
Import get_route(start, end, blocked_nodes) from app.py or a Flask route.
"""

import heapq

# Mock city graph: node_id -> (lat, lng)
# Coordinates are made up but roughly clustered so it looks like a real city on the map.
NODES = {
    "N1": (28.6139, 77.2090),
    "N2": (28.6145, 77.2120),
    "N3": (28.6170, 77.2105),
    "N4": (28.6120, 77.2140),
    "N5": (28.6100, 77.2080),
    "N6": (28.6160, 77.2060),
    "N7": (28.6190, 77.2130),
    "N8": (28.6080, 77.2150),
}

# Undirected weighted edges: (node_a, node_b, weight)
# Weight = arbitrary "travel time" units — tweak as you like.
EDGES = [
    ("N1", "N2", 2),
    ("N1", "N6", 3),
    ("N2", "N3", 2),
    ("N2", "N4", 3),
    ("N3", "N7", 2),
    ("N4", "N5", 2),
    ("N4", "N8", 3),
    ("N5", "N1", 4),
    ("N6", "N3", 4),
    ("N7", "N4", 3),
    ("N8", "N5", 2),
]


def _build_adjacency(blocked_nodes=None):
    """Build adjacency list, optionally excluding blocked nodes (e.g. congestion event)."""
    blocked_nodes = blocked_nodes or set()
    adj = {node: [] for node in NODES if node not in blocked_nodes}
    for a, b, w in EDGES:
        if a in blocked_nodes or b in blocked_nodes:
            continue
        adj[a].append((b, w))
        adj[b].append((a, w))
    return adj


def dijkstra(start, end, blocked_nodes=None):
    """Returns (path_list, total_cost) or (None, None) if no path exists."""
    adj = _build_adjacency(blocked_nodes)
    if start not in adj or end not in adj:
        return None, None

    dist = {node: float("inf") for node in adj}
    prev = {node: None for node in adj}
    dist[start] = 0
    pq = [(0, start)]
    visited = set()

    while pq:
        d, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            break
        for neighbor, weight in adj[node]:
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                prev[neighbor] = node
                heapq.heappush(pq, (nd, neighbor))

    if dist[end] == float("inf"):
        return None, None

    # reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path, dist[end]


def get_route(start="N1", end="N8", blocked_nodes=None):
    """
    High-level helper for the Flask route.
    Returns a list of {lat, lng, node} dicts ready for Leaflet, or [] if no path.
    """
    path, cost = dijkstra(start, end, blocked_nodes)
    if not path:
        return []
    return [{"node": n, "lat": NODES[n][0], "lng": NODES[n][1]} for n in path]


def node_coords(node_id):
    """Return (lat, lng) for a single node, used when logging an event location."""
    return NODES.get(node_id, (28.6139, 77.2090))