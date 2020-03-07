##############################
# UI MODs
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import datetime
import time
import moviepy.editor as mp
import os.path
from os import path

##############################
# Audio to Text MODs
from pydub import AudioSegment
import speech_recognition as sr

##############################
# Youtube JSON MODs
import json
import re
import urllib
import urllib.request
from urllib.request import urlopen
from pytube import YouTube
import pprint as pp

##############################
# For Converting GUI Media to Tkinter-compatible image objects
# https://effbot.org/tkinterbook/photoimage.htm
from PIL import Image, ImageTk

##############################
# For Tooltips
import webbrowser

##############################
# For logging version checking, TBD
version = 1


def is_internet():
    """
    Query internet using python, exception prevents user from accessing tool without internet connection.
    :return:
    """
    try:
        urlopen('https://www.google.com', timeout=1)
        return True
    except:
        win = Tk()
        win.geometry('1400x25')
        win.config(bg='red')
        tkinter.messagebox.showinfo(title='Design Error', message='Ths tool requires an active internet connection. '
                                                                  'Please reconnect and try again. Thanks!')
        exit()


is_internet()

win = Tk()
win.title("Youtube Handler")
# Makes GUI non-resizable
# win.resizable(0, 0)
menu = Menu(win)
win.config(menu=menu, bg='#384048', padx=7, pady=7)

##############################
# Tray/Program Icon
icon_image = Image.open('/****************************************************/youtube_ico.png')
photo = ImageTk.PhotoImage(icon_image)
win.iconphoto(False, photo)

##############################
# Timestamp VARS
now_date = datetime.date.today().strftime('%d%b%y').upper()
now_hour = str(time.localtime().tm_hour)
now_min = str(time.localtime().tm_min)

##############################
# Placeholders for Global Edits | Common VARs
video_id = None
title = ''
description = ''
user_input = ''
my_dir = os.path.dirname(os.path.realpath(__file__))

# '''If user chooses generate transcript from Youtube we must alter functions to rely on Helper Class.
# CONNECT = Generate Transcript
# DISCONNECT = Singular actiins such as generate audio or generate description .txt'''
# action_type = ''

# Tool Tip Screen share Location
help_url = 'https://drive.google.com/file/d/1JqbJgrxMqlw6Xgw6oFeT1J0SDvZpWa6t/view'


##############################


def youtube_help(x):
    webbrowser.open(x, new=1)


def display_user_choice(event):
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    selection = user_option_dropdown.get()
    system_log = f'{timestamp} | {selection} has been chosen, click \'SUBMIT\' to complete your action'
    # status_bar.delete(0, END)
    # status_bar.insert(10, system_log)


def user_action(self):
    global title
    selection = user_option_dropdown.get()
    # Get user Link
    s = user_input.get()
    helper = Helper()
    video_id = helper.id_from_url(str(s))
    api_key = '****************************************************'
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'
    yt_stats = YouTubeStats(url)
    title = yt_stats.get_video_title()
    title = helper.title_to_underscore_title(title)
    description = yt_stats.get_video_description()

    if selection == 'Download Video':
        if path.exists(f'{my_dir}/{title}.mp4'):
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            system_log = f'{timestamp} | Video detected, no download required'
            print(system_log)
            # status_bar.delete(0, END)
            # status_bar.insert(10, system_log)

        else:
            download_vid()

    elif selection == 'Convert Audio':
        # action_type = 'DISCONNECT'
        convert_to_mp3()

    elif selection == 'Generate Metrics File':
        # action_type = 'DISCONNECT'
        generate_metrics_report()

    elif selection == 'Generate Transcript':
        # action_type = 'DISCONNECT'
        if path.exists(f'{title}_transcript.txt'):
            pass
            # timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            # system_log = f'{timestamp} | Transcript Detected, there is no write required'
            # print(system_log)
            # status_bar.delete(0, END)
            # status_bar.insert(10, system_log)

        else:
            if path.exists(f'{title}.mp3'):
                generate_transcript()
            else:
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                print(f'{timestamp} | No .mp3 for {title} detected. Please convert your mp4 to audio first')

    elif selection == 'Generate Transcript from Youtube':
        # action_type == 'CONNECT'
        start = time.perf_counter()
        download_vid()
        convert_to_mp3()
        generate_metrics_report()
        generate_transcript()
        finish = time.perf_counter()
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(f'{timestamp} | Processing Complete! Finished in {round(finish - start / 60, 0)} minutes')

    else:
        print('Fail')


