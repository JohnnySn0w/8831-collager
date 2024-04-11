from PIL import Image
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import multiprocessing as mp
import numpy as np
import sys
import math
import logging


def downscale_image(img, method=Image.LANCZOS):
    encoder_max = {"width": 8192, "height": 4320}
    target_height = encoder_max["height"] / 31  # "how many banners can fit?"
    target_width = encoder_max["width"] / 88

    original_width, original_height = img.size
    if original_width > original_height:  # Which dimension is larger?
        if original_width > target_width:
            ratio = math.ceil(original_width / target_width)
            target_width = original_width / ratio
            target_height = original_height / ratio
        else:
            return img
    elif original_height > target_height:
        ratio = math.ceil(original_height / target_height)
        target_width = original_width / ratio
        target_height = original_height / ratio
    else:
        return img

    resized_img = img.resize((round(target_width), round(target_height)), method)
    resized_img.save("./downscaled.png")
    return resized_img


# Define the function to find the closest image
def find_closest_image(args):
    x, y, pixel_rgb, nn, image_data = args
    distance, index = nn.kneighbors([pixel_rgb])
    return x, y, image_data.iloc[index[0]]["Image Name"].values[0]


def load_and_parse(image_path):
    # Load the image
    img = Image.open(image_path)
    img = downscale_image(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    pixels = img.load()

    # Load your CSV data
    csv_path = "image_values.csv"
    image_data = pd.read_csv(csv_path)

    # Assuming your CSV has columns 'Image Name', 'Flashy', 'Mean Red', 'Mean Green', 'Mean Blue'
    # Filter out flashy images if necessary
    image_data = image_data[image_data["Flashy"] == False]

    # Extract RGB values
    rgb_values = image_data[["Mean Red", "Mean Green", "Mean Blue"]].values

    # Build a k-d tree
    nn = NearestNeighbors(n_neighbors=1, algorithm="kd_tree")
    nn.fit(rgb_values)

    # Prepare arguments for multiprocessing: list of (x, y, pixel_value)
    args_list = [
        (x, y, pixels[x, y], nn, image_data)
        for x in range(img.width)
        for y in range(img.height)
    ]

    # Setup multiprocessing pool
    pool = mp.Pool(mp.cpu_count())
    # pprint(args_list)
    # Process each pixel in parallel
    results = pool.map(find_closest_image, args_list)

    # Cleanup
    pool.close()
    pool.join()

    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=["x", "y", "func_result"])

    # Save to CSV
    df.to_csv("pixel_results.csv", index=False)


if __name__ == "__main__":
    image_path = sys.argv[1]
    load_and_parse(image_path)
