from flask import Flask, render_template, jsonify
from database import get_db, init_db
from routing import get_route
from data_simulator.event_sim import simulate_event
import data_simulator.event_sim as event_sim
init_db()
# from flask import Flask, ... — pulling specific names out of the flask package instead of the whole thing, so you can write Flask() instead of flask.Flask().
# render_template — the function that finds an HTML file inside templates/ and returns it as a response.
# jsonify — converts a Python dict/list into a proper JSON HTTP response (sets the right headers etc.).
# from database import get_db, init_db — importing your own two functions from the file you just wrote. Python treats database.py as a module because it's in the same folder.
app = Flask(__name__)

from detect_routes import detect_bp
app.register_blueprint(detect_bp)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")

@app.route("/response")
def response():
    return render_template("response.html")

@app.route("/api/summary")
def api_summary():
    conn = get_db()
    active_alerts = conn.execute("SELECT COUNT(*) as c FROM alerts").fetchone()["c"]
    sensor_types_online = conn.execute("SELECT COUNT(DISTINCT type) as c FROM sensor_readings").fetchone()["c"]
    active_events = conn.execute("SELECT COUNT(*) as c FROM events WHERE status = 'active'").fetchone()["c"]
    conn.close()

    return jsonify({
        "active_alerts": active_alerts,
        "sensor_types_online": sensor_types_online,
        "active_events": active_events
    })
# -------------------------------
# GET SENSOR DATA
# -------------------------------

@app.route("/api/sensors")
def get_sensors():
    conn = get_db()
    rows = conn.execute("""
        SELECT id, type, value, unit, status, timestamp
        FROM sensor_readings
        ORDER BY timestamp ASC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# -------------------------------
# GET ALERT HISTORY
# -------------------------------

@app.route("/api/alerts")
def get_alerts():
    conn = get_db()
    rows = conn.execute("""
        SELECT source_module, message, severity, timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# -------------------------------
# OVERALL SMART CITY SCORE
# -------------------------------

@app.route("/api/score")
def get_score():
    conn = get_db()
    rows = conn.execute("""
        SELECT type, value, unit, status
        FROM sensor_readings
        WHERE id IN (
            SELECT MAX(id)
            FROM sensor_readings
            GROUP BY type
        )
    """).fetchall()
    conn.close()

    total = len(rows)
    if total == 0:
        return jsonify({"score": 0, "normal": 0, "alerts": 0})

    normal = sum(1 for row in rows if row["status"] == "normal")
    alerts = total - normal
    score = round((normal / total) * 100)

    return jsonify({"score": score, "normal": normal, "alerts": alerts})


# -------------------------------
# RUN FLASK
# -------------------------------

@app.route("/api/events", methods=["GET"])
def api_events():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/events", methods=["POST"])
def api_trigger_event():
    event = simulate_event()
    return jsonify(event), 201


@app.route("/api/route", methods=["GET"])
def api_route():
    blocked = {event_sim.CURRENT_BLOCKED_NODE} if event_sim.CURRENT_BLOCKED_NODE else None
    path = get_route("N1", "N8", blocked_nodes=blocked)
    return jsonify(path)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
