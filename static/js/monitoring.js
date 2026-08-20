// ==========================================
// SMART CITY MONITORING - FULL JAVASCRIPT
// ==========================================


// Sensor types
const types = [
    "energy",
    "water",
    "waste",
    "environment"
];


// Store charts
const charts = {};


// ==========================================
// CREATE CHARTS
// ==========================================

types.forEach(type => {

    const ctx = document
        .getElementById(type + "Chart")
        .getContext("2d");


    charts[type] = new Chart(ctx, {

        type: "line",

        data: {

            labels: [],

            datasets: [{
                label:
                    type.charAt(0).toUpperCase()
                    + type.slice(1),

                data: [],

                borderWidth: 3,

                tension: 0.4,

                fill: false,

                pointRadius: 4,

                pointHoverRadius: 6
            }]
        },


        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: false,

            scales: {

                y: {

                    beginAtZero: true

                }

            },

            plugins: {

                legend: {

                    display: true

                }

            }

        }

    });

});


// ==========================================
// UPDATE SENSOR DASHBOARD
// ==========================================

async function updateDashboard() {

    try {

        const response =
            await fetch("/api/sensors");


        const readings =
            await response.json();


        // If database has no readings
        if (readings.length === 0) {

            return;

        }


        // Update every sensor type
        types.forEach(type => {


            // Get readings for this sensor
            const sensorReadings =
                readings
                    .filter(sensor =>
                        sensor.type === type
                    )
                    .slice(-10);


            // If no readings for this type
            if (sensorReadings.length === 0) {

                return;

            }


            // Latest reading
            const latest =
                sensorReadings[
                    sensorReadings.length - 1
                ];


            // ==================================
            // STATUS
            // ==================================

            const statusElement =
                document.getElementById(
                    type + "Status"
                );


            if (latest.status === "alert") {

                statusElement.innerHTML = `
                    <span class="status-dot red"></span>
                    ALERT
                `;

            }
            else {

                statusElement.innerHTML = `
                    <span class="status-dot green"></span>
                    NORMAL
                `;

            }


            // ==================================
            // CURRENT VALUE
            // ==================================

            const currentElement =
                document.getElementById(
                    type + "Current"
                );


            currentElement.textContent =
                `Current: ${latest.value} ${latest.unit}`;


            // ==================================
            // CHART
            // ==================================

            const chart =
                charts[type];


            // Time labels
            chart.data.labels =
                sensorReadings.map(sensor => {

                    return sensor.timestamp
                        .substring(11, 19);

                });


            // Sensor values
            chart.data.datasets[0].data =
                sensorReadings.map(sensor => {

                    return sensor.value;

                });


            // Update chart
            chart.update();

        });


    }
    catch (error) {

        console.error(
            "Error loading sensor data:",
            error
        );

    }

}


// ==========================================
// UPDATE OVERALL SMART CITY SCORE
// ==========================================

async function updateScore() {

    try {

        const response =
            await fetch("/api/score");


        const data =
            await response.json();


        // Display score
        document.getElementById(
            "overallScore"
        ).textContent = data.score;


        // Display normal count
        document.getElementById(
            "normalCount"
        ).textContent = data.normal;


        // Display alert count
        document.getElementById(
            "alertCount"
        ).textContent = data.alerts;


        // ==================================
        // SCORE MESSAGE
        // ==================================

        const message =
            document.getElementById(
                "scoreMessage"
            );


        if (data.score === 100) {

            message.textContent =
                "🌟 Excellent! All city systems are operating normally.";

        }
        else if (data.score >= 75) {

            message.textContent =
                "👍 Good! Most city systems are operating normally.";

        }
        else if (data.score >= 50) {

            message.textContent =
                "⚠️ Moderate! Some systems need attention.";

        }
        else {

            message.textContent =
                "🚨 Critical! Immediate attention required.";

        }

    }
    catch (error) {

        console.error(
            "Error loading smart city score:",
            error
        );

    }

}


// ==========================================
// UPDATE ALERT HISTORY
// ==========================================

async function updateAlerts() {

    try {

        const response =
            await fetch("/api/alerts");


        const alerts =
            await response.json();


        const container =
            document.getElementById(
                "alertHistory"
            );


        // ==================================
        // NO ALERTS
        // ==================================

        if (alerts.length === 0) {

            container.innerHTML = `
                <p>
                    ✅ No alerts recorded.
                </p>
            `;

            return;

        }


        // Clear old alerts
        container.innerHTML = "";


        // ==================================
        // DISPLAY ALERTS
        // ==================================

        alerts.forEach(alert => {


            const item =
                document.createElement("div");


            item.className =
                "alert-item";


            // Convert timestamp
            const time =
                new Date(
                    alert.timestamp
                ).toLocaleString();


            item.innerHTML = `

                <div class="alert-icon">
                    🚨
                </div>

                <div class="alert-details">

                    <div class="alert-message">
                        ${alert.message}
                    </div>

                    <div class="alert-time">
                        ${time}
                    </div>

                </div>

                <div class="alert-severity">
                    ${alert.severity.toUpperCase()}
                </div>

            `;


            container.appendChild(item);

        });

    }
    catch (error) {

        console.error(
            "Error loading alert history:",
            error
        );

    }

}


// ==========================================
// INITIAL LOAD
// ==========================================

updateDashboard();

updateScore();

updateAlerts();


// ==========================================
// AUTOMATIC REFRESH
// ==========================================

// Sensor charts + status
setInterval(
    updateDashboard,
    3000
);


// Overall score
setInterval(
    updateScore,
    3000
);


// Alert history
setInterval(
    updateAlerts,
    3000
);