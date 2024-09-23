import os
import requests
import json
from PIL import Image
from io import BytesIO
import datetime
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

def grabImages():
  imagesWritten = 0

  for i in locations:
      response = json.loads(requests.get('https://mkt-api.gcu.edu/linecam/api/v1/images?includeImages=true&includeInactive=false&location=' + i).text)
      for camera in response:
          print(f"{camera['description']}  ID: {camera['id']}  Time: {camera['updated_at']}")

          timeString = datetime.datetime.strptime(camera['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d-%H%M%S")

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

          imagesWritten += 1

  print(f"Success! Images Written: {imagesWritten}")
