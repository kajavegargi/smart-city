"""
test_detect.py — quick sanity check for detect.py, no Flask/browser needed.

Usage:
    python test_detect.py path/to/some_image.jpg

Good for testing before your webcam/demo setup is ready — grab any
street/traffic photo off Google, save it locally, and run this.
"""

import sys
from detect import detect_objects, check_congestion_trigger

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_detect.py <path_to_image>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        image_bytes = f.read()

    detections = detect_objects(image_bytes)
    print("Detections:", detections)

    triggered = check_congestion_trigger(detections)
    if triggered is not None:
        print(f"Congestion trigger WOULD fire — {triggered} cars detected (> 5)")
    else:
        print("No congestion trigger.")
