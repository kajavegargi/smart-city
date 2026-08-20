"""
detect.py — Member 4
YOLOv8 detection logic. Isolated on purpose: no other module should have
to import from here except detect_routes.py (the Flask route) and,
later, data_simulator/event_sim.py (Member 3's congestion trigger).

Exact task from the plan doc:
  "loads YOLOv8 nano model (ultralytics package), function that takes
   an image/frame and returns detected objects as JSON
   (e.g. [{"class": "car", "count": 4}])"
"""

from ultralytics import YOLO
from collections import Counter
import io
from PIL import Image

# Load the model once at import time (not on every request — that's slow).
# 'yolov8n.pt' = nano model, smallest/fastest, good enough for a demo.
model = YOLO("yolov8n.pt")

# Threshold used later to decide "is this congestion?"
CAR_COUNT_THRESHOLD = 5


def detect_objects(image_bytes):
    """
    Takes raw image bytes (e.g. from a Flask file upload) and returns
    detected objects as a list of dicts, grouped by class:

        [{"class": "car", "count": 4}, {"class": "person", "count": 2}]

    This is the function detect_routes.py calls.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    results = model(image, verbose=False)  # run inference
    result = results[0]

    class_names = result.names  # {0: 'person', 2: 'car', ...}
    counts = Counter()

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id]
        counts[class_name] += 1

    detections = [{"class": name, "count": count} for name, count in counts.items()]
    return detections


def check_congestion_trigger(detections):
    """
    Looks at a detections list and decides whether it should fire a
    traffic congestion event, per the doc:
      "if > 5 cars detected → trigger congestion event"

    Returns the car count if triggered, otherwise None.
    Keeping this as a pure function (no DB writes) makes it easy to
    unit test and easy for Member 3 to reuse from event_sim.py.
    """
    car_count = next((d["count"] for d in detections if d["class"] == "car"), 0)
    if car_count > CAR_COUNT_THRESHOLD:
        return car_count
    return None
