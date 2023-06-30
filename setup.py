from cx_Freeze import setup, Executable

script = 'main.py'

setup(
    name='Frame-Coupler',
    version='0.1.0',
    description='This little program selects common images from a set of videos, '
                'using the display of a digital clock in the field of view.',
    executables=[Executable(script)],
    options={
        'build_exe': {
            'packages': ['cv2', 'PIL', 'pytesseract', 'matplotlib', 'numpy'],
        },
    },
)