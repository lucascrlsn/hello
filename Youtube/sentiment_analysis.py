
# https://www.geeksforgeeks.org/python-sentiment-analysis-using-vader/
# import SentimentIntensityAnalyzer class
# from vaderSentiment.vaderSentiment module. 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# function to print sentiments
# of the sentence. 
def sentiment_scores(sentence):
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer 
    # oject gives a sentiment dictionary. 
    # which contains pos, neg, neu, and compound scores. 
    sentiment_dict = sid_obj.polarity_scores(sentence)

    print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", sentiment_dict['neg'] * 100, "% Negative")
    print("sentence was rated as ", sentiment_dict['neu'] * 100, "% Neutral")
    print("sentence was rated as ", sentiment_dict['pos'] * 100, "% Positive")

    print("Sentence Overall Rated As", end=" ")

    # decide sentiment as positive, negative and neutral 
    if sentiment_dict['compound'] >= 0.05:
        print("Positive")

    elif sentiment_dict['compound'] <= - 0.05:
        print("Negative")

    else:
        print("Neutral")

    # Driver code


if __name__ == "__main__":
    print("\n1st statement :")
    sentence = "the Apostle Paul is determined and maybe more than a little angry he's writing the church at thessalonica beautiful city in Macedonia."

    # function calling 
sentiment_scores(sentence)

print("\n2nd Statement :")
sentence = "he loves the people there they are as he says his glory and joy and what annoys the profit but annoys the preacher is that they are under incredible pressure and therefore he decides to write a letter to them to comfort them and to make sure they can withstand the heat that they're going under"
sentiment_scores(sentence)

print("\n3rd Statement :")
sentence = "I am elated, happy, and joyfull."
sentiment_scores(sentence)