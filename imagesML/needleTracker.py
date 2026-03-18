from ultralytics import YOLO
import cv2
import numpy as np

# Load YOLOv8 model (pre-trained on COCO dataset)
model = YOLO("yolov8n.pt")  # Small, fast model (or use "yolov8s.pt" for better accuracy)

# Load the image
image_path = "image.jpg"
image = cv2.imread(image_path)

# Run object detection
results = model(image)

# Process results
for result in results:
    for box in result.boxes:
        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])  # Get coordinates
        confidence = box.conf[0]  # Confidence score
        label = result.names[int(box.cls[0])]  # Class label
        
        # Draw bounding box on the image
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(image, f"{label}: {confidence:.2f}", (x_min, y_min - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Print coordinates
        print(f"Detected {label}: (x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max})")

# Show result
cv2.imshow("Detected Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