class Helper:
    # strips video ID from url with REGEX
    def __init__(self):
        pass

    def title_to_underscore_title(self, title: str):
        title = title.replace('\'', '')
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


# def print_sys_log():
#     # psl_id = str(id(print_sys_log))
#     timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
#     # print(f'{timestamp} | {psl_id} | User Queried Youtube')
#     print(f'{timestamp} | User Queried Youtube')

def download_vid():
    global title
    global description
    selection = user_option_dropdown.get()
    # Get user Link
    s = user_input.get()
    helper = Helper()
    video_id = helper.id_from_url(str(s))
    api_key = 'AIzaSyAxE2KLI-sMV-hG-1e5WVJtdvDPsUmLwY0'
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'
    yt_stats = YouTubeStats(url)
    title = yt_stats.get_video_title()
    title = helper.title_to_underscore_title(title)
    description = yt_stats.get_video_description()
    answer = 'yes'
    # answer = tkinter.messagebox.askquestion('Proceed?',
    #                                         'Are you sure you want to continue with the download? Larger files will take some time to display in your active directory')
    if answer == 'yes':
        start_download = time.perf_counter()
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        system_log = f'{timestamp} | Downloading, please wait...'
        # downloading_notification = tkinter.messagebox.showinfo('Downloading...', 'Downloading, you will be '
        #                                                                          'notified when it is complete. '
        #                                                                          'Closing this dialogue will not '
        #                                                                          'cancel the process.')
        # status_bar.delete(0, END)
        # status_bar.insert(10, system_log)2
        print(system_log)
        yt_stats.download_video(s, title)
        # download_complete = tkinter.messagebox.showinfo('Complete','Your download has finished and is located at: {my_dir}')
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        finish_download = time.perf_counter()
        print(f'{timestamp} | Download complete in {round(finish_download - start_download, 2)} seconds!')
    else:
        system_log = f'{timestamp} | Download canceled'
        # status_bar.delete(0, END)
        # status_bar.insert(10, system_log)
        print(system_log)


def convert_to_mp3():
    # if action_type == 'CONNECT':
    #     title = title
    # else:
    #     title = user_input.get()
    if path.exists(f'{my_dir}/{title}.mp3'):
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        system_log = f'{timestamp} | Audio detected, no conversion is required'
        # status_bar.delete(0, END)
        # status_bar.insert(10, system_log)
        print(system_log)
    else:
        if path.exists(f'{my_dir}/{title}.mp4'):
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            answer = 'yes'
            # answer = tkinter.messagebox.askquestion('Proceed?',
            #                                         'Are you sure you want to continue with the audio conversion? Larger files will take some time to display in your active directory')
            if answer == 'yes':
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                start_conversion = time.perf_counter()
                system_log = f'{timestamp} | Video detected, converting...'
                print(system_log)
                # status_bar.delete(0, END)
                # status_bar.insert(10, system_log)
                clip = mp.VideoFileClip(f'{title}.mp4')
                clip.audio.write_audiofile(f'{title}.mp3')
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                end_conversion = time.perf_counter()
                print(
                    f'{timestamp} | Your video was converted to an mp3 file in {round(end_conversion - start_conversion, 2)} seconds!')
            else:
                system_log = f'{timestamp} | Audio conversion canceled'
                print(system_log)
                # status_bar.delete(0, END)
                # status_bar.insert(10, system_log)

        else:
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            system_log = f'{timestamp} | An MP4 video is required before you can convert to audio.' \
                         f' Change your dropdown to \'Download Video\' and submit that first.'
            print(system_log)
            # status_bar.delete(0, END)
            # status_bar.insert(10, system_log)


def generate_metrics_report():
    if path.exists(f'{my_dir}/{title}_description.txt'):
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        system_log = f'{timestamp} | Description File Detected, there is no write required'
        print(system_log)
        # status_bar.delete(0, END)
        # status_bar.insert(10, system_log)

    else:
        with open(f'{title}_description.txt', 'w') as f:
            # write line to output file
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            f.write(f'File Creation Date (Local Time): {timestamp}')
            f.write("\n")
            f.write(f'Filename: {title}')
            f.write("\n")
            f.write(f'Description: {description}')
            system_log = f'{timestamp} | No metadata file detected. {title}.txt was saved in the active directory'
            print(system_log)
            # status_bar.delete(0, END)
            # status_bar.insert(10, system_log)


