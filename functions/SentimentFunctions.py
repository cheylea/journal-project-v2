#!/usr/bin/python3
# Set of Python functions for interacting with the journal database

### Imports


### Sentiment Functions
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

class SentimentFunctions:

    def get_sentiment(text):
        nltk.download('vader_lexicon', quiet=True)
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        compound = scores['compound']
    
        if compound >= 0.5:
            emotion = "Elated"
        elif 0.05 <= compound < 0.5:
            emotion = "Happy"
        elif -0.05 < compound < 0.05:
            emotion = "Neutral"
        elif -0.5 <= compound <= -0.05:
            emotion = "Sad"
        else:  # compound < -0.5
            emotion = "Upset"
    
        return compound, emotion