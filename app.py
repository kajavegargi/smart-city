from flask import Flask, render_template, jsonify
from database import get_db, init_db
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
    sensor_types_online = conn.execute("SELECT COUNT(DISTINCT type) as c from sensors").fetchone()["c"]
    active_events = conn.execute("SELECT COUNT(*) as c FROM events WHERE status = 'active' ").fetchone()["c"]
    conn.close()

    return jsonify(
        {
            "active_alerts" : active_alerts,
            "sensor_types_online" : sensor_types_online,
            "active_events" : active_events
            }
        )

@app.route("/api/alerts")
def api_alerts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 20").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