def generate_transcript():
    global title
    global my_dir
    # if action_type == 'CONNECT':
    #     title = title
    # else:
    #     title = user_input.get()
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    my_dir = os.path.dirname(os.path.realpath(__file__))
    # Convert to .wave
    print(f'{timestamp} | \'{title}\' detected')
    sound = AudioSegment.from_mp3(f'{title}.mp3')
    print(f'{timestamp} | Converting to .wav, standby...')
    sound.export(f'{title}.wav', format='wav')
    print(f'{timestamp} | A .wav file has been created. ')
    ############################################
    # VARs
    # ffmpeg must be properly installed on OS, worked well with "brew install"
    AudioSegment.converter = '/****************************************************/ffmpeg'

    # Input audio file to be sliced
    audio = AudioSegment.from_wav(f'{my_dir}/{title}.wav')

    # Length of the audio file in milliseconds
    n = len(audio)

    # Variable to count the number of sliced chunks
    counter = 1

    # Text file to write the recognized audio
    fh = open(f'{my_dir}/{title}_transcript.txt', 'w+')

    # Interval length at which to slice the audio file.
    # If length is 22 seconds, and interval is 5 seconds,
    # The chunks created will be:
    # chunk1 : 0 - 5 seconds
    # chunk2 : 5 - 10 seconds
    # chunk3 : 10 - 15 seconds
    # chunk4 : 15 - 20 seconds
    # chunk5 : 20 - 22 seconds
    min_interval = 1
    interval = (min_interval * 60) * 1000  # multiply to convert to milliseconds
    number_of_chunks = round((n / interval), 0) - 1
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(f'{timestamp} | Splitting your audio into {number_of_chunks}, {min_interval}-minute '
          f'files for accurate voice to text conversion')

    # Length of audio to overlap.
    # If length is 22 seconds, and interval is 5 seconds,
    # With overlap as 1.5 seconds,
    # The chunks created will be:
    # chunk1 : 0 - 5 seconds
    # chunk2 : 3.5 - 8.5 seconds
    # chunk3 : 7 - 12 seconds
    # chunk4 : 10.5 - 15.5 seconds
    # chunk5 : 14 - 19.5 seconds
    # chunk6 : 18 - 22 seconds
    overlap = 1.5 * 1000

    # Initialize start and end seconds to 0
    start = 0
    end = 0

    # Flag to keep track of end of file.
    # When audio reaches its end, flag is set to 1 and we break
    flag = 0
    ############################################
    # End VARs
    # Iterate from 0 to end of the file,
    # with increment = interval
    for i in range(0, 2 * n, interval):
        # During first iteration,
        # start is 0, end is the interval
        if i == 0:
            start = 0
            end = interval
        # All other iterations,
        # start is the previous end - overlap
        # end becomes end + interval
        else:
            start = end - overlap
            end = start + interval
        # When end becomes greater than the file length,
        # end is set to the file length
        # flag is set to 1 to indicate break.
        if end >= n:
            end = n
            flag = 1
        # Storing audio file from the defined start to end
        chunk = audio[start:end]
        # Filename / Path to store the sliced audio
        filename = f'{title}_chunk_' + str(counter) + '.wav'
        # Store the sliced audio file to the defined path
        chunk.export(title, format="wav")
        # Get Timestamp
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        # Print information about the current chunk
        print(f'{timestamp} | Processing chunk ' + str(counter) + '. Start = '
              + str(start) + ' end = ' + str(end))
        # Increment counter for the next chunk
        counter = counter + 1
        # Here, Google Speech Recognition is used
        # to take each chunk and recognize the text in it.
        # Specify the audio file to recognize
        AUDIO_FILE = title
        # Initialize the recognizer
        r = sr.Recognizer()
        # Traverse the audio file and listen to the audio
        with sr.AudioFile(AUDIO_FILE) as source:
            audio_recorded = r.record(source)

        # Try to recognize the listened audio
        # And catch expectations.
        try:
            rec = r.recognize_google(audio_recorded)
            # If recognized, write into the file.
            fh.write('\n')
            fh.write('\n')
            fh.write(f'Transcript #{counter - 1}')
            fh.write('\n')
            fh.write(rec + ' ')
        # If google could not understand the audio
        except sr.UnknownValueError:
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            print(f'{timestamp} | Could not understand audio in')
            counter = counter - 1
        # If the results cannot be requested from Google.
        # Probably an internet connection error.
        except sr.RequestError as e:
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            print(f'{timestamp} | Could not request results')
            counter = counter - 1
        # Check for flag.
        # If flag is 1, end of the whole audio reached.
        # Close the file and break.
        if flag == 1:
            fh.close()
            timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
            print(f'{timestamp} | The audio transcript was saved at {my_dir}/{title}_transcript.txt')
            break


