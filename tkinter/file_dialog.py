
from tkinter import *
from tkinter import filedialog
import os

# Open Files Dialog Box - Python Tkinter GUI Tutorial #15: https://www.youtube.com/watch?v=Aim_7fC-inw

# Set file location or refer dialog to program location using my_dir
my_file_path = ''
my_directory = os.path.dirname(os.path.realpath(__file__))

# Set path var below to either one of two options above
path = my_directory

root = Tk()
root.title('File Dialog')
# Hide root
root.overrideredirect(True)

# Return Name and Location of File, use this format to show multiple filetypes: --> ('png files', '*.png'),('all files', '*.*')
root.filename = filedialog.askopenfilename(initialdir=path, title='Select A File')

root.mainloop()