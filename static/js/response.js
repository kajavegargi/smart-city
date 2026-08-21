// static/js/response.js — Member 3

let responseMap;
let markers = [];

document.addEventListener("DOMContentLoaded", () => {
  responseMap = createMap("response-map", [28.614, 77.211], 14);

  document.getElementById("simulate-event-btn").addEventListener("click", simulateEvent);

  fetchEvents();
  fetchRoute();

  setInterval(fetchEvents, 5000);
  setInterval(fetchRoute, 5000);
});

async function simulateEvent() {
  try {
    const res = await fetch("/api/events", { method: "POST" });
    if (!res.ok) throw new Error("Failed to simulate event");
    await fetchEvents();
    await fetchRoute();
  } catch (err) {
    console.error(err);
  }
}

async function fetchEvents() {
  try {
    const res = await fetch("/api/events");
    const events = await res.json();
    renderEventsList(events);
    renderEventMarkers(events);
  } catch (err) {
    console.error("Error fetching events:", err);
  }
}

function renderEventsList(events) {
  const list = document.getElementById("events-list");
  if (!events.length) {
    list.innerHTML = `<li>No events yet.</li>`;
    return;
  }
  list.innerHTML = events
    .map(
      (e) => `
      <li class="border-l-4 ${e.status === "active" ? "border-red-500" : "border-border-dim"} pl-2">
        <div class="font-medium text-white">${e.description}</div>
        <div class="text-text-dim text-xs">${e.type} · ${e.status} · ${e.timestamp}</div>
      </li>`
    )
    .join("");
}

function renderEventMarkers(events) {
  markers.forEach((m) => responseMap.removeLayer(m));
  markers = [];

  events
    .filter((e) => e.status === "active")
    .forEach((e) => {
      const marker = addMarker(
        responseMap,
        e.location_lat,
        e.location_lng,
        `<b>${e.type}</b><br>${e.description}`
      );
      markers.push(marker);
    });
}

async function fetchRoute() {
  try {
    const res = await fetch("/api/route");
    const points = await res.json();
    if (!points.length) return;
    const coordsArray = points.map((p) => [p.lat, p.lng]);
    drawRoute(responseMap, coordsArray);
  } catch (err) {
    console.error("Error fetching route:", err);
  }
}