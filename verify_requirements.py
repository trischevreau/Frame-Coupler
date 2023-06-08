"""
@author: Tristan Chevreau

Tests the requirements for the use of this program.
"""

libs = [
    "os",
    "pickle",
    "math",
    "tkinter",
    "tkinter.filedialog",
    "csv",
    "shutil",
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
        print(f"library '{lib}' is missing or not installed correctly")
    else:
        print(f"library '{lib}' OK")