def display_results():
    pp.pprint(data)


def doNothing():
    print('Okay, okay, I won\'t...')


def display_user_choice(event):
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    selection = user_option_dropdown.get()
    system_log = f'{timestamp} | {selection} has been chosen, click \'SUBMIT\' to complete your action'
    print(system_log)


def link_help_prompt():
    prompt = tkinter.messagebox.askquestion('Where do I get the link?', 'The link entry box in this tool is '
                                                                        'where you paste the link of the Youtube '
                                                                        'video you are interested in. To get the '
                                                                        'correct link go to the video of interest, '
                                                                        'click share, and copy the link displayed. '
                                                                        'Make sure you do not use the URL at the very '
                                                                        'top of your browser. Want more help?')
    if prompt == 'yes':
        youtube_help(help_url)
    else:
        pass


def show_instructions():
    instructions = tkinter.messagebox.showinfo('General Instructions', '''This tool can download MP4\'s from Youtube, convert them to MP3 files, and also download a text document showing pertinent information about your video.

Downloading Videos: Go to your Youtube Video and Click \'Share\'. You must be logged in. Then copy the link.

Converting to MP3: Currently, this tool only converts the file that was recently downloaded from Youtube. The tool converts by the EXACT filename previously created

Generate Metrics File: This will download a .txt file of your file name, it's description as posted on Youtube. More functionality will be added later on.

Generate Transcript: IN DEVELOPMENT

** FINAL THOUGHTS: Currently, this program starts with the download, converts it to MP3, and then generates a txt if needed. If you find any errors please start from the beginning.''')


################################################
# Menu Drop down 1 "File"
subMenu = Menu(menu)
menu.add_cascade(label='File', menu=subMenu)
subMenu.add_command(label='Close', command=win.quit)

helpMenu = Menu(menu)
menu.add_cascade(label='Instructions', menu=helpMenu)
helpMenu.add_command(label='General Instructions', command=show_instructions)
menu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='Where do I get the link?', command=link_help_prompt)

################################################
submitButt = Button(win, text='Submit', highlightbackground='#708090')
submitButt.bind('<Button-1>', user_action)
submitButt.grid(row=0, column=15)

# ComboBox Style
ttk_style = ttk.Style()

ttk_style.theme_create('combostyle', parent='alt',
                       settings={'TCombobox':
                                     {'configure':
                                          {'selectbackground': '#708090',
                                           'fieldbackground': '#708090',
                                           'background': '#708090',
                                           'relief': 'RAISED',
                                           }}}
                       )
# ATTENTION: this applies the new style 'combostyle' to all ttk.Combobox
ttk_style.theme_use('combostyle')

# Combobox
user_option_dropdown = ttk.Combobox(win, width='15', values=['--CHOOSE ACTION--',
                                                             'Download Video',
                                                             'Convert Audio',
                                                             'Generate Metrics File',
                                                             'Generate Transcript',
                                                             'Generate Transcript from Youtube'
                                                             ])
user_option_dropdown.current(0)
user_option_dropdown.grid(row=0, column=13)
user_option_dropdown.bind('<<ComboboxSelected>>', display_user_choice)
closeButt = Button(win, text='X', fg='black', highlightbackground='red', command=win.destroy)
closeButt.grid(row=0, column=16, sticky=W)

# Progress Bar Style
ttk_style = ttk.Style()

ttk_style.theme_create('barstyle', parent='alt',
                       settings={'TProgressbar':
                                     {'configure':
                                          {'thickness': '5',
                                           }}}
                       )
# ATTENTION: this applies the new style 'barstyle' to all ttk.Progressbar
ttk_style.theme_use('barstyle')

# Progress bar
progress = ttk.Progressbar(win, orient=HORIZONTAL, length=100, mode='determinate')
progress.grid(row=1, column=0, columnspan=30, sticky='WE')

################################################

l1 = Label(win, text='Link', bg='#708090', fg='white', font='bold')
l1.grid(row=0, column=0, sticky='WE')

user_input = StringVar()
e1 = Entry(win, textvariable=user_input, width=25, highlightbackground='red', highlightthickness=1)
e1.grid(row=0, column=1, sticky='WE')

win.mainloop()



