from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory
import os


def select_batch():
    Tk().withdraw()
    return askopenfilenames()


def select_folder():
    Tk().withdraw()
    directory = askdirectory()
    files = [(directory + "/" + file) for file in os.listdir(directory)]
    return files


def choose_directory():
    Tk().withdraw()
    directory = askdirectory()
    return directory


if __name__ == '__main__':
    print(select_folder())
