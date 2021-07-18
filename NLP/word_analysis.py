
##################################################
# Word Analysis
import collections
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
filename = '************************************************************'

text = f'{my_dir}/{filename}.txt'
selective_pos_words = ''


def remove_stop_words():
    # Remove Stop Words | https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
    # word_tokenize accepts a string as an input, not a file
    stop_words = set(stopwords.words('english'))
    file1 = open(f'{text}', 'r+')
    # Use this to read file content as a stream:
    line = file1.read()
    words = line.split()
    for r in words:
        if not r in stop_words:
            appendFile = open('filteredtext.txt', 'a')
            appendFile.write(" "+r)
            appendFile.close()
    # f = open('filteredtext.txt', 'r')
    # contents = f.read()


def dedup():
    global selective_pos_words
    # https://stackoverflow.com/questions/25798674/python-duplicate-words
    word_counts = collections.Counter(selective_pos_words)
    for word, count in sorted(word_counts.items()):
    #     # pp.pprint('"%s" is repeated %d time%s.' % (word, count, "s" if count > 1 else ""))
        pp.pprint(word)


def show_nouns():
    global selective_pos_words
    """Uncomment next two lines if not combining with 'remove_stop_words()'"""
    # f = open(text, 'r')
    # contents = f.read()
    remove_stop_words()
    f = open('filteredtext.txt', 'r')
    contents = f.read()
    tokens = nltk.word_tokenize(contents)
    pos = nltk.pos_tag(tokens)
    selective_pos = ['NNPS', 'NNP']
    selective_pos_words = []
    for word, tag in pos:
        if tag in selective_pos:
            selective_pos_words.append(word)
    # pp.pprint(f'NOUNS: {selective_pos_words}')
    dedup()


def show_verbs():
    remove_stop_words()
    f = open('filteredtext.txt', 'r')
    contents = f.read()
    tokens = nltk.word_tokenize(contents)
    pos = nltk.pos_tag(tokens)
    selective_pos = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    selective_pos_words = []
    for word, tag in pos:
        if tag in selective_pos:
            selective_pos_words.append((word))
    pp.pprint(f'VERBS: {selective_pos_words}')

# ##########################################
# Functions
# remove_stop_words()
# show_nouns()
# show_verbs()
