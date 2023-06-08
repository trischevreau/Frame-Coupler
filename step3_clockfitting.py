"""
@author: Tristan Chevreau

Processes the raw OCR data to try and fit a model on the usable clock times.

Input :
- a folder path (the folder must contain the raw OCR results from step2)

Output :
- a file named "__clock_fitting" at the root of the folder path, which is the pickle of a dict of this form :
  > {TIMESTAMPS: the timestamps of the video (even those not used for fitting).
     COMPUTED_CLOCK_TIMES: all estimated clock times (this means, the fitting function applied to the timestamps).}
"""

import os
import pickle
from tkinter.filedialog import askdirectory

import numpy as np
import matplotlib.pyplot as plt

from data.vars import replacements
from data.constants import *


def process(text):
    """
    This function tries to transform a string into a usable clock time in the form 00:mm:ss:fff.
    Common character errors are replaced by their corresponding numbers (for example : @ = 0) (see data.vars)
    It detects 00 as the starting point of the string.
    :param text: the string to process
    :return: None if no starting point was found else the 12 next characters (supposedly 00:mm:ss:fff)
    """
    try:
        for confusion, number in replacements.items():
            if confusion in text:
                text = text.replace(confusion, number)
        i = 0
        while text[i:i+2] != "00" and i < len(text):
            i += 1
        if i >= len(text):
            return None
        text = text[i:i+13]
        return text
    except IndexError:
        return None


def convert_to_milliseconds(time_string):
    """ This function converts a hh:mm:ss:fff time string to milliseconds.
    :param time_string: The string in a hh:mm:ss:fff form
    :return: None if the step1_conversion was not possible else the value in milliseconds
    """
    try:
        milliseconds = (int(time_string[0:2]) * 3600 + int(time_string[3:5]) * 60 + int(time_string[6:8])) * 1000
        milliseconds +=  int(time_string[9:12].zfill(3))
        return milliseconds
    except ValueError:
        return None
    except TypeError:
        return None


def cleanup_values(mask_):
    """ This functions filters clock_times and filtered_timestamps according to mask_.
    :param mask_: the mask to apply to clock_times and filtered_timestamps
    :return: the number of deleted values
    """
    global clock_times, filtered_timestamps
    length_before = len(clock_times)
    clock_times = [ct for ct, me in zip(clock_times, mask_) if me == False]
    filtered_timestamps = [ts for ts, me in zip(filtered_timestamps, mask_) if me == False]
    return length_before - len(clock_times)


