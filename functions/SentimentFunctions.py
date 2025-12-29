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

    list = ["""I am grateful for speaking to James to get certain things off my chest. Our conversation quickly became talking about life rather than the things getting me down and it made me remember why I love talking to him. For my health I spent the day in bed, which isn't the most ideal but is what it is. And for someone else, I did a lot of work for SOS and supported my committee colleagues.
For my picture today I've added one of Penny with her pom pom. Did make me smile this morning."""
,"I am extremely grateful for still having old work colleagues in my life and that I can still find the energy to see them.  I also didn't go to Dewys wedding because I was so tired, but I am glad I made the effort. I felt like I was regaining a little bit of my old self which surprised me a bit because I missed it. For my health I made sure I ate well and although I didn't have time to exercise I did manage to get some more steps in than yesterday. It was also me that organised the wedding card so we had a cute one from all of us to give."
,"I am very pleased that rehearsals went well today and had strawberries and cream for pudding. It has been a really nice day with James and both Penny and Basil have been spoiled. Singing has been a good use of my time for my wellbeing, though I may have taken on a bit too much with the entertainers work - it has been biting off a little more than I want to chew. However putting together the music for everyone did make it all feel a bit more worth it. Oh and also the house is lovely and clean."
,"Today I managed to get out for a long walk with a new friend. This is someone who is hurting so it was nice to let her have someone to chat to. She does make me a bit nervous though because of bad past experiences but Iâ€™m really glad I went through with seeing her. For my health I think the walk counts. A bonus thing I am grateful for is James and his adult panto stuff, Iâ€™ve attached a picture today from their promo - it really made me smile!"""
,"Today I am most grateful for the peaceful and calm moments between storms, and having the chance to gently stroke Jamesâ€™ head while he talks about having a good day and also talking about me to his friends. I really get the sense heâ€™s coming out of a dark spot and Iâ€™m so so happy for him. For me today I had a nice relaxing bath and finally used my Cinnamonroll bath bomb. "
,"Today Iâ€™m feeling grateful for my team and the people around me. I think Dan K nearly cried again in our catch up. Iâ€™m reminded that everyone is human and although sometimes that is hard I think itâ€™s beautiful. For my health I walked a good amount and also decided to try to be in a better mood today. I helped James with Power BI today. It was tough but did eventually get there. I am starting to wonder what life would feel like if I wasnâ€™t so tired all the time but oh well. Anyway my whole team were in for like the first time in a very long time and will be that way for a while. In fact I donâ€™t think we will ever all be back together, so this is a memory of that. "
,"Today I told myself off out loud and it really worked. So Iâ€™m grateful for my self awareness that got me over some really tough anxiety. I was in a good mood when James came home which meant we were both having a nice time. I had gone out and got him a pie and some dessert choices and he settled on crÃ¨me brÃ»lÃ©e. I feel like going out to get some dessert and treat ourselves after a tricky week was good for me too. "
,"I upset James slightly this morning by belittling his caring about Penny being on the side. I didnâ€™t mean it, I just really hate the spikes. So I put together a plan to create an automated cat sprayer to spray her with water if she goes up on the side! James was so delighted with it and Iâ€™m so happy. Iâ€™m grateful for Luke today who made me smile a lot! And for my health I managed to clear off my todo list. Tomorrow I think I will be able to genuinely relax which is kind of mad. "
,"I am grateful for the time I got to have today. I also cleaned the fridge. And I gave Fi a piece of KFC (drumstick). A simple day today but a good one. "
,"Iâ€™m really grateful to James who drove me to the hospital this morning and stayed with me even though I told him he could stay home. He slept on the waiting room chairs and it was nice to have his company whilst I was quite scared. I had a nice long bath after the ordeal and I somehow managed to sort out the carols rehearsal I proceeded to miss as well as despite not being there it apparently went rather well. "
,"I am grateful for the quiet moments of rest. And being able to finish a lot of things on my list. For me I took a sick day which was worth doing. And for someone else I gave Amber a birthday gift and she loved it. "
,"I am grateful for central heating. I did a lot of cycling and walking today. And if sorting the carols rehearsal tonight was not selfless enough then I donâ€™t know what isâ€¦"
,"Claire and Ollie read my blog about this journal! I am grateful for this. For me today Iâ€™m not sure I did anything, Iâ€™m trying to think but itâ€™s been quite a slow and rubbish day I think I neglected myself. For others Iâ€™m still counting the SOS carols stuff though not sure I feel that grateful for it but trying to remain positive. Also James bought me a bun."
,"Grateful for so much today. I got to see James in his Pussy in Boots show. George and I went on a fair ground round. I drank too much and spent lots of time with friends. I caught up with the cast, and generally just felt so proud of James. Just an all round good day."
,"I am grateful for the people around me who got me through my time at work. Work will never be for me, itâ€™s horrible, buts it the people that help you through. (Though some people do suck!!) for me today I felt good adding things to sell to Vinted. For others Iâ€™ve kept the house tidy and popped things into the attic. "
]
    for text in list:
        print(get_topic(text))