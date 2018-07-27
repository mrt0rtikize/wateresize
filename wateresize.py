"""
Simple script that sets watermark and resizes image to the given percentage.

"""

import sys
from os import listdir, mkdir
from os.path import isfile, join, exists
from wand.image import Image
from wand import exceptions
import argparse
import logging
from os import remove as rmfile
from settings import settings

# logging
logging.basicConfig(filename="wateresize.log", level=logging.DEBUG)


# ===============================
# Check if directory exists
# =============================== 
def check_in_path(path):
    if not exists(path):
        logging.error("{0} directory does not exists.".format(path))
    return path


# ===============================
# Create output directory if does not exist
# =============================== 
def create_out_path(out):
    if not exists(out):
        logging.info("Creating directory {0}.".format(out))
        mkdir(out)
        logging.info("Created directory {0}.".format(out))
    return out


# ===============================
# Determine orientation from exif 
# =============================== 
def orientation(img):
    for k, v in img.metadata.items():
        if k.startswith("exif:Orientation"):
            return v


# ===============================
# Change image (or logo) size
# ===============================
def img_resize(img, is_logo=False):
    if is_logo:
        tmp_width = settings.logo_width
        tmp_height = settings.logo_height
    else:
        tmp_width = settings.img_width
        tmp_height = settings.img_height

    try:
        current_ratio = img.width / img.height
        planned_ratio = int(tmp_width) / int(tmp_height)
        if current_ratio == planned_ratio:
            img.resize(int(tmp_width), int(tmp_height))
        elif current_ratio > planned_ratio:
            img.resize(int(tmp_width), round(int(tmp_width) / current_ratio))
        else:
            img.resize(round(int(tmp_height) * current_ratio), int(tmp_height))
    except ValueError as e:
        logging.error(e)
    return img


# ===============================
# Rotate if necessary and set watermark
# =============================== 
def watermark_position(img, watermark):
    orient = orientation(img)
    logging.info("orientation = {0}".format(orient))
    if (orient == "8"):
        img.rotate(-90)
        set_watermark(img, watermark)
        img.rotate(90)
    elif (orient == "6"):
        img.rotate(90)
        set_watermark(img, watermark)
        img.rotate(-90)
    else:
        set_watermark(img, watermark)


# ===============================
# Set watermark at the bottom-left corner of the image
# ===============================                     
def set_watermark(img, watermark):
    if settings.logo_width != '' and settings.logo_height != '':
        watermark = img_resize(watermark, True)
    if settings.horizontal is 'r' or settings.horizontal is 'R':
        horizontal = img.width - watermark.width - settings.horisontal_padding
    elif settings.horizontal is 'l' or settings.horizontal is 'L':
        horizontal = settings.horisontal_padding
    else:
        logging.error('Wrong settings.horizontal value in settings.py!')
    if settings.vertical is 'b' or settings.vertical is 'B':
        vertical = img.height - watermark.height - settings.vertical_padding
    elif settings.vertical is 't' or settings.vertical is 'T':
        vertical = settings.vertical_padding
    else:
        logging.error('Wrong settings.verticat value in settings.py!')
    logging.debug('logo position: ' + str(horizontal) + str(vertical))
    img.watermark(watermark, transparency=settings.transparency, left=horizontal, top=vertical)


"""
BEGIN
"""
# Parse args
parser = argparse.ArgumentParser(description='Set watermark on left-bottom corner and resize image.')
parser.add_argument('-w', "--watermark", action="store", dest="w", help="watermark image to set. If missing, watermark"
                                                                        " will not be set.")
parser.add_argument('-i', "--input", action="store", dest="i", required=True, help="input directory (mandatory).")
parser.add_argument('-o', "--output", action="store", dest="o", default="/tmp/resize/", help="output directory.")

args = parser.parse_args()

# Checks
in_path = check_in_path(args.i)
out_path = create_out_path(args.o)
if args.w:
    watermark = Image(filename=args.w)

# Run
logging.info("Resizing all files from {0}. Output to {1}".format(in_path, out_path))
for f in listdir(in_path):
    filename = join(in_path, f)
    if isfile(filename):
        logging.info(filename)
        try:
            with Image(filename=filename) as img:
                logging.debug("Size before {0}.".format(img.size))
                if settings.img_width != '' and settings.img_height != '':
                    img = img_resize(img)
                if args.w:
                    watermark_position(img, watermark)
                img.save(filename=out_path + "/" + f)
                logging.debug("Size after {0}.".format(img.size))
                rmfile(in_path + "/" + f)
        except exceptions.MissingDelegateError as error:
            logging.error(
                "MissingDelegateError. It seems like file {0} is not an image. Error: ".format(filename) + str(error))
        except Exception as e:
            logging.error("Image processing error:", e)

"""
END
"""
