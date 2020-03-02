from pydub import AudioSegment
import os
import speech_recognition as sr
import datetime
import time

##############################
# Timestamp VARS
now_date = datetime.date.today().strftime('%d%b%y').upper()
now_hour = str(time.localtime().tm_hour)
now_min = str(time.localtime().tm_min)

##############################
# Initial Config Vars
my_filename = '**********************************'
my_dir = os.path.dirname(os.path.realpath(__file__))
my_file = f'{my_dir}/{my_filename}.wav'
sound = AudioSegment.from_mp3(f'{my_dir}/{my_filename}.wav')

####################
# ffmpeg must be properly installed on OS, worked well with "brew install"
AudioSegment.converter = '**********************************/ffmpeg'

# Input audio file to be sliced
audio = AudioSegment.from_wav(f'{my_filename}.wav')

''' 
Step #1 - Slicing the audio file into smaller chunks. 
'''

# Length of the audio file in milliseconds
n = len(audio)

# Variable to count the number of sliced chunks
counter = 1

# Text file to write the recognized audio
fh = open(f'{my_filename}_transcript.txt', 'w+')

# Interval length at which to slice the audio file.
# If length is 22 seconds, and interval is 5 seconds,
# The chunks created will be:
# chunk1 : 0 - 5 seconds
# chunk2 : 5 - 10 seconds
# chunk3 : 10 - 15 seconds
# chunk4 : 15 - 20 seconds
# chunk5 : 20 - 22 seconds
min_interval = 5
interval = (min_interval*60)*1000   # multiply to convert to milliseconds

number_of_chunks = round((n/interval), 0)
timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
print(f'{timestamp} | Splitting your audio into {number_of_chunks} {min_interval}-minute '
      f'files to convert from voice to text')

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
    filename = f'{my_filename}_chunk_' + str(counter) + '.wav'
    # Store the sliced audio file to the defined path
    chunk.export(filename, format="wav")
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
    AUDIO_FILE = filename
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
        fh.write(f'Transcript #{counter-1}')
        fh.write('\n')
        fh.write(rec + ' ')
    # If google could not understand the audio
    except sr.UnknownValueError:
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(f'{timestamp} | Could not understand audio')
        counter = counter - 1
    # If the results cannot be requested from Google.
    # Probably an internet connection error.
    except sr.RequestError as e:
        timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        print(f'{timestamp} | Could not request results.')
        counter = counter - 1
    # Check for flag.
    # If flag is 1, end of the whole audio reached.
    # Close the file and break.
    if flag == 1:
        print(f'{timestamp} | Processing Complete!')
        fh.close()
        break

