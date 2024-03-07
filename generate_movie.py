from PIL import Image, ImageSequence, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
import pandas as pd
import numpy as np
from moviepy.editor import ImageSequenceClip
import sys
import math
from config import *

# Load CSV
df = pd.read_csv(sys.argv[1])
orig_img = Image.open(sys.argv[2])

# Dimensions of the replacement images
img_width, img_height = 88, 31

# Original image dimensions (to be replaced with actual dimensions)
original_width = orig_img.width  # Example, replace with the actual width
original_height = orig_img.height  # Example, replace with the actual height

# Calculate canvas size based on the original image dimensions
canvas_size = (original_width * img_width, original_height * img_height)

def create_frame(frame_number):
    # Create a blank canvas
    canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    blank = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))  # for blank frames
    for _, row in df.iterrows():
        image_path = row["func_result"]
        # Adjust x, y to scale up to the new grid
        x, y = int(row["x"]) * img_width, int(row["y"]) * img_height

        with Image.open(f"./buttons/{image_path}") as img:
            # Handle animated images
            if "duration" in img.info:
                try:
                    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                    img_frame = frames[frame_number % len(frames)]
                except IndexError as e:
                    logging.error(f"Tried to parse frames but got {e}")
                    img_frame = blank
            else:
                img_frame = img

            img_frame = img_frame.convert("RGBA")

            # Paste the image frame onto the canvas
            canvas.paste(img_frame, (x, y))

    return np.array(canvas)


# Determine number of frames for the video (based on the animated images)
num_frames = 30  # Adjust based on your needs

# Create the frames for the video
frames = [create_frame(f) for f in range(num_frames)]

# Create the video
clip = ImageSequenceClip(frames, fps=10)  # Adjust FPS as needed
clip.write_videofile(
    "output_video.mp4", codec="libx264", audio_codec="aac"
)  # https://stackoverflow.com/a/70826414
