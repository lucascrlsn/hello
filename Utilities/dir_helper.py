import os
import pprint as pp
import datetime
import time


def show_dir_contents():
    # Location of this file
    my_dir = os.path.dirname(os.path.realpath(__file__))
    # Location of files of interest
    my_files = f'{my_dir}/*******************************************/'
    # All files in my_dir w/ full path
    files = [os.path.join(r, file) for r, d, f in os.walk(my_files) for file in f]
    # Number of files
    pp.pprint(len(files))
    # List of Files
    # pp.pprint(files)


def change_filename():
    # Requires os and datetime mods
    # Loops through directory to change all file names based on creation date and time
    time.sleep(10)
    target = '/*******************************************'
    prefix = 'someprefix_'
    os.chdir(target)
    allfiles = os.listdir(target)
    for filename in os.listdir(target):
        os.rename(filename, datetime.datetime.fromtimestamp(
                             os.path.getmtime(filename)).strftime(
                              '{0}%Y%m%d %I:%M %p.jpeg'.format(prefix)))


show_dir_contents()
