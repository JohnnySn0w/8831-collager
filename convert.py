import logging
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import time

# local files
from config import *

start = time.perf_counter()
# Load your CSV data
csv_path = "image_values.csv"  # Update this path to your CSV file
image_data = pd.read_csv(csv_path)

# Assuming your CSV has columns 'Image Name', 'Flashy', 'Mean Red', 'Mean Green', 'Mean Blue'
# Filter out flashy images if necessary
image_data = image_data[image_data["Flashy"] == False]

# Extract RGB values
rgb_values = image_data[["Mean Red", "Mean Green", "Mean Blue"]].values

# Build a k-d tree
nn = NearestNeighbors(n_neighbors=1, algorithm="kd_tree")
nn.fit(rgb_values)


# Define the function to find the closest image
def find_closest_image(pixel_rgb):
    distance, index = nn.kneighbors([pixel_rgb])
    return image_data.iloc[index[0]]["Image Name"].values[0]


# Example usage
pixel_rgb = (200, 180, 0)  # Example pixel RGB value
find = time.perf_counter()
closest_image = find_closest_image(pixel_rgb)
end = time.perf_counter()
proc_time = end - find
total_time = end - start
logging.info(f"Closest image: {closest_image}")
logging.debug(f"Total processing time: {total_time:.6f} seconds")
logging.debug(f"processing time for actual search {proc_time:.6f} seconds")
logging.debug(f"For a 400x400 img this would be {(400*400)*proc_time:.6f} seconds")
