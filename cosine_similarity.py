# computing cosine similarity matrix for videos in database
# inputs: likes, dislikes, views, title, description, comment prob_pos,
#   comment prob_neg, comment prob_neutral, channel_name,


import pandas as pd
from rake_nltk import Rake
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import psycopg2

def connectDb():
    try:
        connection = psycopg2.connect(user = "marlie",
                                      password = "secret",
                                      host = "127.0.0.1",
                                      port = "5433",
                                      database = "Honours")
        cursor = connection.cursor()

        cursor.execute("""SELECT video.likes, video.dislikes, views, title,
                        descr, channel_name, comments.prob_pos, comments.prob_neg,
                        comments.prob_neutral
                        FROM comments JOIN video
                        ON comments.video_id = video.v_id;""")
        record = cursor.fetchone()
        print (record)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")

df = pd.read_csv('https://query.data.world/s/uikepcpffyo2nhig52xxeevdialfl7')

df = df[['Title','Genre','Director','Actors','Plot']]
df.head()
