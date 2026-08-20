"""
detect_routes.py — Member 4
Isolated Flask route: POST /api/detect, accepts an image, returns
detection JSON. Doesn't touch other routes.

Built as a Blueprint on purpose — you register it in app.py with two
lines and never have to edit anyone else's routes, which avoids merge
conflicts with Members 1/2/3.

Also wires detection into the alert/event system: if more than 5 cars
are detected, it inserts a row into `events` (type='traffic') and a
matching row into `alerts`, using the same schema Member 1 defined in
database.py. This satisfies the doc's integration task:
  "Wire detection output as an alternate trigger into Member 3's
   event_sim.py (e.g. 'if >5 cars detected → trigger congestion event')"

Once Member 3's event_sim.py exists with its own function for firing an
event (e.g. simulate_traffic_event()), swap the direct INSERT below for
a call to that function so there's a single source of truth. Until then,
this route is fully self-contained and demoable on its own.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database import get_db
from detect import detect_objects, check_congestion_trigger

detect_bp = Blueprint("detect_bp", __name__)


@detect_bp.route("/api/detect", methods=["POST"])
def api_detect():
    if "image" not in request.files:
        return jsonify({"error": "no image file provided, expected form field 'image'"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()

    try:
        detections = detect_objects(image_bytes)
    except Exception as e:
        return jsonify({"error": f"detection failed: {str(e)}"}), 500

    triggered_car_count = check_congestion_trigger(detections)
    event_triggered = False

    if triggered_car_count is not None:
        _insert_congestion_event(triggered_car_count)
        event_triggered = True

    return jsonify({
        "detections": detections,
        "congestion_triggered": event_triggered
    })


def _insert_congestion_event(car_count):
    """
    Inserts a traffic event + matching alert, following the exact
    schema from database.py:
      events(type, location_lat, location_lng, description, status, timestamp)
      alerts(source_module, message, severity, timestamp)

    Coordinates are a placeholder "Node 5" style mock location, matching
    Member 3's mock city graph described in the doc. Swap these for real
    coordinates once event_sim.py's node list exists.
    """
    conn = get_db()
    now = datetime.now().isoformat(timespec="seconds")

    conn.execute(
        "INSERT INTO events (type, location_lat, location_lng, description, status, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("traffic", 12.9716, 77.5946, f"Congestion detected: {car_count} cars (YOLOv8)", "active", now)
    )
    conn.execute(
        "INSERT INTO alerts (source_module, message, severity, timestamp) VALUES (?, ?, ?, ?)",
        ("detection", f"Traffic congestion detected — {car_count} cars in frame", "high", now)
    )
    conn.commit()
    conn.close()
