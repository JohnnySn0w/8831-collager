from PIL import Image
import multiprocessing as mp
import sys
# from pprint import pprint


import pandas as pd
from sklearn.neighbors import NearestNeighbors

# Load your CSV data
csv_path = 'image_values.csv'  # Update this path to your CSV file
image_data = pd.read_csv(csv_path)

# Assuming your CSV has columns 'Image Name', 'Flashy', 'Mean Red', 'Mean Green', 'Mean Blue'
# Filter out flashy images if necessary
image_data = image_data[image_data['Flashy'] == False]

# Extract RGB values
rgb_values = image_data[['Mean Red', 'Mean Green', 'Mean Blue']].values

# Build a k-d tree
nn = NearestNeighbors(n_neighbors=1, algorithm='kd_tree')
nn.fit(rgb_values)

# Define the function to find the closest image
def find_closest_image(args):
    x, y, pixel_rgb = args
    distance, index = nn.kneighbors([pixel_rgb])
    return x, y, image_data.iloc[index[0]]['Image Name'].values[0]

def main(image_path):
    # Load the image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = img.load()
    

    # Prepare arguments for multiprocessing: list of (x, y, pixel_value)
    args_list = [(x, y, pixels[x, y]) for x in range(img.width) for y in range(img.height)]

    # Setup multiprocessing pool
    pool = mp.Pool(mp.cpu_count())
    # pprint(args_list)
    # Process each pixel in parallel
    results = pool.map(find_closest_image, args_list)
    
    # Cleanup
    pool.close()
    pool.join()

    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['x', 'y', 'func_result'])

    # Save to CSV
    df.to_csv('pixel_results.csv', index=False)

if __name__ == '__main__':
    image_path = sys.argv[1]
    main(image_path)
