import os
import sys
import logging
import time
from zipfile import ZipFile, error
from tqdm import tqdm

from config import *
from gen_means import process_folder, dir_name, file_name
from parse_image import load_and_parse
from generate_movie import gen_movie


def unzip_banners():
    try:
        with ZipFile("./geocities_88x31_buttons_nodupes.zip", "r") as banner_zip:
            # this will create the buttons folder for us
            for member in tqdm(banner_zip.infolist(), desc="Extracting "):
                try:
                    banner_zip.extract(member, "./")
                except error as e:
                    pass
    except FileNotFoundError:
        logging.error(
            "You need to put the no-dupes geocities zip in the root directory."
        )
        exit(2)


def fill_banners_dir():
    if not os.listdir(dir_name):
        logging.info("Directory is empty, attempting extracting")
        unzip_banners()
        logging.info("extraction complete")
    else:
        logging.info("Directory is not empty, skipping extraction")


def unzip_banners_if_needed():
    if os.path.isdir(dir_name):
        fill_banners_dir()
    else:
        logging.info("Given directory doesn't exist, creating")
        os.makedirs(dir_name)
        fill_banners_dir()


def convert_that_image_boy():
    unzip_banners_if_needed()
    if not os.path.isfile(file_name):
        logging.info(f"Could not find {file_name}, generating.")
        process_folder()
    else:
        logging.info(f"found {file_name}")
    if len(sys.argv) < 2:
        logging.error("Please provide a filepath to the image you want to transform.")
        exit(2)
    elif not os.path.isfile(sys.argv[1]):
        logging.error("Please provide a valid path")
        exit(2)
    image_path = sys.argv[1]
    load_and_parse(image_path)
    gen_movie()


if __name__ == "__main__":
    t0 = time.time()
    convert_that_image_boy()
    t1 = time.time()
    logging.info(f"total time is {t1-t0}")
