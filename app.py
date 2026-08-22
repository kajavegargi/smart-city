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


# -------------------------------
# GET SENSOR DATA
# -------------------------------

@app.route("/api/sensors")
def get_sensors():

    conn = sqlite3.connect("smart_city.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, type, value, unit, status, timestamp
        FROM sensors
        ORDER BY timestamp ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    sensors = []

    for row in rows:

        sensors.append({
            "id": row["id"],
            "type": row["type"],
            "value": row["value"],
            "unit": row["unit"],
            "status": row["status"],
            "timestamp": row["timestamp"]
        })

    return jsonify(sensors)


# -------------------------------
# GET ALERT HISTORY
# -------------------------------

@app.route("/api/alerts")
def get_alerts():

    conn = sqlite3.connect("smart_city.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT source_module, message, severity, timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for row in rows:

        alerts.append({
            "source_module": row["source_module"],
            "message": row["message"],
            "severity": row["severity"],
            "timestamp": row["timestamp"]
        })

    return jsonify(alerts)


# -------------------------------
# OVERALL SMART CITY SCORE
# -------------------------------

@app.route("/api/score")
def get_score():

    conn = sqlite3.connect("smart_city.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get latest reading of every sensor type
    cursor.execute("""
        SELECT type, value, unit, status
        FROM sensors
        WHERE id IN (
            SELECT MAX(id)
            FROM sensors
            GROUP BY type
        )
    """)

    rows = cursor.fetchall()
    conn.close()

    total = len(rows)

    if total == 0:
        return jsonify({
            "score": 0,
            "normal": 0,
            "alerts": 0
        })

    normal = sum(1 for row in rows if row["status"] == "normal")
    alerts = total - normal

    score = round((normal / total) * 100)

    return jsonify({
        "score": score,
        "normal": normal,
        "alerts": alerts
    })


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
