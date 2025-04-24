import torch
import cv2
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'webapp')))
from app import add_fine

# Load YOLOv5 pretrained model  
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)

# Define allowed vehicle classes
VEHICLE_CLASSES = ['car', 'truck', 'bus', 'motorcycle']

def run_detection(video_source=0):
    cap = cv2.VideoCapture(video_source)

    # Debug: Check if video file or webcam opened successfully
    if not cap.isOpened():
        print("❌ Error: Could not open video source.")
        return

    print("✅ Video opened successfully.")

    # Folder to store screenshots
    screenshot_folder = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'screenshots')
    os.makedirs(screenshot_folder, exist_ok=True)  # Ensure the folder exists

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame.")
            break

        # Run YOLO detection
        results = model(frame)
        detections = results.pandas().xyxy[0]

        # Filter only vehicle classes
        vehicles = detections[detections['name'].isin(VEHICLE_CLASSES)]

        for _, row in vehicles.iterrows():
            x1, y1, x2, y2 = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
            label = f"{row['name']} {row['confidence']:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Generate a temporary vehicle_id (could be from a license plate or unique ID)
            vehicle_id = f"{int(time.time())}"  # Placeholder, replace with license plate or another method
            print(f"✅ Generated vehicle_id: {vehicle_id}")  # Debugging: Check vehicle_id

            # Save screenshot in the static/screenshots folder
            filename = f"{vehicle_id}_{int(time.time())}.jpg"
            path = os.path.join(screenshot_folder, filename)
            cv2.imwrite(path, frame)

            print(f"✅ Screenshot saved at: {path}")  # Debugging: Check the image path

            # Add fine to DB with the relative path for Flask to serve the image
            relative_path = f"screenshots/{filename}"
            add_fine(vehicle_id, relative_path)

        # Display the frame with bounding boxes
        cv2.imshow('YOLO Vehicle Detection', frame)

        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quitting detection...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detection("sample_road_video.mp4")  # Or use 0 for webcam
