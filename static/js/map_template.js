function createMap(divId, center, zoom = 13) {
    const map = L.map(divId).setView(center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    return map;
}
function drawRoutes(map, routes) {
    // clear any previously drawn routes
    if (window._routeLines) {
        window._routeLines.forEach((line) => map.removeLayer(line));
    }
    window._routeLines = [];

    routes.forEach((route) => {
        const latlngs = route.path.map((p) => [p.lat, p.lng]);
        const line = L.polyline(latlngs, { color: "blue" }).addTo(map);
        window._routeLines.push(line);
    });

    if (window._routeLines.length) {
        const group = L.featureGroup(window._routeLines);
        map.fitBounds(group.getBounds());
    }
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