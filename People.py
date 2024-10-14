import torch
import cv2
import pandas as pd
from datetime import datetime
import os

def loadModel() :
    # Load YOLOv5 model (using a larger model for better accuracy)
    model = torch.hub.load('ultralytics/yolov5', 'yolov5m')  # Use yolov5m instead of yolov5s for better accuracy
    return model

def detect(image_path, model, output_path, threshold):
    
    confidence_threshold = threshold  # Increased confidence threshold for better accuracy
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not open image")
        exit()  

    # Perform object detection
    results = model(image)

    # Get detection results
    labels, cords = results.xyxyn[0][:, -1].numpy(), results.xyxyn[0][:, :-1].numpy()

    # Annotate frame and count people
    image_height, image_width = image.shape[:2]
    people_count = 0  # Variable to count people
    n = len(labels)
    for i in range(n):
        row = cords[i]
        if row[4] >= confidence_threshold and model.names[int(labels[i])] == 'person':  # Filter for 'person' class
            x1, y1, x2, y2 = int(row[0] * image_width), int(row[1] * image_height), int(row[2] * image_width), int(row[3] * image_height)
            bgr = (0, 255, 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), bgr, 2)
            text = f"Person {row[4]:.2f}"
            cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, bgr, 2)

            # Increment the person count
            people_count += 1

    # Print the number of people detected in the image
    print(f"Detected {people_count} people.")

    
    return people_count, image
