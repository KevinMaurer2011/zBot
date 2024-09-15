import glob
import pickle
import json
import os


def print_world_data():
    # Find the latest world data file
    latest_world_data_file = max(
        glob.glob("D:/ZaleniaData/WorldData/*"), key=os.path.getctime
    )

    # Load the data
    with open(latest_world_data_file, "rb") as fp:
        world_data = pickle.load(fp)

    # Parse the JSON data
    world_data = json.loads(world_data)

    # Print the world data
    print("World Data:")
    print(json.dumps(world_data, indent=2))


# Call the function to print the world data
print_world_data()
