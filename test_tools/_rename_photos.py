"""
@author: Tristan Chevreau

This code renames photos from a folder to an integer, 0 being the oldest file.
"""

import os
import shutil
from PIL import Image


if __name__=="__main__":

    # Specify the folder path where your images are located
    folder_path = input("path ? ")

    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter the list to include only image files (you can modify the condition as needed)
    image_files = [file for file in files if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    # Create a list to store the file paths and corresponding EXIF dates
    file_exif_dates = []

    # Iterate over the image files and extract the EXIF dates
    for image_file in image_files:
        file_path = os.path.join(folder_path, image_file)
        try:
            with Image.open(file_path) as image:
                exif_info = image._getexif()  # Get the EXIF data
                exif_date = exif_info.get(36867)  # EXIF tag for DateTimeOriginal (change it if needed)
                if exif_date:
                    file_exif_dates.append((file_path, exif_date))
        except (IOError, OSError, AttributeError, KeyError):
            # Handle exceptions that may occur while processing the files
            pass

    # Sort the list based on the EXIF dates (oldest first)
    file_exif_dates.sort(key=lambda x: x[1])

    # Rename the files in the desired order
    for i, (file_path, _) in enumerate(file_exif_dates):
        file_name, file_ext = os.path.splitext(file_path)
        new_file_name = f"{i+1:05d}{file_ext}"  # Renaming format: 0001.jpg, 0002.jpg, etc.
        new_file_path = os.path.join(folder_path, new_file_name)
        shutil.move(file_path, new_file_path)  # Move the file with the new name

