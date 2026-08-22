// ============================================================
// SMART CITY DISASTER MONITORING
// ============================================================


// ============================================================
// DISASTER ICONS
// ============================================================

const disasterIcons = {

    "Flood": "🌧️",

    "Heatwave": "🌡️",

    "Landslide": "🪨",

    "Earthquake": "🌍"

};


// ============================================================
// UPDATE CURRENT PRIORITY DISASTER
// ============================================================

async function updateCurrentDisaster() {

    try {

        const response =
            await fetch(
                "/api/current-disaster"
            );


        const data =
            await response.json();


        // ====================================================
        // DISASTER
        // ====================================================

        document.getElementById(
            "disasterIcon"
        ).textContent =
            disasterIcons[
                data.disaster
            ] || "⚠️";


        document.getElementById(
            "disasterName"
        ).textContent =
            data.disaster;


        // ====================================================
        // RISK LEVEL
        // ====================================================

        const riskLevel =
            document.getElementById(
                "riskLevel"
            );


        riskLevel.textContent =
            data.level;


        riskLevel.className =
            data.level.toLowerCase();


        // ====================================================
        // SCORE
        // ====================================================

        document.getElementById(
            "riskScore"
        ).textContent =
            `Risk Score: ${data.score}/100`;


        // ====================================================
        // RECOMMENDATION
        // ====================================================

        document.getElementById(
            "recommendation"
        ).textContent =
            "💡 " +
            data.recommendation;


        // ====================================================
        // RESOURCES
        // ====================================================

        document.getElementById(
            "ambulances"
        ).textContent =
            data.resources.ambulances;


        document.getElementById(
            "rescueTeams"
        ).textContent =
            data.resources.rescue_teams;


        document.getElementById(
            "shelters"
        ).textContent =
            data.resources.shelters;


        document.getElementById(
            "reliefSupplies"
        ).textContent =
            data.resources.relief_supplies;


        // ====================================================
        // RISK OVERVIEW
        // ====================================================

        const overview =
            document.getElementById(
                "riskOverview"
            );


        overview.innerHTML = "";


        Object.entries(
            data.all_risks
        ).forEach(
            ([disaster, score]) => {


                let level;


                if (score < 25) {

                    level = "LOW";

                }

                else if (score < 50) {

                    level = "MODERATE";

                }

                else if (score < 75) {

                    level = "HIGH";

                }

                else {

                    level = "CRITICAL";

                }


                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "risk-item";


                item.innerHTML = `

                    <div class="risk-item-name">

                        ${disasterIcons[disaster] || "⚠️"}

                        ${disaster}

                    </div>

                    <div class="
                        risk-item-score
                        ${level.toLowerCase()}
                    ">

                        ${score}/100

                    </div>

                    <div>

                        ${level}

                    </div>

                `;


                overview.appendChild(
                    item
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Error loading current disaster:",
            error
        );

    }

}


// ============================================================
// UPDATE READINESS SCORE
// ============================================================

async function updateScore() {

    try {

        const response =
            await fetch(
                "/api/score"
            );


        const data =
            await response.json();


        document.getElementById(
            "overallScore"
        ).textContent =
            data.score;


        document.getElementById(
            "normalCount"
        ).textContent =
            data.normal;


        document.getElementById(
            "alertCount"
        ).textContent =
            data.alerts;


        const message =
            document.getElementById(
                "scoreMessage"
            );


        if (data.score >= 80) {

            message.textContent =
                "🌟 Excellent disaster readiness.";

        }

        else if (data.score >= 60) {

            message.textContent =
                "👍 Good readiness. Continue monitoring.";

        }

        else if (data.score >= 40) {

            message.textContent =
                "⚠️ Moderate readiness. Preparedness actions recommended.";

        }

        else {

            message.textContent =
                "🚨 Critical situation. Immediate response recommended.";

        }

    }

    catch (error) {

        console.error(
            "Error loading score:",
            error
        );

    }

}


// ============================================================
// UPDATE ALERT HISTORY
// ============================================================

async function updateAlerts() {

    try {

        const response =
            await fetch(
                "/api/alerts"
            );


        const alerts =
            await response.json();


        const container =
            document.getElementById(
                "alertHistory"
            );


        if (
            alerts.length === 0
        ) {

            container.innerHTML = `
                <p>
                    ✅ No alerts recorded.
                </p>
            `;

            return;

        }


        container.innerHTML = "";


        alerts.forEach(
            alert => {


                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "alert-item";


                const time =
                    new Date(
                        alert.timestamp
                    ).toLocaleString();


                item.innerHTML = `

                    <div>

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

                    <strong>

                        ${alert.severity.toUpperCase()}

                    </strong>

                `;


                container.appendChild(
                    item
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Error loading alerts:",
            error
        );

    }

}


// ============================================================
// INITIAL LOAD
// ============================================================

updateCurrentDisaster();

updateScore();

updateAlerts();


// ============================================================
// REFRESH DASHBOARD
// ============================================================

// Dashboard checks the database every 3 seconds.
// Actual sensor simulation changes every 30 seconds.

setInterval(
    updateCurrentDisaster,
    3000
);


setInterval(
    updateScore,
    3000
);


setInterval(
    updateAlerts,
    3000
);