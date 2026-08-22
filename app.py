from flask import Flask, render_template, jsonify
import sqlite3


app = Flask(__name__)

DB_NAME = "smart_city.db"


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    conn = sqlite3.connect(
        DB_NAME
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# MONITORING PAGE
# ============================================================

@app.route("/monitoring")
def monitoring():

    return render_template(
        "monitoring.html"
    )


# ============================================================
# LATEST SENSOR VALUE
# ============================================================

def latest_value(
    cursor,
    sensor_type
):

    cursor.execute("""
        SELECT value
        FROM sensor_readings
        WHERE type = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        sensor_type,
    ))

    row = cursor.fetchone()

    if row:

        return row["value"]

    return 0


# ============================================================
# NORMALIZE
# ============================================================

def normalize(
    value,
    minimum,
    maximum
):

    score = (
        (value - minimum)
        /
        (maximum - minimum)
    ) * 100

    return max(
        0,
        min(100, score)
    )


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(score):

    if score < 25:

        return "LOW"

    elif score < 50:

        return "MODERATE"

    elif score < 75:

        return "HIGH"

    else:

        return "CRITICAL"


# ============================================================
# CALCULATE ALL RISKS
# ============================================================

def calculate_all_risks(cursor):

    rainfall = latest_value(
        cursor,
        "rainfall"
    )

    water_level = latest_value(
        cursor,
        "water_level"
    )

    drainage = latest_value(
        cursor,
        "drainage"
    )

    temperature = latest_value(
        cursor,
        "temperature"
    )

    humidity = latest_value(
        cursor,
        "humidity"
    )

    soil_moisture = latest_value(
        cursor,
        "soil_moisture"
    )

    slope_instability = latest_value(
        cursor,
        "slope_instability"
    )

    seismic_activity = latest_value(
        cursor,
        "seismic_activity"
    )


    # ========================================================
    # FLOOD
    # ========================================================

    flood_score = round(

        normalize(
            rainfall,
            0,
            120
        ) * 0.40

        +

        normalize(
            water_level,
            0,
            5
        ) * 0.40

        +

        (100 - drainage) * 0.20

    )


    # ========================================================
    # HEATWAVE
    # ========================================================

    heatwave_score = round(

        normalize(
            temperature,
            20,
            45
        ) * 0.70

        +

        normalize(
            humidity,
            20,
            100
        ) * 0.30

    )


    # ========================================================
    # LANDSLIDE
    # ========================================================

    landslide_score = round(

        normalize(
            rainfall,
            0,
            120
        ) * 0.30

        +

        normalize(
            soil_moisture,
            0,
            100
        ) * 0.35

        +

        normalize(
            slope_instability,
            0,
            100
        ) * 0.35

    )


    # ========================================================
    # EARTHQUAKE
    # ========================================================

    earthquake_score = round(

        normalize(
            seismic_activity,
            0,
            8
        )

    )


    return {

        "Flood": flood_score,

        "Heatwave": heatwave_score,

        "Landslide": landslide_score,

        "Earthquake": earthquake_score

    }


# ============================================================
# CURRENT PRIORITY DISASTER
# ============================================================

@app.route("/api/current-disaster")
def current_disaster():

    conn = get_connection()
    cursor = conn.cursor()


    risks = calculate_all_risks(
        cursor
    )


    conn.close()


    # ========================================================
    # FIND HIGHEST RISK
    # ========================================================

    disaster = max(
        risks,
        key=risks.get
    )


    score = risks[
        disaster
    ]


    level = risk_level(
        score
    )


    # ========================================================
    # RESOURCE ALLOCATION
    # ========================================================

    if score < 25:

        ambulances = 0
        rescue_teams = 0
        shelters = 0
        supplies = 0


    elif score < 50:

        ambulances = 2
        rescue_teams = 1
        shelters = 1
        supplies = 100


    elif score < 75:

        ambulances = 4
        rescue_teams = 3
        shelters = 2
        supplies = 250


    else:

        ambulances = 6
        rescue_teams = 5
        shelters = 3
        supplies = 500


    # ========================================================
    # DISASTER-SPECIFIC RESOURCE ADJUSTMENT
    # ========================================================

    if disaster == "Flood":

        shelters += 1

        supplies += 100


    elif disaster == "Earthquake":

        ambulances += 2

        rescue_teams += 2


    elif disaster == "Landslide":

        rescue_teams += 2

        ambulances += 1


    elif disaster == "Heatwave":

        ambulances += 1

        shelters += 1


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    if score < 25:

        recommendation = (
            "No immediate emergency deployment "
            "required. Continue monitoring."
        )

    else:

        recommendation = (
            f"{level} {disaster} risk detected. "
            f"Prioritize emergency resources "
            f"for the affected zone."
        )


    return jsonify({

        "disaster": disaster,

        "score": score,

        "level": level,

        "recommendation":
            recommendation,

        "resources": {

            "ambulances":
                ambulances,

            "rescue_teams":
                rescue_teams,

            "shelters":
                shelters,

            "relief_supplies":
                supplies

        },

        # Keep all risk values internally available
        "all_risks": risks

    })


# ============================================================
# SENSOR API
# ============================================================

@app.route("/api/sensors")
def get_sensors():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            id,
            type,
            value,
            unit,
            status,
            timestamp
        FROM sensor_readings
        ORDER BY id ASC
    """)


    rows = cursor.fetchall()

    conn.close()


    sensors = []


    for row in rows:

        sensors.append({

            "id":
                row["id"],

            "type":
                row["type"],

            "value":
                row["value"],

            "unit":
                row["unit"],

            "status":
                row["status"],

            "timestamp":
                row["timestamp"]

        })


    return jsonify(
        sensors
    )


# ============================================================
# ALERT API
# ============================================================

@app.route("/api/alerts")
def get_alerts():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            source_module,
            message,
            severity,
            timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT 15
    """)


    rows = cursor.fetchall()

    conn.close()


    alerts = []


    for row in rows:

        alerts.append({

            "source_module":
                row["source_module"],

            "message":
                row["message"],

            "severity":
                row["severity"],

            "timestamp":
                row["timestamp"]

        })


    return jsonify(
        alerts
    )


# ============================================================
# OVERALL READINESS SCORE
# ============================================================

@app.route("/api/score")
def get_score():

    conn = get_connection()
    cursor = conn.cursor()


    risks = calculate_all_risks(
        cursor
    )


    conn.close()


    scores = list(
        risks.values()
    )


    average_risk = (
        sum(scores)
        /
        len(scores)
    )


    readiness = round(
        100 - average_risk
    )


    readiness = max(
        0,
        min(
            100,
            readiness
        )
    )


    normal = sum(
        1
        for score in scores
        if score < 50
    )


    alerts = sum(
        1
        for score in scores
        if score >= 50
    )


    return jsonify({

        "score":
            readiness,

        "normal":
            normal,

        "alerts":
            alerts

    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )