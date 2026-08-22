// static/js/congestion.js — captures frames from a video feed and sends
// each to /api/detect, then renders detection counts + congestion alerts.

const USE_WEBCAM = false; // set true to use live webcam instead of a video file
const SAMPLE_VIDEO_PATH = "/static/videos/traffic_sample.mp4"; // put your clip here

const video = document.getElementById("feed-video");
const canvas = document.getElementById("feed-canvas");
const ctx = canvas.getContext("2d");
const statusEl = document.getElementById("detect-status");
const countsEl = document.getElementById("detection-counts");
const logEl = document.getElementById("congestion-log");

const CAPTURE_INTERVAL_MS = 3000; // how often a frame is sent for detection
let congestionEvents = [];

async function setupFeed() {
  if (USE_WEBCAM) {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
  } else {
    video.src = SAMPLE_VIDEO_PATH;
  }
}

function captureFrame() {
  return new Promise((resolve) => {
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.8);
  });
}

async function runDetectionCycle() {
  if (video.readyState < 2) return; // frame not ready yet

  statusEl.textContent = "Detecting...";
  try {
    const blob = await captureFrame();
    const formData = new FormData();
    formData.append("image", blob, "frame.jpg");

    const res = await fetch("/api/detect", { method: "POST", body: formData });
    const data = await res.json();

    renderCounts(data.detections || []);
    if (data.congestion_triggered) logCongestionEvent(data.detections);

    statusEl.textContent = "Live";
  } catch (err) {
    console.error("Detection error:", err);
    statusEl.textContent = "Error";
  }
}

function renderCounts(detections) {
  if (!detections.length) {
    countsEl.innerHTML = "No objects detected in this frame.";
    return;
  }
  countsEl.innerHTML = detections
    .map((d) => `<div>${d.class}: <span class="font-mono text-white">${d.count}</span></div>`)
    .join("");
}

function logCongestionEvent(detections) {
  const carCount = detections.find((d) => d.class === "car")?.count ?? "?";
  const time = new Date().toLocaleTimeString();
  congestionEvents.unshift({ carCount, time });
  congestionEvents = congestionEvents.slice(0, 10);

  logEl.innerHTML = congestionEvents
    .map(
      (e) => `<li class="border-l-4 border-red-500 pl-2">
        <div class="font-medium text-white">🚗 Congestion detected — ${e.carCount} cars</div>
        <div class="text-text-dim text-xs">${e.time}</div>
      </li>`
    )
    .join("");
}

setupFeed().then(() => {
  video.addEventListener("loadeddata", () => {
    runDetectionCycle();
    setInterval(runDetectionCycle, CAPTURE_INTERVAL_MS);
  });
});