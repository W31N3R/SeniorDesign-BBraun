import cv2

# Initialize the webcam
cap = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()

qr_data = None  # This will store the QR code contents

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect and decode the QR code
    data, bbox, _ = qr_detector.detectAndDecode(frame)

    # If a QR code is detected and decoded
    if bbox is not None and data:
        qr_data = data
        print(f"QR Code Data: {qr_data}")
        # Optionally, draw a box around the QR code
        for i in range(len(bbox)):
            pt1 = tuple(bbox[i][0])
            pt2 = tuple(bbox[(i + 1) % len(bbox)][0])
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("QR Code Scanner", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()

# qr_data now holds the last QR code read
print(f"Final QR Code Data: {qr_data}")
