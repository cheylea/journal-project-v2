#!/usr/bin/python3
# Set of Python functions for analysing sentiment of text inputs.

# Imports
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
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
    
    def get_topic(text):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        topics = {
            "family": "family, parents, auntie, Blair, Bo, James, Kezia, Serenity, Martha, spouse, partner",
            "health": "health, wellbeing, exercise, meditation, running, walking, sleep, diet, food, nutrition, gym, tidy",
            "work": "job, career, projects, Workdry, council, boss, colleagues, team",
            "nature": "nature, parks, walks, outdoors, trees, greenery, hiking, steps, climbing, mountains",
            "pets": "cats, pets, animals, Penny, Basil, kitty"
        }

        topic_embeddings = model.encode(list(topics.values()), convert_to_tensor=True)

        entry_emb = model.encode(text, convert_to_tensor=True)
        sims = util.cos_sim(entry_emb, topic_embeddings)[0]
        best_idx = sims.argmax()
        return list(topics.keys())[best_idx]