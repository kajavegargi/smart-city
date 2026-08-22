function createMap(divId, center, zoom = 13) {
    const map = L.map(divId).setView(center, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    return map;
}

const EMOJI_ICONS = {
    ambulance: "🚑",
    rescue_team: "🚒",
    shelter: "🏠",
    relief_supply: "📦",
    flood: "🌊",
    landslide: "⛰️",
    earthquake: "🌐",
    heatwave: "🌡️",
};

function emojiIcon(emoji) {
    return L.divIcon({
        html: `<div style="font-size:24px; line-height:24px;">${emoji}</div>`,
        className: "emoji-marker",
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12],
    });
}

function addMarker(map, lat, lng, popupText = "", type = null) {
    const icon = type && EMOJI_ICONS[type] ? emojiIcon(EMOJI_ICONS[type]) : undefined;
    const marker = icon
        ? L.marker([lat, lng], { icon }).addTo(map)
        : L.marker([lat, lng]).addTo(map);
    if (popupText) marker.bindPopup(popupText);
    return marker;
}

let currentRouteLine = null;

function drawRoute(map, coordsArray) {
    if (currentRouteLine) map.removeLayer(currentRouteLine);
    currentRouteLine = L.polyline(coordsArray, { color: "blue" }).addTo(map);
    map.fitBounds(currentRouteLine.getBounds());
}

const ROUTE_STYLES = {
    flood: { color: "#4EE1C4", dashArray: null },
    landslide: { color: "#FFB454", dashArray: "8,6" },
    earthquake: { color: "#FF5C5C", dashArray: "2,6" },
    heatwave: { color: "#FFD24E", dashArray: "12,4" },
};

function drawRoutes(map, routes) {
    if (window._routeLines) {
        window._routeLines.forEach((line) => map.removeLayer(line));
    }
    window._routeLines = [];

    routes.forEach((route) => {
        const latlngs = route.path.map((p) => [p.lat, p.lng]);
        const style = ROUTE_STYLES[route.event_type] || { color: "blue", dashArray: null };
        const line = L.polyline(latlngs, style).addTo(map);
        window._routeLines.push(line);
    });

    if (window._routeLines.length) {
        const group = L.featureGroup(window._routeLines);
        map.fitBounds(group.getBounds());
    }
}