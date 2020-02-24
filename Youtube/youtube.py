import json
import re
import urllib.request
from pytube import YouTube
import moviepy.editor as mp
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import pprint as pp
import os.path
from os import path
import datetime
import time
from time import strftime, ctime, gmtime
from tkinter import *
import tkinter.messagebox
from tkinter import ttk


###########################################################################################
#                                   NOTES                                                 #
###########################################################################################
# Concatenated URL VAR Format
# https://www.googleapis.com/youtube/v3/videos?part=snippet&id=iM5kwbF-Mkk&key=
###########################################################################################


window = Tk()
window.title('My Youtube Buddy')
window.config(bg='light grey', highlightcolor='red', highlightthickness=5, highlightbackground='black', relief='sunken',
              borderwidth=5, pady=8)

d = datetime.date.today().strftime("%d%b%y").upper()
timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
video_id = None
title = ''


def display_user_choice(event):
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    selection = user_option_dropdown.get()
    system_log = f'{timestamp} | {selection} has been chosen, click \'SUBMIT\' to complete your action'
    status_bar.delete(0, END)
    status_bar.insert(10, system_log)


def user_action():
    selection = user_option_dropdown.get()

    if selection == 'Download Video':
        if path.exists(f'{title}.mp4'):
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            system_log = f'{timestamp} | Video detected, no download required'
            status_bar.delete(0, END)
            status_bar.insert(10, system_log)

        else:
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            answer = tkinter.messagebox.askquestion('Proceed?', 'Are you sure you want to continue with the download? Larger files will take some time to display in your active directory')
            if answer == 'yes':
                system_log = f'{timestamp} | Downloading, please wait...'
                status_bar.delete(0, END)
                status_bar.insert(10, system_log)
                yt_stats.download_video(s, title)
            else:
                system_log = f'{timestamp} | Download canceled'
                status_bar.delete(0, END)
                status_bar.insert(10, system_log)

    elif selection == 'Convert Audio':
        if path.exists(f'{title}.mp3'):
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            system_log = f'{timestamp} | Audio detected, no conversion is required'
            status_bar.delete(0, END)
            status_bar.insert(10, system_log)

        else:
            if path.exists(f'{title}.mp4'):
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                answer = tkinter.messagebox.askquestion('Proceed?', 'Are you sure you want to continue with the audio conversion? Larger files will take some time to display in your active directory')
                if answer == 'yes':
                    system_log = f'{timestamp} | Video detected, converting...'
                    status_bar.delete(0, END)
                    status_bar.insert(10, system_log)
                    clip = mp.VideoFileClip(f'{title}.mp4')
                    clip.audio.write_audiofile(f'{title}.mp3')
                else:
                    system_log = f'{timestamp} | Audio conversion canceled'
                    status_bar.delete(0, END)
                    status_bar.insert(10, system_log)

            else:
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                system_log = f'{timestamp} | A MP4 video is required before you can convert to audio.' \
                             f'Change your dropdown to \'Download Video\' and submit that first.'
                status_bar.delete(0, END)
                status_bar.insert(10, system_log)

    elif selection == 'Generate Metrics File':
        if path.exists(f'{title}_description.txt'):
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            system_log = f'{timestamp} | Description File Detected, there is no write required'
            status_bar.delete(0, END)
            status_bar.insert(10, system_log)

        else:
            with open(f'{title}_description.txt', 'w') as f:
                # write line to output file
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                f.write(f'File Creation Date (Local Time): {timestamp}')
                f.write("\n")
                f.write(f'Filename: {title}')
                f.write("\n")
                f.write(f'Description: {description}')
                system_log = f'{timestamp} | No metadata file detected. {title}.txt was generated in the active directory'
                status_bar.delete(0, END)
                status_bar.insert(10, system_log)

    else:
        print('Fail')


class Helper:
    # strips video ID from url with REGEX
    def __init__(self):
        pass

    def title_to_underscore_title(self, title: str):
        title = title.replace('\'','')
        title = re.sub('[\W_]+', '_', title)
        return title.lower()

    def id_from_url(self, url: str):
         return url.rsplit('/', 1)[1]


class YouTubeStats:
    def __init__(self, url: str):
         self.json_url = urllib.request.urlopen(url)
         self.data = json.loads(self.json_url.read())

    def print_data(self):
        pp.pprint(self.data)

    def get_video_title(self):
        return self.data["items"][0]["snippet"]["title"]

    def get_video_description(self):
        return self.data["items"][0]["snippet"]["description"]

    def download_video(self, s: str, title: str):
        YouTube(s).streams.first().download(filename=title)

    def download_audio(self, s: str, title: str):
        YouTube(s).streams.first().download(filename=title)


s = 'https://youtu.be/ZkYOvViSx3E'
helper = Helper()
video_id = helper.id_from_url(str(s))
api_key = '*******************************************'
url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'
yt_stats = YouTubeStats(url)
title = yt_stats.get_video_title()
title = helper.title_to_underscore_title(title)
description = yt_stats.get_video_description()

# Label for User
l1 = Label(window, text="Youtube URL")
l1.grid(row=0, column=0, sticky=E)

# Box for Youtube Video URL
user_entry = StringVar()
e1 = ttk.Entry(window, textvariable=user_entry)
e1.grid(row=0, column=1, sticky=W)

# Combobox
user_option_dropdown = ttk.Combobox(window, width='15', values=['--CHOOSE ACTION--', 'Download Video', 'Convert Audio', 'Generate Metrics File', 'Generate Transcript'])
user_option_dropdown.current(0)
user_option_dropdown.grid(row=0, column=2, padx=5)
user_option_dropdown.bind('<<ComboboxSelected>>', display_user_choice)

# Action Button
submit_button = ttk.Button(window, text='SUBMIT', command=user_action)
submit_button.grid(row=0, column=3, padx=5)
# Close Button
close_button = Button(window, text='X', width='1', command=window.destroy)
close_button.grid(row=0, column=4, padx=5)

# Status Scroll Bar
sb = Scrollbar(window, orient=HORIZONTAL)
sb.grid(row=3, column=0, sticky='WE', columnspan='5')

# Status Bar
status = StringVar()
status_bar = Entry(window, textvariable=status, relief=SUNKEN, xscrollcommand=sb.set)
status_bar.grid(row=2, column=0, sticky='WE', columnspan='5')
sb.config(command=status_bar.xview)

window.mainloop()



