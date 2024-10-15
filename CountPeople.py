from tinydb import TinyDB, Query
import requests
import json
import cv2
from datetime import datetime
import requests
import json
from io import BytesIO
from datetime import datetime
from Detect import loadModel, detect
import os
import numpy as np

db = TinyDB('./database/db.json')

model = loadModel()

buildings = [
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

def addImageToDB(camera_id, timestamp, location, numPeople, imagePath) :
    
    properties = {
        'id': camera_id,
        'timestamp': timestamp,
        'location': location,
        'numPeople': numPeople,
        'imagePath': imagePath
    }
    
    return properties

def peopleDetectAndDB():

    # Ensure the input_images directory exists
    input_images_path = './input_images'
    output_images_path = './static'

    os.makedirs(input_images_path, exist_ok=True)
    os.makedirs(output_images_path, exist_ok=True)

    for building in buildings:
        cameras = json.loads(requests.get(f'https://mkt-api.gcu.edu/linecam/api/v1/images?includeImages=true&includeInactive=false&location={building}').text)
        for camera in cameras:
            print(f"{camera['description']}  ID: {camera['id']}  Time: {camera['updated_at']}")

            timeString = datetime.strptime(camera['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d-%H%M%S")
            # nerd time zone (freaky)
            unixTime = int(datetime.fromisoformat(camera['updated_at'].replace("Z", "+00:00")).timestamp())
            
            # Define image name and path to save in input_images folder
            imageName = f"{camera['id']}_{camera['description']}.jpg"
            input_image_path = os.path.join(input_images_path, imageName)
            
            try: 
                # Step 1: Download the image and save it to input_images folder
                response = requests.get(camera['url'])
                image = BytesIO(response.content)

                # Convert BytesIO image into NumPy array (compatible with OpenCV)
                image_array = np.frombuffer(image.getvalue(), dtype=np.uint8)
                image_file = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if image_file is None:
                    raise ValueError("Failed to decode image")

                # Save the image to the input_images folder
                cv2.imwrite(input_image_path, image_file)
                print(f"Image saved to {input_image_path}")
                

                # Step 2: Pass the saved image to the detect function
                people_count, annotated_image = detect(input_image_path, model, output_images_path, 0.15)
                
                # Save the annotated image in the output_images2 folder
                output_image_path = os.path.join(output_images_path, imageName)
                cv2.imwrite(output_image_path, annotated_image)
                print(f"Annotated image saved to {output_image_path}")

                os.remove(input_image_path)
                print(f"Cleaned up input image {input_image_path}")
                
                # Add image information to the database
                imageInformation = addImageToDB(camera_id=camera['id'], timestamp=unixTime, location=camera['description'], numPeople=people_count, imagePath=output_image_path)
                db.insert(imageInformation)

            except Exception as e:
                print(f"Error: Could not process image - {e}")
