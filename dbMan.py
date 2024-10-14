from tinydb import TinyDB, Query
import os
from datetime import datetime, timedelta

# Initialize TinyDB
db = TinyDB('db.json')

def delete_old_records():
    # Get the current Unix timestamp
    current_time = int(datetime.now().timestamp())
    
    # Calculate the cutoff time for one hour ago in Unix timestamp
    cutoff_time = current_time - 300  # 3600 seconds in an hour

    # Query object for TinyDB
    Records = Query()
    
    # Remove records older than one hour
    oldRecords = db.search(Records.timestamp < cutoff_time)
    for oldRecord in oldRecords:
        os.remove(oldRecord['imagePath'])
        
    db.remove(Records.timestamp < cutoff_time)
    print(f"Deleted records older than one hour.")