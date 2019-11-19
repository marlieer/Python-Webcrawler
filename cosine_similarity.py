# @Marlie Russell 2019 | YouTube Recommender
# Computes cosine similarity matrix for videos in database
# using "How to build a content-based movie recommender system with NLP" tutorial from towardsdatascience.com
# inputs: likes, dislikes, views, title, description, comment prob_pos,
#   comment prob_neg, comment prob_neutral, channel_name,


import pandas as pd
from rake_nltk import Rake
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import psycopg2
from connectDb import connect


# create similarity matrix
def matrix(df):
    count = CountVectorizer()
    count_matrix = count.fit_transform(df)
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    print(cosine_sim)
    
# collect vector inputs
def collectInputs():
    try:
        cursor,connection= connect()

        cursor.execute("""SELECT video.likes, video.dislikes, views, title,descr,
                        clean_descr, channel_name, AVG(comments.prob_pos),
                        AVG(comments.prob_neg),
                        AVG(comments.prob_neutral), v_id
                        FROM comments join video
                        ON comments.video_id = video.v_id
                        GROUP BY v_id, video.likes, video.dislikes, views, title;""")
        results = cursor.fetchall()

        # create DataFrame from Query result
        df = pd.DataFrame(results, columns=['likes','dislikes','views','title',
                                            'descr','clean_descr','channel_name',
                                            'AVG(prob_pos)','AVG(prob_neg)',
                                            'AVG(prob_neutral)', 'v_id'])

        # use Rake to collect keywords in descr, assign to column "Key_words"
        df['Key_words']=""
        for index,row in df.iterrows():
            try:
                descr = row['descr']
                r = Rake()
                r.extract_keywords_from_text(descr)
                key_words_dict_scores = r.get_word_degrees()
                row['Key_words'] = list(key_words_dict_scores.keys())
            except (Exception) as e:
                print("Error in Rake loop", e)
        print(df)

        # pass df to matrix operation
        matrix(df[['likes','dislikes','views',
                    'AVG(prob_pos)','AVG(prob_neg)',
                    'AVG(prob_neutral)','Key_words']])


    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")

def main():
    collectInputs()


if __name__=="__main__":
    main()
    

