from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)


# -------------------------------
# MONITORING PAGE
# -------------------------------

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

if __name__ == "__main__":
    app.run(debug=True)