def step3(video_path_, info_level=3, interval_to_analyze_=(0, None), residual_thresholds_=(2000, 500, 100)):
    """ This function contains all the things to execute during step3.
    :param info_level: sets the quantity of intermediate plots and info that will be shown (0 is lesser)
    :param residual_thresholds_: the thresholds to apply for each iteration of the residual method
    :param interval_to_analyze_: interval of frames to analyze
    :param video_path_: the path containing __raw_OCR_results in which to save __clock_fitting
    :return: True when the step is successful
    """

    global clock_times, filtered_timestamps

    clock_times = []  # ms
    timestamps = []  # arbitrary time units
    filtered_timestamps = []  # arbitrary time units

    # load the results
    with open(video_path_ + raw_OCR_results_filename, "rb") as f:
        results = pickle.load(f)
    if info_level >= 1:
        print(f"[step3][i] raw OCR results loaded from {video_path_}")
    m, M = interval_to_analyze_
    if M is None:
        M = len(results.keys())
    number_of_frames = M - m

    # process the raw OCR results to usable milliseconds clock times
    n_letters = len(str(number_of_frames))
    for i, file_ in enumerate(sorted(results.keys(),
                                     key=lambda k: float(k.replace(".jpg", "").replace("_", ".")))[m:M]):
        frame_str = results[file_]
        frame_ms = convert_to_milliseconds(process(frame_str))
        if info_level >= 1:
            print(f"[step3][i][{str(i+1).zfill(n_letters)}/{number_of_frames}] {frame_str} becomes {frame_ms} ms")
        clock_times.append(frame_ms)
        timestamps.append(float(file_.replace(".jpg", "").replace("_", ".")))
    print(f"[step3][i] computed {len(clock_times)} values.")
    filtered_timestamps = list(timestamps)

    # get rid of unusable string times
    mask = [True if e is None else False for e in clock_times]
    print(f"[step3][w] {cleanup_values(mask)} values were unreadable")

    # get rid of times that are obviously too high
    mask = [False if v <= np.quantile(clock_times, 0.7) * 2 else True for v in clock_times]
    print(f"[step3][w] {cleanup_values(mask)} values were obviously too high")

    print(f"[step3][w] there is {len(filtered_timestamps)} values left")

    # using a residual approach, fine-tune the fitting
    fit = np.polyfit(filtered_timestamps, clock_times, 1)
    for residual_iter, res_threshold in enumerate(residual_thresholds_):
        residuals = [abs(ct - fit[0]*filtered_timestamps[i] - fit[1]) for i, ct in enumerate(clock_times)]
        # plot the way values will be deleted
        if info_level >= 3:
            plt.scatter(filtered_timestamps, clock_times, color="b", label=f"values before filtering", marker="+")
            try:
                rg = range(0, len(filtered_timestamps), len(filtered_timestamps)//10)
            except ValueError:
                rg = range(0, len(filtered_timestamps))
            plt.xticks([filtered_timestamps[i] for i in rg], [i for i in rg])
            plt.plot(filtered_timestamps, [fit[0]*ts + fit[1] for ts in filtered_timestamps],
                     label=f"fitting (before filtering)", color="y")
            plt.axline((0, fit[1] - res_threshold), slope=fit[0], label=f"'lowest' filter", color="r")
            plt.axline((0, fit[1] + res_threshold), slope=fit[0], label=f"'highest' filter", color="r")
            plt.legend()
            plt.xlim(min(filtered_timestamps) * 0.9, max(filtered_timestamps) * 1.1)
            plt.ylim(fit[0] * min(filtered_timestamps) + fit[1] * 0.9,
                     fit[0] * max(filtered_timestamps) + fit[1] * 1.1)
            plt.title(f"filtering of clock times (residual, with threshold {res_threshold} on iter {residual_iter+1})")
            plt.xlabel("index of the frames")
            plt.ylabel("read clock times")
            plt.show()
        # cleanup the values and fit with the cleaner set
        mask = [False if residuals[i] < res_threshold else True for i, ct in enumerate(clock_times)]
        print(f"[step3][w] {cleanup_values(mask)} values were discarded on iter {residual_iter+1} "
              f"with threshold {res_threshold}")
        print(f"[step3][w] there is {len(filtered_timestamps)} values left")
        fit = np.polyfit(filtered_timestamps, clock_times, 1)

    # get a list of all possible timestamps from a folder containing video frames
    all_timestamps = list(sorted(
        [float(k.replace(".jpg", "").replace("_", ".")) for k in os.listdir(video_path_) if k.endswith(".jpg")]
    ))

    results = {
        COMPUTED_CLOCK_TIMES: [fit[0]*ts + fit[1] for ts in all_timestamps],
        TIMESTAMPS: all_timestamps,
    }

    # plot the last fitting (the one that will be saved)
    if info_level >= 2:
        plt.scatter(filtered_timestamps, clock_times, label=f"values (filtered)", color="b")
        plt.plot(all_timestamps, results[COMPUTED_CLOCK_TIMES], label="fitting (last)", color="y")
        plt.xlim(min(all_timestamps) * 0.9, max(all_timestamps) * 1.1)
        plt.ylim(fit[0] * min(all_timestamps) + fit[1] * 0.9,
                 fit[0] * max(all_timestamps) + fit[1] * 1.1)
        plt.title("fitting for clock time, saved fit")
        plt.xlabel("timestamps of the frames")
        plt.ylabel("read clock times")
        plt.legend()
        plt.show()

    # plot the residual error
    if info_level >= 3:
        residuals = [abs(ct - (fit[0]*filtered_timestamps[i] + fit[1])) for i, ct in enumerate(clock_times)]
        plt.plot(filtered_timestamps, residuals, label=f"residuals", color="b")
        plt.xlim(min(all_timestamps) * 0.9, max(all_timestamps) * 1.1)
        plt.ylim(0, max(residuals) * 1.1)
        plt.title("residual error on filtered timestamps")
        plt.xlabel("timestamps of the frames")
        plt.ylabel("residual error")
        plt.legend()
        plt.show()

    # info on the series
    if info_level >= 1:
        frequencies = 1/(np.diff([fit[0]*ts + fit[1] for ts in timestamps])/1000)
        print(f"[step3][r] average sampling frequency : {np.mean(frequencies)} Hz with sigma {np.std(frequencies)} Hz")
        print(f"[step3][i] {100 * len(clock_times) / number_of_frames} % of the frames with OCR results"
              f" where deemed appropriate for fitting")
        print(f"[step3][i] {100 * len(clock_times) / len(all_timestamps)} % of the total of frames"
              f" where deemed appropriate for fitting")

    # save / replace the results
    if os.path.isfile(video_path_ + clock_fitting_results_filename):
        print(f"[step3][w] file {clock_fitting_results_filename} already exists, it will be removed and replaced")
        os.remove(video_path_ + clock_fitting_results_filename)
    with open(video_path_ + clock_fitting_results_filename, "wb") as f:
        pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)

    return True


if __name__=="__main__":

    # init
    clock_times = []
    filtered_timestamps = []

    # user-adjustable values
    plot = 2  # sets the quantity of intermediate plots that will be shown (0 is lesser)
    interval_to_analyze = (0, None)  # frames
    residual_thresholds = (500, 100, 50)

    # setting the folder to process
    print("[step3][c] choose a folder containing the raw ocr data")
    video_path = askdirectory()
    if video_path == "":
        raise ValueError("no folder selected")

    step3(video_path, plot, interval_to_analyze, residual_thresholds)
