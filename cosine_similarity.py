# @Marlie Russell 2019 | YouTube Recommender
# Computes cosine similarity matrix for videos in database
# using "How to build a content-based movie recommender system with NLP" tutorial from towardsdatascience.com
# inputs: likes, dislikes, views, title, description, comment prob_pos,
#   comment prob_neg, comment prob_neutral, channel_name,


import pandas as pd
from rake_nltk import Rake
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import psycopg2
from connectDb import connect


# create similarity matrix
def matrix(df):
    # all the numeric values
    df_num = df[['likes', 'dislikes', 'views',
                 'AVG(prob_pos)', 'AVG(prob_neg)',
                 'AVG(prob_neutral)']]

    # create column 'text' to store a row's title and channel name
    text_list = []
    for index, row in df.iterrows():
        text_list.append(row['title'] + " " + row['channel_name'].replace(" ", ""))
    df['text'] = text_list

    # transform text into count_matrix for similarity between words
    count = TfidfVectorizer()
    count_matrix = count.fit_transform(df['text'])

    # append df_num to df_text and compute cosine similarity
    doc_term_matrix = count_matrix.todense()
    df_text = pd.DataFrame(doc_term_matrix, columns=count.get_feature_names())
    final_df = np.concatenate([df_text,df_num], axis=1)
    cosine_sim = cosine_similarity(final_df, final_df)

    np.savetxt('cos_sim.csv', cosine_sim)

    # create Series with similarity scores in descending for first entry
    score_series = pd.Series(cosine_sim[0]).sort_values(ascending=False)
    top_3_indexes = list(score_series.iloc[1:4].index)
    print(top_3_indexes)
    for i in top_3_indexes:
        print(df['url'][i])


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
                        GROUP BY v_id, video.likes, video.dislikes, views, title LIMIT 15;""")
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
