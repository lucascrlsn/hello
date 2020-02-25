from collections import Counter
import os
import pprint as pp
import nltk

##################################################
# Stop Word Filtering
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import io
##################################################
my_dir = os.path.dirname(os.path.realpath(__file__))
file = '***********************************************'

text = f'{my_dir}/{file}.txt'


def remove_stop_words():
    # Remove Stop Words | https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
    # word_tokenize accepts a string as an input, not a file
    stop_words = set(stopwords.words('english'))
    file1 = open(f'{file}.txt', 'r+')
    # Use this to read file content as a stream:
    line = file1.read()
    words = line.split()
    for r in words:
        if not r in stop_words:
            appendFile = open('filteredtext.txt', 'a')
            appendFile.write(" "+r)
            appendFile.close()
    f = open('filteredtext.txt', 'r')
    contents = f.read()


def show_nouns():
    f = open(text, 'r')
    contents = f.read()
    tokens = nltk.word_tokenize(contents)
    pos = nltk.pos_tag(tokens)
    selective_pos = ['NNPS', 'NNP']
    selective_pos_words = []
    for word, tag in pos:
        if tag in selective_pos:
            selective_pos_words.append((word))
    print(f'NOUNS: {selective_pos_words}')


def show_verbs():
    f = open(text, 'r')
    contents = f.read()
    tokens = nltk.word_tokenize(contents)
    pos = nltk.pos_tag(tokens)
    selective_pos = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    selective_pos_words = []
    for word, tag in pos:
        if tag in selective_pos:
            selective_pos_words.append((word))
    print(f'VERBS: {selective_pos_words}')




# Functions
# process_transcript()
# remove_stop_words()
show_nouns()
# show_verbs()
