from flask import Flask, request, render_template
from tinydb import Query
from CountPeople import peopleDetectAndDB, db
import threading
import time
from datetime import datetime
from dbMan import delete_old_records

app = Flask(__name__)

# Function to add random numPeople to the DB every 10 minutes
def update_db():
    while True:
        delete_old_records()
        peopleDetectAndDB()
        time.sleep(600)  # Sleep for 600 seconds (10 minutes)

# Start the background thread for updating the DB every 10 minutes
def start_background_thread():
    threading.Thread(target=update_db, daemon=True).start()
    
# Function to calculate the color based on numPeople
def calculate_color(num_people):
    if num_people < 0:
        num_people = 0
    elif num_people > 30:
        num_people = 30
    red = int((num_people / 30) * 255)
    green = int((1 - (num_people / 30)) * 255)
    return f'rgb({red}, {green}, 0)'
    
@app.route('/')
def index():
    # Get all unique locations
    Location = Query()
    all_records = db.all()

    # Create a dictionary to store the most recent numPeople count per location
    location_people_counts = {}

    # Loop through all records and store the latest numPeople count for each location
    for record in all_records:
        location = record['location']
        timestamp = record['timestamp']
        # If the location is not already added or the current record is newer, update the dictionary
        if location not in location_people_counts or timestamp > int(location_people_counts[location]['timestamp']):
            location_people_counts[location] = {
                'numPeople': record['numPeople'],
                'timestamp': record['timestamp'],
                'humanTime': datetime.fromtimestamp(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                'imagePath': record['imagePath'],  # Include image path here
                'color': calculate_color(record['numPeople'])  # Calculate color based on numPeople
            }
            
    # Sort by most busy or least busy based on user selection
    sort_order = request.args.get('sort', 'most_busy')  # Default to most busy
    if sort_order == 'least_busy':
        sorted_locations = sorted(location_people_counts.items(), key=lambda x: x[1]['numPeople'])
    else:
        sorted_locations = sorted(location_people_counts.items(), key=lambda x: x[1]['numPeople'], reverse=True)

    # Render the data in an HTML template
    return render_template('index.html', locations=sorted_locations)


if __name__ == '__main__':
    # Start the background thread
    start_background_thread()

    # Run the Flask app
    app.run(debug=True)
