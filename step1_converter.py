"""
@author: Tristan Chevreau

A converter for transforming mp4 videos to jpg grayscales.

Input :
- mp4 video

Output :
- a jpg grayscale for each frame, usable for OCR, whose name is its timestamp.
"""

import os
import cv2


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
    # read it until the end
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:  # if the frame was not kept ...
            continue  # ... ignore it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        cv2.imwrite(folder_name + "/" + str(timestamp).replace('.', '_') + ".jpg", gray)
        count += 1
        if count > (video_length - 1):  # if we read all the frames ...
            cap.release()  # ... close the video
        callback(count / video_length * 100)


if __name__=="__main__":

    print("### converter")
    print()

    video_path = input("Input the path of the video : ")
    if not os.path.isfile(video_path):
        raise ValueError("you did not enter valid filepath")
    if not video_path.split(".")[-1] == "mp4":
        raise ValueError("not a .mp4 file")

    print()
    print("beginning conversion ...")
    print()

    step1_conversion(video_path, ".".join(video_path.split(".")[:-1]), callback=progress_bar)
    print(f"> {video_path} was converted to jpg grayscales")
    print()
