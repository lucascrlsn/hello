from gensim.summarization import summarize, keywords
import pprint as pp

# Sources: https://radimrehurek.com/gensim/auto_examples/tutorials/run_summarization.html#sphx-glr-download-auto-examples-tutorials-run-summarization-py

# text=('')

t = open('transcript.txt', 'r')
file = t.read()

source = file

# Keywords
# pp.pprint(keywords(source))

# Summarize | can use  word_count or ratio
pp.pprint(summarize(source, word_count=75))


# pp.pprint(source)
