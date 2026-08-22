// ==========================================
// SMART CITY MONITORING - FULL JAVASCRIPT
// ==========================================

// Sensor types — must match sensor_sim.py's SENSOR_CONFIG keys exactly
const types = [
    "seismic_activity",
    "river_level",
    "rainfall",
    "heat_index"
];

// Store charts
const charts = {};

// ==========================================
// CREATE CHARTS
// ==========================================

types.forEach(type => {
    const ctx = document.getElementById(type + "Chart").getContext("2d");

    charts[type] = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: type.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase()),
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
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: true } }
        }
    });
});

// ==========================================
// UPDATE SENSOR DASHBOARD
// ==========================================

async function updateDashboard() {
    try {
        const response = await fetch("/api/sensors");
        const grouped = await response.json();  // now { "seismic_activity": [...], ... }

        types.forEach(type => {
            const sensorReadings = (grouped[type] || []).slice(-10);

            if (sensorReadings.length === 0) return;

            const latest = sensorReadings[sensorReadings.length - 1];

            const statusElement = document.getElementById(type + "Status");
            statusElement.innerHTML = latest.status === "alert"
                ? `<span class="status-dot red"></span> ALERT`
                : `<span class="status-dot green"></span> NORMAL`;

            const currentElement = document.getElementById(type + "Current");
            currentElement.textContent = `Current: ${latest.value} ${latest.unit}`;

            const chart = charts[type];
            chart.data.labels = sensorReadings.map(s => s.timestamp.substring(11, 19));
            chart.data.datasets[0].data = sensorReadings.map(s => s.value);
            chart.update();
        });
    } catch (error) {
        console.error("Error loading sensor data:", error);
    }
}

// ==========================================
// ALERT HISTORY, SCORE — unchanged
// ==========================================

async function updateScore() {
    try {
        const response = await fetch("/api/score");
        const data = await response.json();

        document.getElementById("overallScore").textContent = data.score;
        document.getElementById("normalCount").textContent = data.normal;
        document.getElementById("alertCount").textContent = data.alerts;

        const message = document.getElementById("scoreMessage");
        if (data.score === 100) message.textContent = "🌟 Excellent! All city systems are operating normally.";
        else if (data.score >= 75) message.textContent = "👍 Good! Most city systems are operating normally.";
        else if (data.score >= 50) message.textContent = "⚠️ Moderate! Some systems need attention.";
        else message.textContent = "🚨 Critical! Immediate attention required.";
    } catch (error) {
        console.error("Error loading smart city score:", error);
    }
}

async function updateAlerts() {
    try {
        const response = await fetch("/api/alerts");
        const alerts = await response.json();
        const container = document.getElementById("alertHistory");

        if (alerts.length === 0) {
            container.innerHTML = `<p>✅ No alerts recorded.</p>`;
            return;
        }

        container.innerHTML = "";
        alerts.forEach(alert => {
            const item = document.createElement("div");
            item.className = "alert-item";
            const time = new Date(alert.timestamp).toLocaleString();
            item.innerHTML = `
                <div class="alert-icon">🚨</div>
                <div class="alert-details">
                    <div class="alert-message">${alert.message}</div>
                    <div class="alert-time">${time}</div>
                </div>
                <div class="alert-severity">${alert.severity.toUpperCase()}</div>
            `;
            container.appendChild(item);
        });
    } catch (error) {
        console.error("Error loading alert history:", error);
    }
}

updateDashboard();
updateScore();
updateAlerts();

setInterval(updateDashboard, 3000);
setInterval(updateScore, 3000);
setInterval(updateAlerts, 3000);