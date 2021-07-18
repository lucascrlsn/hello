from gensim.summarization import summarize, keywords
import pprint as pp

"""It is best of have a clean transcript already containing punctuation and accurate grammar."""

"""gensim==3.8.3 is required to summarize per https://discuss.streamlit.io/t/no-module-named-gensim-summarization/11780/8. 
PRI Source: https://radimrehurek.com/gensim/auto_examples/tutorials/run_summarization.html#sphx-glr-download-auto-examples-tutorials-run-summarization-py """

content = ''


def get_summary():
    global content
    t = open(f'{content}.txt', 'r')
    file = t.read()
    source = file
    # Summarize | can use  word_count or ratio
    pp.pprint(summarize(source, word_count=75))


def get_keywords():
    global content
    t = open(f'{content}.txt', 'r')
    file = t.read()
    source = file
    # Print Keywords
    pp.pprint(keywords(source))


# get_keywords()
get_summary()


