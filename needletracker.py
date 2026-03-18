import cv2
import numpy as np

def track_needle(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Unable to load image.")
        return

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use edge detection to find the needle
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Use HoughLinesP to detect lines in the image
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

    # Draw the lines on the image
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display the result
    cv2.imshow('Needle Tracking', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
track_needle('path_to_your_image.jpg')