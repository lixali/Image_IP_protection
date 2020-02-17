#!/usr/bin/python3.5

import os 
import argparse
import sys


#parser = argparse.ArgumentParser()
#parser.add_argument("-a", "--log", required=True)
#args = parser.parse_args()

f = open(sys.argv[1], "r+")
f2 = open("image_returned.txt", "w+")

for line in f:
    if "JPEG" in line:
        image = line
        image = image.replace("\n","")
    else:
        image = "not_found"

if "not_found" in image:
    f2.write("similar_image_not_found")
else:
    f2.write(image)
    command = "aws s3 cp s3://puretest1000/" + str(image) + " ./static"
    #print(command)
    os.system(command)


