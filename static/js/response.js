// static/js/response.js — Member 3

let responseMap;
let markers = [];
let resourceMarkers = [];

document.addEventListener("DOMContentLoaded", () => {
  responseMap = createMap("response-map", [12.9716, 77.5946], 13);

  document.getElementById("simulate-event-btn").addEventListener("click", simulateEvent);

  fetchEvents();
  fetchResources();
  fetchRoute();

  setInterval(fetchEvents, 5000);
  setInterval(fetchResources, 5000);
  setInterval(fetchRoute, 5000);
});

async function simulateEvent() {
  try {
    const res = await fetch("/api/simulate-event", { method: "POST" });
    if (!res.ok) throw new Error("Failed to simulate event");
    await fetchEvents();
    await fetchResources();
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
        `<b>${e.type}</b><br>${e.description}`,
        e.type
      );
      markers.push(marker);
    });
}

async function fetchResources() {
  try {
    const res = await fetch("/api/resources");
    const resources = await res.json();
    renderResourceMarkers(resources);
  } catch (err) {
    console.error("Error fetching resources:", err);
  }
}

function renderResourceMarkers(resources) {
  resourceMarkers.forEach((m) => responseMap.removeLayer(m));
  resourceMarkers = [];

  resources.forEach((r) => {
    const status = r.status === "dispatched" ? "🚨 dispatched" : "✅ available";
    const marker = addMarker(
      responseMap,
      r.location_lat,
      r.location_lng,
      `<b>${r.name}</b><br>${status}`,
      r.type
    );
    resourceMarkers.push(marker);
  });
}

async function fetchRoute() {
  try {
    const res = await fetch("/api/route");
    const routes = await res.json();
    if (!routes.length) return;
    drawRoutes(responseMap, routes);
  } catch (err) {
    console.error("Error fetching route:", err);
  }
}