function createMap(divId, center, zoom = 13) {
    const map = L.map(divId).setView(center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    return map;
}

function addMarker(map, lat, lng, popupText = "") {
    const marker = L.marker([lat, lng]).addTo(map);
    if (popupText) marker.bindPopup(popupText);
    return marker;
}
let currentRouteLine = null;

function drawRoute(map, coordsArray) {
    if (currentRouteLine) map.removeLayer(currentRouteLine);
    currentRouteLine = L.polyline(coordsArray, { color: "blue" }).addTo(map);
    map.fitBounds(currentRouteLine.getBounds());
}