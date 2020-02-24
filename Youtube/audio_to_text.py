
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import os
import datetime
import time


##############################
# Timestamp VARS
now_date = datetime.date.today().strftime('%d%b%y').upper()
now_hour = str(time.localtime().tm_hour)
now_min = str(time.localtime().tm_min)

##############################
# my_filename file must be an MP3 file for conversion to .wav, or if you already have a .wav you should be fine
my_filename = '****************************************'
my_dir = os.path.dirname(os.path.realpath(__file__))

# ffmpeg must be properly installed on OS, worked well with "brew install"
AudioSegment.converter = '/****************************************/bin/ffmpeg'


def audio_to_text():
        if path.exists(f'{my_filename}.wav'):
                print('.wav detected, generating transcript...')
                # use the audio file as the audio source
                save_transcript()
        else:
                print('no .wav detected, converting mp3 and generating transcript...')
                # convert mp3 file to wav
                sound = AudioSegment.from_mp3(f'{my_dir}/{my_filename}.mp3')
                print('Converting to .wav, standby...')
                sound.export(f'{my_filename}.wav', format='wav')
                print('A .wav file has been created. ')
                save_transcript()


def save_transcript():
        # transcribe audio file
        AUDIO_FILE = f'{my_filename}.wav'
        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source, duration=300)  # read the entire audio file
        with open(f'{my_filename}_transcript.txt', 'w') as f:
                # write line to output file
                timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
                f.write(f'File Creation Date (Local Time): {timestamp}')
                f.write("\n")
                f.write(f'Filename: {my_filename}')
                f.write("\n")
                f.write(f'Transcription: {r.recognize_google(audio)}')
        print(f'The transcript was saved at {my_dir}/{my_filename}.txt')


audio_to_text()




