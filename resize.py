"""
Simple script that sets watermark and resizes image to the given percentage.

Usage:

"""

import sys
# TODO import argparse
from os import listdir, mkdir
from os.path import isfile, join, exists, exists
from wand.image import Image
import argparse


# ===============================
# Check if directory exists
# =============================== 
def check_in_path(path):
    if not exists(path):
        raise "{0} directory does not exists.".format(path) 
    return path

# ===============================
# Create output directory if does not exist
# =============================== 
def create_out_path(out):
    if not exists(out):
        print "Creating directory {0}.".format(out)
        mkdir(out)
        print "Created directory {0}.".format(out)
    return out

# ===============================
# Check resize value. Values below 5 are not permitted
# ===============================         
def check_resize_value(value):
    if (value < 5):
        raise NameError("Invalid resize value: " + value)
    return str(value) + '%'

# ===============================
# Determine orientation from exif 
# =============================== 
def orientation(img):
    for k, v in img.metadata.items():
        if k.startswith("exif:Orientation"):
            return v
            
# ===============================
# Rotate if necessary and set watermark
# =============================== 
def watermark_position(img, watermark):
    orient = orientation(img)
    print "orientation = {0}".format(orient)
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
    img.watermark(watermark, transparency = 0.60, left = 15, top = img.height - watermark.height - 15)

"""
BEGIN
"""
# Parse args
parser = argparse.ArgumentParser(description='Set watermark on left-bottom corner and resize image.')
parser.add_argument('-w', "--watermark", action="store", dest="w", help="watermark image to set. If missing, watermark will not be set.")
parser.add_argument('-i', "--input", action="store", dest="i", required = True, help="input directory (mandatory).")
parser.add_argument('-o', "--output", action="store", dest="o", default="/tmp/resize/", help="output directory.")
parser.add_argument('-r', "--resize", action="store", dest="r", default="100", help="image resize percent. If missing will not resize image.")

args = parser.parse_args()

# Checks
in_path = check_in_path(args.i)
out_path = create_out_path(args.o)
resize_value = check_resize_value(args.r)
resize_v = int(args.r)
if args.w:
    watermark = Image(filename=args.w)

# Run
print "Resizing all files from {0}. Output to {1}".format(in_path, out_path)
for f in listdir(in_path):
    filename=join(in_path, f)
    if isfile(filename):
        print "---\n" + filename
        try:
            with Image(filename=filename) as img:
                print "Size before {0}.".format(img.size)
                if args.r:
                    img.transform(resize = resize_value)
                if args.w:
                    watermark_position(img, watermark) 
                img.save(filename = out_path + "/" + f)
                print "Size after {0}.".format(img.size)
        except Exception as e:
            print "Image processing error:", e

print "Finished processing images."
"""
END
"""
