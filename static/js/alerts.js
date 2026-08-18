async function pollAlerts() {
    const res = await fetch("/api/alerts");
    const alerts = await res.json();

    const badge = document.getElementById("alert-badge");
    const dropdown = document.getElementById("alert-dropdown");
    
    if (alerts.length > 0) {
    badge.textContent = alerts.length;
    badge.classList.remove("hidden");
    } else {
    badge.classList.add("hidden");
    }
dropdown.innerHTML = alerts.length
    ? alerts.map(a => `
        <div class="p-3 border-b text-sm">
            <span class="font-semibold uppercase text-xs ${
                a.severity === 'high' ? 'text-red-600' :
                a.severity === 'medium' ? 'text-yellow-600' : 'text-gray-500'
            }">${a.severity}</span>
            <div>${a.message}</div>
            <div class="text-gray-400 text-xs">${a.source_module} · ${a.timestamp}</div>
        </div>
    `).join("")
    : `<div class="p-3 text-sm text-gray-500">No alerts yet</div>`;
}

document.getElementById("alert-bell").addEventListener("click", () => {
    document.getElementById("alert-dropdown").classList.toggle("hidden");
});

pollAlerts();
setInterval(pollAlerts, 5000);