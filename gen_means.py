from typing import Tuple
import struct
from PIL import Image, ImageSequence, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 1000000000  

import numpy as np
import os
import csv
import multiprocessing

from config import *

def calculate_frame_rgb(frame):
    # Ensure image is in RGBA for transparency handling
    if frame.mode != 'RGBA':
        frame = frame.convert('RGBA')
    
    # Create a blank (white) background image
    background = Image.new('RGB', frame.size, (255, 255, 255))
    # Paste the frame onto the background, using the frame's alpha channel as the mask
    background.paste(frame, mask=frame.split()[3])  # 3 is the index of the alpha channel

    pixels = np.array(background)

    # Calculate mean RGB values
    mean_rgb = np.mean(pixels[:, :, :3], axis=(0, 1))
    return mean_rgb

def process_image(image_path, flashy_threshold)-> Tuple[bool, np.ndarray]:
    """Calculate the mean RGB value of an image, considering both single and multilayer images,
    and accounting for alpha channels and interlacing."""
    try:
        with Image.open(image_path) as img:
            # Initialize sums and pixel count
            mean_rgbs = []
            
            # Process each frame in the image
            for frame in ImageSequence.Iterator(img):
                mean_rgb = calculate_frame_rgb(frame)
                mean_rgbs.append(mean_rgb)

            #calc overall image means
            image_means = np.mean(mean_rgbs, axis=0)
            image_means = [round(x) for x in image_means]
            if len(mean_rgbs) < 2:
                # Single frame, or not enough data to determine flashiness
                return False, image_means
            
            # Calculate standard deviation across frames for each RGB channel
            std_devs = np.std(mean_rgbs, axis=0)

            is_flashy = np.any(std_devs > flashy_threshold)
            # if is_flashy:
            #     logging.info(f'found flashy {image_path}')
            return is_flashy, image_means
    except (OSError, ValueError, IndexError, Image.DecompressionBombError, struct.error) as e:
        logging.info(f"Error processing image {image_path}: {e}")
        return False, [0, 0, 0]  # or another appropriate default value

def process_image_wrapper(args):
    """Wrapper for the process_image function to fit the multiprocessing map method."""
    image_path, flashy_threshold = args
    return process_image(image_path, flashy_threshold)

def process_folder(folder_path, output_csv):
    """Process each image in a folder and write mean RGB values to a CSV file."""
    # Define CSV headers
    headers = ['Image Name', 'Flashy', 'Mean Red', 'Mean Green', 'Mean Blue']
    flashy_threshold = 30
    image_paths = [
        os.path.join(folder_path, filename)
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
    ]
    args = [(image_path, flashy_threshold) for image_path in image_paths]
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    results = pool.map(process_image_wrapper, args)

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        

        for result, image_path in zip(results, image_paths):
            flashy, mean_rgb = result
            filename = os.path.basename(image_path)
            if type(mean_rgb) is list:
                writer.writerow([filename, flashy] + mean_rgb)
                continue
            writer.writerow([filename, flashy] + list(mean_rgb.tolist()))
    
    logging.info(f"Processed folder '{folder_path}' and saved output to '{output_csv}'.")

# Specify your folder path and output CSV file name
folder_path = './buttons'
output_csv = 'image_values.csv'


if __name__ == "__main__":
    process_folder(folder_path, output_csv)
