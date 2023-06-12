"""
@author: Tristan Chevreau

Uses pytesseract to do the OCR of each images from a folder.
Lets you choose the part of the frames containing the text to recognize.

Input :
- a folder path (the folder must contain jpg grayscales)

Output :
- a file named "__raw_OCR_results" at the root of the folder path, which is the pickle of a dict of this form :
  > {"image_name_1.jpg": "results_of_ocr_from_image_1", "image_name_2.jpg": "results_of_ocr_from_image_2", ...}
"""

import os
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askinteger
import pickle
from math import sqrt
import tkinter as tk

import pytesseract
from PIL import Image, ImageTk

from data.constants import raw_OCR_results_filename
from run_parameters import pytesseract_exe_file_path

# this line should point to your own installation of tesseract-ocr
pytesseract.pytesseract.tesseract_cmd = pytesseract_exe_file_path


class CropBox:
    """
    This class contains an interface to choose cropping points for the frames.
    This is useful to reduce computing time as well as improving the results.
    """

    def __init__(self, image_path, canvas_size = (600, 400)):
        """ The init method.
        :param image_path: the path of the image to display to choose the crop frame
        :param canvas_size: the size of the display canvas
        """
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.__close_window)
        self.root.title("choose a crop frame for the clock display")
        self.displayed_image = None
        self.click_cross_size = 3
        self.displayed_to_original_ratio = None
        self.original_image = Image.open(image_path)
        # video visualization
        self.canvas = tk.Canvas(self.root, width=canvas_size[0], height=canvas_size[1], bg="gray")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.__last_clicks = [(None, None), (None, None)]
        self.canvas.bind("<Button-1>", self.__on_canvas_click)
        self.canvas.bind('<Configure>', self.__canvas_resized)

    def __on_canvas_click(self, event):
        """ The callback function when the canvas is called.
        :param event: the tk event instance
        :return:
        """
        self.__last_clicks.pop(0)
        x, y = event.x, event.y
        self.__last_clicks.append((x, y))
        self.__display()

    def __display_clicks(self):
        """ Displays the clicks on the canvas, as well as a rectangle to show the crop frame.
        :return:
        """
        for click in [c for c in self.__last_clicks if None not in c]:
            x, y = click
            self.canvas.create_line(x - self.click_cross_size, y, x + self.click_cross_size, y, fill="red")
            self.canvas.create_line(x, y - self.click_cross_size, x, y + self.click_cross_size, fill="red")
        if (None, None) not in self.__last_clicks:
            self.canvas.create_rectangle(*self.__last_clicks, outline="blue", width=5)

    def mainloop(self):
        """ The mainloop of the tkinter root. Returns the crop frame in the form of coordinates.
        :return:
        """
        self.root.mainloop()
        clicks = [[int(e * self.displayed_to_original_ratio) for e in ee] for ee in self.__last_clicks]
        # extract the coordinates
        x0, y0 = clicks[0]
        x1, y1 = clicks[1]
        # Ensure x0 is less than x1
        if x0 > x1:
            x0, x1 = x1, x0
        # Ensure y0 is less than y1
        if y0 > y1:
            y0, y1 = y1, y0
        return x0, y0, x1, y1

    def __canvas_resized(self, *_):
        """ This function displays the image back each time the canvas is resized.
        :param _: ignored.
        :return:
        """
        self.__last_clicks = [(None, None), (None, None)]
        self.__display()

    def __display(self):
        """ This function displays everything.
        :return:
        """
        self.displayed_image = self.original_image.copy()
        self.displayed_image.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.displayed_to_original_ratio = self.original_image.width / self.displayed_image.width
        self.displayed_image = ImageTk.PhotoImage(self.displayed_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.displayed_image)
        self.__display_clicks()
        self.canvas.update()

    def __get_real_pixel_distance_between_crosses(self):
        """ Uses the ratio to get the real length in image pixels between crosses.
        :return: the pixel distance for the real image, or None if a click is missing.
        """
        if (None, None) not in self.__last_clicks:
            x1, y1 = self.__last_clicks[0]
            x2, y2 = self.__last_clicks[1]
            false_len = sqrt((x1 - x2)**2 + (y1 - y2)**2)
            return false_len * self.displayed_to_original_ratio
        return None

    def __close_window(self):
        """ Exits the program cleanly.
        :return:
        """
        self.root.destroy()


def step2(video_path_, info_level=2, repeat_frame=1):
    """ This function contains all the things to execute during step2.
    :param info_level: the level of information given to the user
    :param video_path_: the path containing the .jpg images to do the OCR on
    :param repeat_frame: the number of frames between each OCR analysis (1 means every frame, 2 every other frame ...)
    :return: True when the step is successful.
    """

    print(f"[step2][i] beginning OCR of frames from folder {video_path_}")

    all_images_paths = list(sorted(
        [k for k in os.listdir(video_path_) if k.endswith(".jpg")],
        key=lambda k:float(k.replace(".jpg", "").replace("_", "."))
    ))

    # choose a crop box for the OCR (same for all frames)
    print(f"[step2][i] choose a crop frame (see opened window)")
    crop_box_instance = CropBox(video_path_ + "/" + all_images_paths[0])
    crop_frame = crop_box_instance.mainloop()


    # initialize variables
    number_of_frames = len(all_images_paths)
    results = {}
    n_letters = len(str(number_of_frames))

    # do the ocr
    for i, file_ in enumerate(all_images_paths):
        if i % repeat_frame == 0:
            frame = Image.open(video_path_ + "/" + file_)
            frame = frame.crop(crop_frame)
            frame_str = pytesseract.image_to_string(frame, timeout=15,
                                                    config="--psm 7 --oem 3").rstrip().replace('\n', " ")
            if info_level >= 1:
                print(f"[step2][i][{str(i+1).zfill(n_letters)}/{number_of_frames}] found {frame_str} in {file_}")
            results[file_] = frame_str

    # remove the results file, if it already exists
    if os.path.isfile(video_path_ + raw_OCR_results_filename):
        print(f"[step2][w] file {raw_OCR_results_filename} already exists, it will be removed and replaced")
        os.remove(video_path_ + raw_OCR_results_filename)

    # save the results
    with open(video_path_ + raw_OCR_results_filename, "wb") as f:
        pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__=="__main__":

    # setting the folder to process
    print("[step2][c] choose a folder containing the raw ocr data")
    video_path = askdirectory()
    if video_path == "":
        raise ValueError("no folder selected")

    # setting the number of ignored frames
    print("[step2][c] choose between how many frames we should perform OCR \n"
          "(1 means every frame, 2 means every other frame, etc.) ")
    repeat_frame = askinteger("Enter a number",
                              "Between how many frames should we perform OCR ? \n"
                              "(1 means every frame, 2 means every other frame, etc.) ")
    if repeat_frame is None or repeat_frame < 1:
        raise ValueError("you did not enter a correct value")

    step2(video_path, repeat_frame=repeat_frame)
