"""
@author: Tristan Chevreau

This program moves and renames images located in subdirectories within a root folder.
It assumes that the images are organized in the following structure:
- root_folder
  - folder_1
    - 00001.png
    - 00002.png
    - ...
  - folder_2
    - 00001.png
    - 00002.png
    - ...

The program iterates through each subdirectory in the root folder, retrieves the image files, and renames them based on
their parent folder. The renamed images are then moved to the root folder with the format:
- root_folder
    - 00001_folder1.png
    - 00002_folder1.png
    - ....._folder1.png
    - 00001_folder2.png
    - 00002_folder2.png
    - ....._folder2.png

Note: Make sure you have the necessary permissions to move and rename the files in the specified folders.
"""

import os
import shutil

def move_and_rename_images(root_folder_):
    for folder_name in os.listdir(root_folder_):
        folder_path = os.path.join(root_folder_, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    extension = os.path.splitext(file_name)[1]
                    new_file_name = ".".join(file_name.split(".")[:-1]) + "_" + folder_name + extension
                    new_file_path = os.path.join(root_folder_, new_file_name)
                    shutil.copy(file_path, new_file_path)


root_folder = input("select a folder to flatten : ")
move_and_rename_images(root_folder)
print("ok")
