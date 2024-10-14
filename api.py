from tinydb import TinyDB, Query
import requests
import json
from datetime import datetime
from People import loadModel, detect

db = TinyDB('./database/db.json')

area = 'Chaparral Hall (45)'

response = json.loads(requests.get('https://mkt-api.gcu.edu/linecam/api/v1/images?includeImages=true&includeInactive=false&location=' + area).text)

def addImageToDB(timestamp, location, numPeople) :
    
    image = {
        'timestamp': timestamp,
        'location': location,
        'numPeople': numPeople
    }
    
    return image

for location in response:
    print(location['description'])
    db.insert(addImageToDB(location['updated_at'], location['description'], 7))


Camera = Query()

locations = db.search(Camera.location == 'Lopes Mart')

for location in locations:
    print(location['numPeople'])
    