import sqlite3
import random
import time
from datetime import datetime


DB_NAME = "smart_city.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DB_NAME)


# ============================================================
# ADD SENSOR READING
# ============================================================

def add_sensor(
    sensor_type,
    value,
    unit,
    threshold
):

    status = (
        "alert"
        if value > threshold
        else "normal"
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_readings
        (type, value, unit, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        sensor_type,
        value,
        unit,
        status,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    print(
        f"{sensor_type}: "
        f"{value} {unit} → {status}"
    )


# ============================================================
# ADD ALERT
# ============================================================

def add_alert(
    source,
    message,
    severity
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts
        (source_module, message, severity, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        source,
        message,
        severity,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# ============================================================
# NORMALIZE VALUE TO 0-100
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

def get_risk_level(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MODERATE"

    elif score < 75:
        return "HIGH"

    else:
        return "CRITICAL"


# ============================================================
# FLOOD RISK
# ============================================================

def calculate_flood_risk(
    rainfall,
    water_level,
    drainage
):

    rainfall_score = normalize(
        rainfall,
        0,
        120
    )

    water_score = normalize(
        water_level,
        0,
        5
    )

    drainage_score = (
        100 - drainage
    )

    score = (
        rainfall_score * 0.40
        +
        water_score * 0.40
        +
        drainage_score * 0.20
    )

    return round(score)


# ============================================================
# HEATWAVE RISK
# ============================================================

def calculate_heatwave_risk(
    temperature,
    humidity
):

    temperature_score = normalize(
        temperature,
        20,
        45
    )

    humidity_score = normalize(
        humidity,
        20,
        100
    )

    score = (
        temperature_score * 0.70
        +
        humidity_score * 0.30
    )

    return round(score)


# ============================================================
# LANDSLIDE RISK
# ============================================================

def calculate_landslide_risk(
    rainfall,
    soil_moisture,
    slope_instability
):

    rainfall_score = normalize(
        rainfall,
        0,
        120
    )

    soil_score = normalize(
        soil_moisture,
        0,
        100
    )

    slope_score = normalize(
        slope_instability,
        0,
        100
    )

    score = (
        rainfall_score * 0.30
        +
        soil_score * 0.35
        +
        slope_score * 0.35
    )

    return round(score)


# ============================================================
# EARTHQUAKE RISK
# ============================================================

def calculate_earthquake_risk(
    seismic_activity
):

    score = normalize(
        seismic_activity,
        0,
        8
    )

    return round(score)


# ============================================================
# SIMULATION LOOP
# ============================================================

while True:

    print("\n")
    print("======================================")
    print("GENERATING NEW SENSOR DATA")
    print("======================================")


    # ========================================================
    # SENSOR VALUES
    # ========================================================

    rainfall = random.randint(
        0,
        120
    )

    water_level = round(
        random.uniform(
            0.5,
            5.0
        ),
        2
    )

    drainage = random.randint(
        20,
        100
    )

    temperature = random.randint(
        25,
        45
    )

    humidity = random.randint(
        30,
        100
    )

    soil_moisture = random.randint(
        20,
        100
    )

    slope_instability = random.randint(
        10,
        100
    )

    seismic_activity = round(
        random.uniform(
            0,
            8
        ),
        2
    )


    # ========================================================
    # SAVE SENSOR DATA
    # ========================================================

    add_sensor(
        "rainfall",
        rainfall,
        "mm/hr",
        70
    )

    add_sensor(
        "water_level",
        water_level,
        "m",
        2.5
    )

    add_sensor(
        "drainage",
        drainage,
        "%",
        30
    )

    add_sensor(
        "temperature",
        temperature,
        "°C",
        40
    )

    add_sensor(
        "humidity",
        humidity,
        "%",
        85
    )

    add_sensor(
        "soil_moisture",
        soil_moisture,
        "%",
        75
    )

    add_sensor(
        "slope_instability",
        slope_instability,
        "%",
        70
    )

    add_sensor(
        "seismic_activity",
        seismic_activity,
        "Magnitude",
        5
    )


    # ========================================================
    # CALCULATE ALL RISKS
    # ========================================================

    flood_score = calculate_flood_risk(
        rainfall,
        water_level,
        drainage
    )

    heatwave_score = calculate_heatwave_risk(
        temperature,
        humidity
    )

    landslide_score = calculate_landslide_risk(
        rainfall,
        soil_moisture,
        slope_instability
    )

    earthquake_score = calculate_earthquake_risk(
        seismic_activity
    )


    # ========================================================
    # PRINT ALL RISKS IN TERMINAL
    # ========================================================

    print()
    print(
        "Flood:",
        flood_score,
        get_risk_level(flood_score)
    )

    print(
        "Heatwave:",
        heatwave_score,
        get_risk_level(heatwave_score)
    )

    print(
        "Landslide:",
        landslide_score,
        get_risk_level(landslide_score)
    )

    print(
        "Earthquake:",
        earthquake_score,
        get_risk_level(earthquake_score)
    )


    # ========================================================
    # FIND HIGHEST RISK
    # ========================================================

    risks = {

        "Flood": flood_score,

        "Heatwave": heatwave_score,

        "Landslide": landslide_score,

        "Earthquake": earthquake_score

    }


    highest_disaster = max(
        risks,
        key=risks.get
    )

    highest_score = risks[
        highest_disaster
    ]

    highest_level = get_risk_level(
        highest_score
    )


    print()
    print(
        "CURRENT PRIORITY:",
        highest_disaster
    )

    print(
        "RISK:",
        highest_score,
        "/100"
    )

    print(
        "LEVEL:",
        highest_level
    )


    # ========================================================
    # CREATE ALERT ONLY FOR HIGH/CRITICAL
    # ========================================================

    if highest_score >= 50:

        add_alert(
            "decision-support",
            (
                f"{highest_disaster} "
                f"risk detected: "
                f"{highest_level} "
                f"({highest_score}/100)"
            ),
            highest_level.lower()
        )


    print()
    print("Next reading in 30 seconds...")
    print("======================================")

    time.sleep(30)