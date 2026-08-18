function createLineChart(canvasId, label, color = "#3b82f6") {
    const ctx = document.getElementById(canvasId).getContext("2d");
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: color,
                tension: 0.3,
                fill: false
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: { y: { beginAtZero: false } }
        }
});
}

function updateChart(chart, value, label, maxPoints = 20) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update();
}