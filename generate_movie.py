import numpy as np
import pandas as pd
from PIL import Image, ImageSequence, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from moviepy.editor import ImageSequenceClip
import time
from multiprocessing import Pool, shared_memory

from config import *

"""Functions"""


def create_frame(
    df,
    dtype,
    frame_mem_name,
    frame_number,
    canvas_size,
    banner_width,
    banner_height,
):
    logging.info(f"processing frame {frame_number} in {frame_mem_name}")
    # Height and width are swapped in PIL, adjust for that when using canvas_size dimensions
    shape = (canvas_size[1], canvas_size[0], 4)
    frame_mem = shared_memory.SharedMemory(name=frame_mem_name, create=False)
    frame_array = np.ndarray(shape=shape, dtype=dtype, buffer=frame_mem.buf)
    frame_array.fill(0)

    for _, row in df.iterrows():
        image_path = row["func_result"]
        # Adjust x, y to scale up to the new grid
        x, y = int(row["x"]) * banner_width, int(row["y"]) * banner_height

        try:
            with Image.open(f"./buttons/{image_path}") as img:
                # Handle animated images
                if "duration" in img.info:
                    frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                    img_frame = frames[frame_number % len(frames)]
                else:
                    img_frame = img.convert("RGBA")

                # Catch conversion errors
                if img_frame.mode != "RGBA":
                    img_frame = img_frame.convert("RGBA")

                # Catch sizing errors
                if (
                    img_frame.size[0] > banner_width
                    or img_frame.size[1] > banner_height
                ):
                    img_frame = img_frame.crop((0, 0, banner_width, banner_height))
                # Paste the image frame onto the canvas
                img_array = np.array(img_frame)
                frame_array[y : y + banner_height, x : x + banner_width] = img_array
        except IndexError as e:
            # logging.error(f"Tried to parse frames but got {e}")
            # canvas.paste(blank, (x, y))
            pass
    # frame_array = np.array(canvas)
    frame_mem.close()


def gen_movie():
    # Determine number of frames for the video (based on the animated images)
    num_frames = 30  # for testing. Later, frames should be based on the maximum animated gif used's frames

    # Load CSV
    df = pd.read_csv("pixel_results.csv")
    orig_img = Image.open("downscaled.png")

    # Dimensions of the replacement images
    banner_width, banner_height = 88, 31

    # Calculate canvas size based on the original image dimensions
    canvas_size = (orig_img.width * banner_width, orig_img.height * banner_height)
    num_channels = 4
    dtype = np.uint8
    size = int(np.prod(canvas_size) * num_channels * np.dtype(dtype).itemsize)

    shape = (canvas_size[1], canvas_size[0], num_channels)

    # Create bundle of shared_mem objs, one per frame
    frame_mem_objs = [
        shared_memory.SharedMemory(create=True, size=size) for _ in range(num_frames)
    ]
    frame_names = [frame.name for frame in frame_mem_objs]

    # Create pool and exec
    args = [
        (
            df,
            dtype,
            frame_names[frame_number],
            frame_number,
            canvas_size,
            banner_width,
            banner_height,
        )
        for frame_number in range(num_frames)
    ]
    logging.info("Executing process pool")
    with Pool() as pool:
        pool.starmap(create_frame, args)

    # Now that the sh_mem objs are populated w/ frame data, collate them into a list of np arrays
    processed_frames = [
        np.ndarray(
            shape=shape,
            dtype=dtype,
            buffer=frame.buf,
        )
        for frame in frame_mem_objs
    ]

    # Create the video
    logging.info("processing video")
    clip = ImageSequenceClip(processed_frames, fps=10)  # Adjust FPS as needed
    clip.write_videofile(
        "output_video.mp4", codec="libx264", audio_codec="aac"
    )  # https://stackoverflow.com/a/70826414

    # cleanup
    logging.info("Cleaning up")
    for frame in frame_mem_objs:
        frame.close()
        frame.unlink()
    logging.info("Cleanup complete")


if __name__ == "__main__":
    t0 = time.time()
    gen_movie()
    t1 = time.time()
    logging.info(f"total time is {t1-t0}")
