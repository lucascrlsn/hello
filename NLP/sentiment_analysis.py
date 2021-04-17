
# https://www.geeksforgeeks.org/python-sentiment-analysis-using-vader/
# import SentimentIntensityAnalyzer class
# from vaderSentiment.vaderSentiment module. 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sentence = '''This is a test of Vader Sentiment.'''


def sentiment_scores(sentence):
    # function to print sentiments
    # of the sentence.
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer 
    # object gives a sentiment dictionary
    # which contains pos, neg, neu, and compound scores
    sentiment_dict = sid_obj.polarity_scores(sentence)

    # print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", round(sentiment_dict['neg']*100, 2), "% Negative")
    print("sentence was rated as ", round(sentiment_dict['neu']*100, 2), "% Neutral")
    print("sentence was rated as ", round(sentiment_dict['pos']*100, 2), "% Positive")

    print("Sentence Overall Rated As", end=" ")

    # decide sentiment as positive, negative and neutral 
    if sentiment_dict['compound'] >= 0.05:
        print("Positive")

    elif sentiment_dict['compound'] <= - 0.05:
        print("Negative")

    else:
        print("Neutral")


def sentiment():
    if __name__ == "__main__":
        global sentence
        print('\nSentiment Results :')
        sentiment_scores(sentence)


sentiment()