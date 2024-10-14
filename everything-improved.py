import torch
import cv2
import pandas as pd
import os
import requests
import json
from PIL import Image
from io import BytesIO
from datetime import datetime
import time

imageDumpFolder = "input_images"

locations = [
  "31st Ave. Parking Garage",
  "Aqua Fria Apartments (76)",
  "Camelback Hall (37)",
  "Chaparral Hall (45)",
  "Diamondback Apartments (50)",
  "GCU Arena (38)",
  "Juniper Hall (84)",
  "Prescott Hall (36)",
  "Roadrunner Appartments (28)",
  "Student Union (29)",
  "Technology Building (57)",
  "Thunderground (11)",
  "Turquoise Apartments (61)",
  "Verde River Apartments (78)"
]

# Log file setup
log_file = 'camera_log.csv'
log_columns = ['id', 'Updated', 'Location']
log_data = []

def getLocationImage(location):
    response = json.loads(requests.get('https://mkt-api.gcu.edu/linecam/api/v1/images?includeImages=true&includeInactive=false&location=' + location).text)
    for camera in response:
        print(f"{camera['description']}  ID: {camera['id']}  Time: {camera['updated_at']}")

        timeString = datetime.strptime(camera['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d-%H%M%S")

        imageName = f"{camera['id']}_{camera['description']}_{timeString}.jpg"
        saveStructure = f"./{imageDumpFolder}/"

        try:
            image = Image.open(BytesIO(requests.get(camera['url']).content))
        except:
            print(f"Unable to open image of {camera['description']}")
            
        if not os.path.exists(saveStructure):
            os.makedirs(saveStructure)

        try:
          image.save(os.path.join(saveStructure, imageName))
        except:
          print(f"Unable to save image of {camera['description']}")
        
        log_data.append([camera['id'], camera['updated_at'], camera['description']])
    
    log_df = pd.DataFrame(log_data, columns=log_columns)
    log_df.to_csv(log_file, index=False)
    

def grabImages():
    imagesWritten = 0

    for location in locations:
        getLocationImage(location)

    print(f"Success! Images Written: {imagesWritten}")



# Define which images need to be grabbed

# Grab image
    # Count the people
    # write the data with the timestamp of the photo
    # next image

grabImages()

# Load YOLOv5 model (using a larger model for better accuracy)
model = torch.hub.load('ultralytics/yolov5', 'yolov5m')  # Use yolov5m instead of yolov5s for better accuracy

# Directory containing input images
input_images = 'input_images'  # Folder containing images for detection
os.makedirs(input_images, exist_ok=True)  # Ensure the folder exists

# Directory to save annotated images
output_images = 'output_images'
os.makedirs(output_images, exist_ok=True)

# Log file setup
log_file = 'detection_log.csv'
log_columns = ['Timestamp', 'Object', 'Confidence', 'Image', 'People Count']
log_data = []

# Confidence threshold
confidence_threshold = 0.15  # Increased confidence threshold for better accuracy

images = os.listdir(input_images)

# Process each image in the input folder
for image_file in images:
    image_path = os.path.join(input_images, image_file)

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not open image {image_file}")
        continue

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
    print(f"Image {image_file}: Detected {people_count} people.")

    # Log detected person
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_data.append([timestamp, 'person', row[4], image_file, people_count])

    # Save annotated image
    output_image_path = os.path.join(output_images, image_file)
    cv2.imwrite(output_image_path, image)
    print(f"Annotated image saved to {output_image_path}")

# Save log data to CSV
log_df = pd.DataFrame(log_data, columns=log_columns)
log_df.to_csv(log_file, index=False)

print(f"Detection log saved to {log_file}")
print(f"Annotated images saved to {output_images}")
