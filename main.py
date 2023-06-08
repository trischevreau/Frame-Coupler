"""
@author: Tristan Chevreau

Uses the separate steps to make all of them.
"""

import os

from run_parameters import *
from step1_converter import step1_conversion, progress_bar
from step2_rawOCR import step2
from step3_clockfitting import step3
from step4_framecoupler import step4


if __name__=="__main__":

    """
    0 : bare minimum (load status, warnings, errors, ...) - command line only
    1 : + progress info, some results - command line only
    2 : + last fitting, common time frame, coupling quality vs quantity, coupled frames and variance of the coupling
    3 : + intermediate fittings, last residual error of fitting
    """

    print()
    print("### VIDEO FRAME COUPLER")
    print()
    print("### running parameters (can be changed in the run_parameters.py file) :")
    print(f"### user info level = {info_level}/3 ; save = {save}")
    print(f"### Tesseract EXE filepath {pytesseract_exe_file_path}")
    print()

    # choose the videos
    try:
        n_videos = int(input("### [c] how many videos to couple ? "))
        assert n_videos >= 2
    except ValueError:
        raise ValueError("you did not enter a valid number of videos")
    except AssertionError:
        raise ValueError("the number of videos should be an integer greater than 1")

    try:
        repeat_frame = int(input("### [c] between how many frames should we perform OCR ? "
                                 "(1 means every frame, 2 means every other frame, etc.) "))
        assert repeat_frame > 0
    except ValueError:
        raise ValueError("you did not enter a valid number of frames")
    except AssertionError:
        raise ValueError("the number of frames should be an integer greater than 0")

    print("### [c] select the filepath of the videos")
    video_paths = []
    for i in range(n_videos):
        video_paths.append(input(f"### [c] input the absolute filepath of video {i+1} : "))
        if not os.path.isfile(video_paths[-1]):
            raise ValueError("you did not enter valid filepath")
        if not video_paths[-1].split(".")[-1] == "mp4":
            raise ValueError("not a .mp4 file")
        print(f"### [i] video {i} is {video_paths[-1]}")


    res_path = input("### [c] where do you want to output the results (absolute path) ? ")
    try:
        os.makedirs(res_path)
    except FileNotFoundError:
        raise ValueError("not a valid folder path")
    except FileExistsError:
        pass
    print(f"### [i] results folder is {res_path}")

    print()
    print("### STEP 1 : Conversion to frames")
    print()

    answer = "n"
    if all([os.path.isdir(".".join(video_path.split(".")[:-1])) for video_path in video_paths]):
        answer = input("### [c] it seems like the videos were already converted to gray frames, is it correct ? (Y/n) ")

    if answer.lower() == "n":

        print("### beginning conversion(s) ...")
        print()

        for video_path in video_paths:
            step1_conversion(video_path, ".".join(video_path.split(".")[:-1]), callback=progress_bar)
            print(f"> {video_path} was converted to jpg gray frames")


        print("### ACTION : please delete any unwanted frame in the explorer now ...")
        input("### ACTION : press enter when it is done")
    else:
        print("### [i] skipping step 1")
    video_paths = [".".join(video_path.split(".")[:-1]) for video_path in video_paths]

    print()
    print("### STEP 2 : raw OCR")
    print()

    for video_path in video_paths:
        step2(video_path, info_level=info_level, repeat_frame=repeat_frame)
        print(f"[step2] finished OCR on {video_path}")
        print()

    print()
    print("### STEP 3 : clock fitting")
    print()

    for video_path in video_paths:
        step3(video_path, info_level=info_level)
        print(f"[step3] finished clock fitting on {video_path}")
        print()

    print()
    print("### STEP 4 : frame coupling")
    print()

    step4(video_paths, results_save_path_=res_path, save_=save, info_level_=info_level)

    print()
    print("### DONE")
    print()
