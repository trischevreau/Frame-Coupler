"""
@author: Tristan Chevreau

Uses the fitting and timestamps to find common images from a set of videos

Input :
- multiple paths to folders containing the results of step3 and step1

Output :
- the coupled images in a folder
"""

import os
import csv
import pickle
from math import inf
import shutil
from tkinter.filedialog import askdirectory

import numpy as np
import matplotlib.pyplot as plt

from data.constants import *


def get_common_times(computed_times_, threshold_, min_common_time, max_common_time):
    """
    This function returns the common time indexes between a list of times using a threshold.
    :param max_common_time: last common time of the videos
    :param min_common_time: first common time of the videos
    :param computed_times_: a list of lists of time (increasing order)
    :param threshold_: the threshold
    :return: a list of lists of indexes corresponding to common times
    """

    # initialize variables
    n_videos_ = len(computed_times_)
    time_indexes = [0 for _ in range(n_videos_)]
    correct_indexes = []
    common_time = min_common_time

    # ignore all times that are not common to everyone
    for i in range(n_videos_):
        while computed_times_[i][time_indexes[i]] < min_common_time:
            time_indexes[i] += 1

    # loop until we have reached the end of the common time frame
    while common_time <= max_common_time:

        # verify if the frame is common to all videos
        frame_is_correct = True
        for video_i in range(n_videos_):
            t1 = computed_times_[video_i][time_indexes[video_i]]
            for video_ii in range(n_videos_):
                if not video_ii == video_i:
                    t2 = computed_times_[video_ii][time_indexes[video_ii]]
                    if abs(t1 - t2) > threshold_:
                        frame_is_correct = False
                        break
            if not frame_is_correct:
                break

        # save the common frame
        if frame_is_correct:
            correct_indexes.append([time_indexes[video_i] for video_i in range(n_videos_)])

        # increase time
        try:
            distances_to_next_time = [computed_times_[i][time_indexes[i] + 1] - common_time for i in range(n_videos_)]
            distances_to_next_time = [e if e != 0 else inf for e in distances_to_next_time]
        except IndexError:  # we went higher than the common time (security in addition to max_common_time)
            break
        min_indices = [index for index, v in enumerate(distances_to_next_time) if v == min(distances_to_next_time)]
        if len(min_indices) != 1:  # in the rare case that two distances are the same (not coded yet)
            raise ValueError("multiple same distance minimum times. not coded.")
        assert all(e > 0 for e in distances_to_next_time)  # if this fails, the computed times are not always increasing
        common_time = computed_times_[min_indices[0]][time_indexes[min_indices[0]] + 1]
        time_indexes[min_indices[0]] += 1

    return correct_indexes


