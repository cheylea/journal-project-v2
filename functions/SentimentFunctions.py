#!/usr/bin/python3
# Set of Python functions for analysing sentiment of text inputs.

# Imports
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk


class SentimentFunctions:
    @staticmethod
    def get_sentiment(text):
        """ Analyse the sentiment of the given text using NLTK's VADER.

        Args:
            text: The text to analyse"""
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
