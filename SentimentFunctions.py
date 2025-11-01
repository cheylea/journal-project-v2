#!/usr/bin/python3
# Set of Python functions for interacting with the journal database

### Imports


### Sentiment Functions
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

class SentimentFunctions:

    def get_sentiment(text):
        nltk.download('vader_lexicon')

        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        return scores['compound']  # compound gives overall sentiment