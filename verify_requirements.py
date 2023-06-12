"""
@author: Tristan Chevreau

Tests the requirements for the use of this program.
"""

import os

from run_parameters import pytesseract_exe_file_path

errors = 0

libs = [
    "numpy",
    "matplotlib.pyplot",
    "cv2",
    "PIL",
    "pytesseract",
]

for lib in libs:
    try:
        exec(f"import {lib}")
    except ImportError:
        print(f"Library '{lib}' is missing or not installed correctly")
        errors += 1
    else:
        print(f"Library '{lib}' OK")

if not os.path.isfile(pytesseract_exe_file_path):
    print(f"The Tesseract-OCR executable path may be incorrect : {pytesseract_exe_file_path}. \n"
          f"Please change it in the run_parameters.")
    errors += 1
else:
    print("The Tesseract-OCR executable path seems correct.")

print()
if errors == 0:
    print("SUCCESS. The requirements are met !")
else:
    print(f"FAIL. {errors} error(s) occurred during requirements testing.")
