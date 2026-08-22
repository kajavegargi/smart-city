"""
app.py — Member 1

Flask app init, route registration for pages, plus the core API routes
(/api/alerts, /api/summary). Member 4's detection route is registered
as a separate Blueprint (detect_routes.py) so it never causes merge
conflicts here — just the two lines near the bottom.

Member 2 and Member 3's simulator scripts (sensor_sim.py, event_sim.py)
run as SEPARATE processes (python data_simulator/sensor_sim.py in its
own terminal) — they are not imported into app.py. They just write to
the same smart_city.db file that app.py reads from.
"""

from flask import Flask, render_template, jsonify
from database import init_db, get_db
from detect_routes import detect_bp
from routing import get_current_routes, resolve_expired_events, seed_resources_if_empty

app = Flask(__name__)

# Member 4's isolated detection route — /api/detect
app.register_blueprint(detect_bp)


# ---------- Page routes ----------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


@app.route("/response")
def response():
    return render_template("response.html")


# ---------- Shared API routes (Member 1) ----------

@app.route("/api/alerts")
def api_alerts():
    """Latest alerts, most recent first — powers the shared bell icon."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/summary")
def api_summary():
    """Counts per module, shown as overview cards on the home page."""
    conn = get_db()

    active_alerts = conn.execute(
        "SELECT COUNT(*) as c FROM alerts"
    ).fetchone()["c"]

    active_events = conn.execute(
        "SELECT COUNT(*) as c FROM events WHERE status = 'active'"
    ).fetchone()["c"]

    sensors_online = conn.execute(
        "SELECT COUNT(*) as c FROM sensors"
    ).fetchone()["c"]

    resources_available = conn.execute(
        "SELECT COUNT(*) as c FROM resources WHERE status = 'available'"
    ).fetchone()["c"]

    resources_dispatched = conn.execute(
        "SELECT COUNT(*) as c FROM resources WHERE status = 'dispatched'"
    ).fetchone()["c"]

    conn.close()

    return jsonify({
        "active_alerts": active_alerts,
        "active_events": active_events,
        "sensors_online": sensors_online,
        "resources_available": resources_available,
        "resources_dispatched": resources_dispatched
    })


# ---------- Member 2: Monitoring API ----------

@app.route("/api/sensors")
def api_sensors():
    """Latest sensor readings, grouped by disaster-risk type."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sensors ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    conn.close()

    grouped = {}
    for row in rows:
        grouped.setdefault(row["type"], []).append(dict(row))

    return jsonify(grouped)


# ---------- Member 3: Response / Routing API ----------

@app.route("/api/events")
def api_events():
    """Latest disaster events, most recent first."""
    resolve_expired_events()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/route")
def api_route():
    """Best current routes from available resources to active events."""
    return jsonify(get_current_routes())


@app.route("/api/resources")
def api_resources():
    resolve_expired_events()
    """All emergency resources and their current status/location."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM resources ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/simulate-event", methods=["POST"])
def api_simulate_event():
    resolve_expired_events() 
    """Manually fire a disaster event — powers the 'Simulate Event' button on response.html."""
    from data_simulator.event_sim import simulate_disaster_event
    event_id = simulate_disaster_event()
    return jsonify({"event_id": event_id, "status": "simulated"})

@app.route("/api/score")
def api_score():
    """Overall safety score: % of latest-per-type sensor readings that are 'normal'."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sensors ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()

    latest_by_type = {}
    for row in rows:
        if row["type"] not in latest_by_type:
            latest_by_type[row["type"]] = row

    total = len(latest_by_type)
    normal = sum(1 for r in latest_by_type.values() if r["status"] == "normal")
    alerts = total - normal
    score = round((normal / total) * 100) if total else 100

    return jsonify({
        "score": score,
        "normal": normal,
        "alerts": alerts
    })

if __name__ == "__main__":
    init_db()
    seed_resources_if_empty()
    app.run(debug=True, port=5001)
