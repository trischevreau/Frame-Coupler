"""
@author: Tristan Chevreau

A converter for transforming mp4 videos to jpg grayscales.

Input :
- mp4 video

Output :
- a jpg grayscale for each frame, usable for OCR, whose name is its frame number.
- a pickle file linking the image file name to the timestamp.
"""

import os
import cv2
import pickle
from tkinter.filedialog import askopenfilename

from data.constants import timestamps_filename


def progress_bar(percent, length=20):
    """ This displays a progress bar in command-line, erasing the last line.
    :param percent: the percentage at which the progress bar is full
    :param length: the size of the progress bar
    :return: None
    """
    str_ = "#" * int(length*percent/100)
    while len(str_) < length:
        str_ += "-"
    n, d = str(round(percent, 2)).split(".")
    print(f"[step1][{n.zfill(2)}.{d.ljust(2, '0')}%] converting ... [{str_}]", end='\r')


def step1_conversion(file_name, folder_name, callback=lambda r: None):
    """ This function contains all the things to execute during step1.
    :param file_name: the name of the .mp4 file to convert.
    :param folder_name: the folder in which to save the frames.
    :param callback: the function to call to update a display.
    :return: None
    """
    # create the folder
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    # open the video
    cap = cv2.VideoCapture(file_name)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    count = 0
    timestamps = {}
    # read it until the end
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:  # if the frame was not kept ...
            continue  # ... ignore it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        timestamps[f"{count:08d}.jpg"] = cap.get(cv2.CAP_PROP_POS_MSEC)
        cv2.imwrite(folder_name + "/" + f"{count:08d}" + ".jpg", gray)
        count += 1
        if count > (video_length - 1):  # if we read all the frames ...
            cap.release()  # ... close the video
        callback(count / video_length * 100)
    # save the timestamps
    with open(folder_name + timestamps_filename, "wb") as f:
        pickle.dump(timestamps, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__=="__main__":

    print("[step1] choose the path of the video")
    video_path = askopenfilename(filetypes=[("MPEG4 File", "*.mp4")])
    if video_path == "":
        raise ValueError("you did not enter a filepath")
    print()

    print()
    print("[step1] beginning conversion ...")
    print()

    step1_conversion(video_path, ".".join(video_path.split(".")[:-1]), callback=progress_bar)
    print(f"[step1] > {video_path} was converted to jpg grayscales and timestamps pickle")
    print()
