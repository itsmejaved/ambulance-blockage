# detection/detector.py

import torch
import cv2

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

        # Display the frame with bounding boxes
        cv2.imshow('YOLO Vehicle Detection', frame)

        # Quit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quitting detection...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detection("sample_road_video.mp4")  # Use 0 for webcam, or provide full video path
