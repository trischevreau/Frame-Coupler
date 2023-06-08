"""
@author: Tristan Chevreau

This is useful to generate test images for the frame coupling.
"""

import os
from PIL import Image, ImageDraw
from math import cos
import datetime

# parameters
video_frame_rate = 120 # Hz
clock_offset = 1.521 # s
event_offset = 0.03 # s
clock_frame_rate = 60 # Hz
event_rate = 1 # Hz
n_images = 121
sz = (200, 150) # px
video_folder_path = os.getcwd() + "/test_files/test2/"

# create the test folder
try:
    os.mkdir(video_folder_path)
except FileExistsError:
    pass

# main process is here
line_length = sz[0] - 2*10
for frame_nr in range(n_images):
    img = Image.new('L', sz, color=0)
    draw = ImageDraw.Draw(img)
    real_time  =  frame_nr / video_frame_rate + clock_offset
    displayed_time = (real_time // (1/clock_frame_rate)) / clock_frame_rate
    str_time = "0" + str(datetime.timedelta(seconds=real_time))[0:11]
    hours = int(real_time // 3600)
    minutes = int((real_time % 3600) // 60)
    seconds = int(real_time % 60)
    milliseconds = int((real_time % 1) * 1000)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    draw.text((10,10), formatted_time, fill=255)
    cosval = abs(cos(real_time * event_rate + event_offset))
    draw.text((10, sz[1]//2), str(cosval)[0:8], fill=255)
    draw.line(((10, sz[1]-10), (10 + cosval * line_length), sz[1]-10),
              fill=255, width=10)
    img.save(video_folder_path + str(frame_nr) + "_0.jpg")
