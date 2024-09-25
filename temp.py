import glob
import pickle
import json
import os
from datetime import datetime


def find_new_continent_openings():
    old_data_path = "D:/ZaleniaData.OLD/WorldData"
    continent_openings = {}
    
    # Get all world data files and sort them by last modified time
    world_data_files = sorted(glob.glob(f"{old_data_path}/*"), key=os.path.getmtime)
    
    for file_path in world_data_files:
        with open(file_path, "rb") as fp:
            world_data = pickle.load(fp)
        
        # Get last modified timestamp
        file_timestamp = os.path.getmtime(file_path)
        file_name = os.path.basename(file_path)
        
        # Check if world_data is a string (JSON)
        if isinstance(world_data, str):
            try:
                world_data = json.loads(world_data)
            except json.JSONDecodeError:
                print(f"Skipping file {file_path}: Invalid JSON")
                continue
        
        # Ensure world_data is a dictionary and has 'continents' key
        if isinstance(world_data, dict) and 'continents' in world_data:
            for continent in world_data["continents"]:
                cont_id = continent["continentIdentifier"]
                
                if cont_id not in continent_openings and continent["cities"]:
                    continent_openings[cont_id] = {
                        "timestamp": file_timestamp,
                        "file": file_name
                    }
        else:
            print(f"Skipping file {file_path}: Invalid data format")
    
    # Print results
    print("New Continent Openings:")
    for cont_id, data in sorted(continent_openings.items(), key=lambda x: x[1]["timestamp"]):
        print(f"Continent {cont_id}: {data['file']} - {format_timestamp(data['timestamp'])}")

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Call the function to find new continent openings
find_new_continent_openings()