def step4(video_paths_, results_save_path_=None, save_=True, info_level_=2):
    """ This function contains all the things to execute during step4.
    :param video_paths_: paths to the folders containing the videos
    :param results_save_path_: path where to save the results
    :param save_: whether the correct frames should be saved or not
    :param info_level_: sets the quantity of intermediate plots and info that will be shown (0 is lesser)
    :return: True when the step is successful
    """

    n_videos_ = len(video_paths_)

    # verify the params
    if results_save_path_ is None and save_ == True:
        raise ValueError("no save path selected")

    # load the results from step3
    timestamps = []
    computed_times = []
    for video_path in video_paths_:
        with open(video_path + clock_fitting_results_filename, "rb") as f:
            results = pickle.load(f)
        timestamps.append(results[TIMESTAMPS])
        computed_times.append(results[COMPUTED_CLOCK_TIMES])
    print("[step4][i] clock fitting results loaded")

    # compute the common timeframe
    max_common_time = min([max(computed_time) for computed_time in computed_times])
    min_common_time = max([min(computed_time) for computed_time in computed_times])
    if max_common_time - min_common_time <= 0:
        raise ValueError("no common timeframe between the files")
    print(f"[step4][i] there is {max_common_time - min_common_time} ms in common starting from {min_common_time} ms")

    # plot the common timeframe
    if info_level_ >= 2:
        for video_i in range(n_videos_):
            plt.scatter(timestamps[video_i], computed_times[video_i])
        plt.axline((0, max_common_time), slope=0, label="max common time", color="red")
        plt.axline((0, min_common_time), slope=0, label="min common time", color="red")
        plt.xlabel("arbitrary relative time indicator (timestamps)")
        plt.ylabel("measured and fitted clock time (ms)")
        plt.title("common timeframes calculator")
        plt.legend()
        plt.xlim(min([min(timestamp) for timestamp in timestamps]) * 0.9,
                 max([max(timestamp) for timestamp in timestamps]) * 1.1)
        plt.ylim(min([min(computed_time) for computed_time in computed_times]) * 0.9,
                 max([max(computed_time) for computed_time in computed_times]) * 1.1)
        plt.show()

    # plot coupling quality vs coupling quantity
    if info_level_ >= 2:
        res = []
        space = np.geomspace(0.01, 10000, 100)
        for i_threshold, threshold in enumerate(space):
            n_correct = len(get_common_times(computed_times, threshold, min_common_time, max_common_time))
            res.append((n_correct, [100 * n_correct / len(timestamps[i]) for i in range(n_videos_)]))
            print(f"[step4][i][{i_threshold + 1}/{space.size}] with threshold {threshold}, "
                  f"found {n_correct} common frames")
        for i in range(n_videos_):
            plt.semilogx(space, [res[ii][1][i] for ii in range(len(res))], label=f"video {i + 1}")
        plt.title("% of kept frames depending on threshold")
        plt.ylabel("% of kept frames")
        plt.xlabel("threshold")
        plt.legend()
        plt.show()

    # choose a threshold
    try:
        print()
        chosen_threshold = float(input("[step4][c] choose a threshold for the frame coupling (ms) : "))
        print()
        assert chosen_threshold >= 0
    except ValueError:
        raise ValueError("you did not enter a valid floating-point value")
    except AssertionError:
        raise ValueError("the threshold should be a strictly positive floating point number")

    # init variables
    average_times = []
    real_times = [[] for _ in range(n_videos_)]
    correct_indexes = get_common_times(computed_times, chosen_threshold, min_common_time, max_common_time)

    # create saving folders
    if save_:
        for i in range(n_videos_):
            try:
                os.mkdir(results_save_path_ + "/" + str(i + 1))
            except FileExistsError:
                pass
        print(f"[step4][i] created saving folders")

    # load the filenames (reverse dict of the timestamps from step1)
    loaded_filenames = {}
    for video_path_ in video_paths_:
        with open(video_path_ + timestamps_filename, "rb") as f:
            res = pickle.load(f)
            loaded_filenames[video_path_] = {v: k for k, v in res.items()}  # reverse dict
        if info_level >= 1:
            print(f"[step3][i] filenames loaded from {video_path_} (reversed timestamps)")

    # iterate through the correct indexes
    n_found = len(correct_indexes)
    for i_found, coupled_frames_index in enumerate(correct_indexes):
        average_times.append(np.mean([[computed_times[i][coupled_frames_index[i]] for i in range(n_videos_)]]))
        for i in range(n_videos_):
            real_times[i].append(computed_times[i][coupled_frames_index[i]])
        if save_:
            if info_level_ >= 1:
                print(f"[step4][i][{i_found + 1}/{n_found}] saving frame at t = {average_times[-1]} ms")
                for i in range(n_videos_):
                    ts = timestamps[i][coupled_frames_index[i]]
                    shutil.copyfile(
                        video_paths_[i] + f"/{loaded_filenames[video_paths_[i]][ts]}",
                        f"{results_save_path_}/{i + 1}_{str(len(average_times)).zfill(8)}.jpg"
                    )

    # info on the found series
    print(f"[step4][i] with threshold {chosen_threshold}, found {n_found} common frames")
    print(f"[step4][i] this represents :")
    for i in range(n_videos_):
        print(f"[step4][i] {100 * len(average_times) / len(timestamps[i])} % of the frames from video {i + 1}")

    # plot the timeline of kept frames and the variance for each coupling
    if info_level_ >= 2:
        plt.title("kept frames and variance of the coupling")
        err = [np.var([real_times[i][ii] for i in range(n_videos_)]) for ii in range(len(average_times))]
        plt.errorbar(average_times, [0 for _ in average_times], yerr=err, fmt='+', ecolor='g')
        plt.xlabel("average time of the couples (ms)")
        plt.ylabel("variance of the coupling (ms)")
        plt.show()

    # save the timestamps of the coupled frames
    if save_:
        with open(f"{results_save_path_}/__times.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["image_index", "average_time"] + [f"video_{i}_time" for i in range(n_videos_)])
            for i in range(len(average_times)):
                writer.writerow([i, average_times[i]] + [real_times[ii][i] for ii in range(n_videos_)])
        print("[step4][i] finished saving times")

    return True


if __name__=="__main__":

    info_level = 2
    save = True

    # choose the paths of the folders containing the frames to couple
    try:
        n_videos = int(input("[step4][c] how many frame folders to couple ? "))
        assert n_videos >= 2
    except ValueError:
        raise ValueError("you did not enter a valid number of videos")
    except AssertionError:
        raise ValueError("the number of videos should be an integer greater than 1")

    if save:
        print("[step4][c] choose the results saving path")
        results_save_path = askdirectory()
        if results_save_path == "":
            raise ValueError("you did not select a results folder")
    else:
        results_save_path = None

    print("[step4][c] choose the folder frames paths")
    video_paths = [askdirectory() for _ in range(n_videos)]
    if "" in video_paths:
        raise ValueError("you did not select all the folders")

    step4(video_paths, results_save_path, save, info_level)
