"""
@author: Tristan Chevreau

This is useful to invert suffix and prefixes ("_" separator).
For example, a folder containing :
- pre_01.jpg
- z_03.jpg
- pre_12_RR.jpg
will become :
- 01_pre.jpg
- 03_z.jpg
- RR_12_pre.jpg
"""

import os

folder = input("folder ?")
ext = ".jpg"

for file in os.listdir(folder):
    if file.endswith(ext):
        new_filename = "_".join(list(reversed(file.removesuffix(ext).split("_")))) + ext
        os.rename(os.path.join(folder, file), os.path.join(folder, new_filename))
        print(f"{file} became {new_filename}")
print("Done")
