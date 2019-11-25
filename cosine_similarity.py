# @Marlie Russell 2019 | YouTube Recommender
# Computes cosine similarity matrix for videos in database
# using "How to build a content-based movie recommender system with NLP" tutorial from towardsdatascience.com
# inputs: likes, dislikes, views, title, description, comment prob_pos,
#   comment prob_neg, comment prob_neutral, channel_name,


import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import psycopg2
from connectDb import connect


# generate recommendations based off index
def recommend(index, df, cosine_sim):
    try:
        recommendations = []

        # create Series with similarity scores in descending for first entry
        score_series = pd.Series(cosine_sim[index]).sort_values(ascending=False)
        top_5_indexes = list(score_series.iloc[1:5].index)
        # print(top_5_indexes)
        for x in range(0, len(top_5_indexes)):
            recommendations.append(df['url'][x])
        # print(recommendations)
    except Exception as e:
        print("Exception in recommend:", e)


# create similarity matrix
def matrix(df):
    # create column 'text' to store a row's title and channel name
    text_list = []
    for index, row in df.iterrows():
        text = row['title'] + " " + row['clean_descr'] + " " + row['channel_name'].replace(" ", "")
        # add channel name to text multiple times to increase similarity
        for x in range(0, 11):
            text += " " + row['channel_name'].replace(" ", "")
        text_list.append(text)
    df['text'] = text_list

    # transform text into count_matrix for similarity between words
    count = TfidfVectorizer()
    count_matrix = count.fit_transform(df['text'])

    # append df_num to df_text and compute cosine similarity
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    print(cosine_sim)

    # save as csv
    np.savetxt('cos_sim.csv', cosine_sim)

    # generate recommendations
    for i in range(len(cosine_sim)):
        recommend(i, df, cosine_sim)


# collect vector inputs
def collectInputs():
    try:
        cursor, connection = connect()

        cursor.execute("""SELECT video.likes, video.dislikes, views, title,descr,
                        clean_descr, channel_name, AVG(comments.prob_pos)*100,
                        AVG(comments.prob_neg)*100,
                        AVG(comments.prob_neutral)*100, v_id, url
                        FROM comments join video
                        ON comments.video_id = video.v_id
                        WHERE "searchQ" = 'control'
                        GROUP BY v_id, video.likes, video.dislikes, views, title
                        ORDER BY views desc;""")
        results = cursor.fetchall()

        # create DataFrame from Query result
        df = pd.DataFrame(results, columns=['likes', 'dislikes', 'views', 'title',
                                            'descr', 'clean_descr', 'channel_name',
                                            'AVG(prob_pos)', 'AVG(prob_neg)',
                                            'AVG(prob_neutral)', 'v_id', 'url'])

        # pass df to matrix operation
        matrix(df)

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")


def main():
    collectInputs()


if __name__ == "__main__":
    main()
