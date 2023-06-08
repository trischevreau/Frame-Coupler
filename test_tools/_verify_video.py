"""
@author: Tristan Chevreau

This displays the difference between timestamps of a video to analyse the consistency of your frame rate.
"""

import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import cv2
import numpy as np

if __name__=="__main__":
    timestamps = []
    file_name = askopenfilename()
    cap = cv2.VideoCapture(file_name)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    count = 0
    while cap.isOpened():
        ret, _ = cap.read()
        if not ret:
            continue
        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        count = count + 1
        print(f"[{count}/{video_length}]")
        if count > (video_length - 1):
            cap.release()
    y = np.diff(timestamps)
    plt.title("difference between consecutive timestamps")
    plt.xlabel("timestamp index (ts[i+1] - ts[i])")
    plt.ylabel("difference (ms)")
    plt.plot(y)
    plt.ylim(0, np.mean(y)*4)
    plt.show()
