"""
@author: Tristan Chevreau

A tool to verify if the frame coupler worked well.

Input :
- a folder path to coupled frames (which resulted from the execution of step4)

Output :
- only visual : seeing the coupled frames together
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk

class Interface:

    def __init__(self, folder_paths, canvas_size = (200, 150)):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.__close_window)
        self.displayed_image = [None for _ in range(len(folder_paths))]
        self.frame_nr = 1
        # video visualization
        self.canvas = []
        self.all_image_files = [[] for _ in range(len(folder_paths))]
        for i, folder_path in enumerate(folder_paths):
            self.canvas.append(tk.Canvas(self.root, width=canvas_size[0], height=canvas_size[1], bg="gray"))
            self.canvas[i].pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
            self.canvas[i].bind('<Configure>', self.__canvas_resized)
            for file_ in os.listdir(folder_path):
                if file_.endswith(".jpg"):
                    self.all_image_files[i].append(Image.open(folder_path + "/" + file_))
        assert all(len(self.all_image_files[i]) == len(self.all_image_files[i+1])
                   for i in range(len(self.all_image_files)-1))
        self.parameters_frame = ttk.Frame(self.root)
        ttk.Button(self.parameters_frame, text="play", command=self.__disp_frames).pack(
            fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.__stop = False
        ttk.Button(self.parameters_frame, text="stop", command=self.__stopf).pack(
            fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.parameters_frame.pack(side=tk.RIGHT)

    def __stopf(self):
        self.__stop = True

    def mainloop(self):
        self.root.mainloop()
        return True

    def __canvas_resized(self, *_):
        self.__display_video_frame()

    def __display_video_frame(self):
        for i in range(len(self.all_image_files)):
            displayed_image = self.all_image_files[i][self.frame_nr]
            self.displayed_image[i] = displayed_image.copy()
            self.displayed_image[i].thumbnail((self.canvas[i].winfo_width(), self.canvas[i].winfo_height()))
            self.displayed_image[i] = ImageTk.PhotoImage(self.displayed_image[i])
            self.canvas[i].delete("all")
            self.canvas[i].create_image(0, 0, anchor=tk.NW, image=self.displayed_image[i])
        self.root.update()

    def __disp_frames(self):
        self.__stop = False
        while not self.__stop:
            self.frame_nr += 1
            if self.frame_nr >= len(self.all_image_files[0]):
                self.frame_nr = 0
            self.__display_video_frame()
            if self.__stop:
                break

    def __close_window(self):
        self.root.destroy()
        quit()

if __name__=="__main__":
    path = askdirectory()
    if path != "":
        interface = Interface([path + "/" + e for e in os.listdir(path) if e[0:2] != "__"])
        interface.mainloop()
