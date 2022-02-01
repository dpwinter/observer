"""
Setup Script for compilation/freezing program to executable using cx_freeze.

1. python3 setup.py build (this builds the program into the directory build/ in the working directory)
2. Place compiled program in /snap/observer (the file Observer.desktop on the Desktop looks here for the executable)
"""

from cx_Freeze import setup, Executable

target = Executable(
        script="App.py",
        targetName="Observer"
        )

setup(
        name="Observer",
        version="0.1", 
        description="Program for Interval Measurement", 
        executables = [target]
     )
