import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from util import connect, closeConnection


def collect_inputs(search_q):
    try:
        cursor, connection = connect()

        cursor.execute("""SELECT video.likes, video.dislikes, views, title,descr,
                        clean_descr, channel_name, video.duration, AVG(comments.prob_pos)*100,
                        AVG(comments.prob_neg)*100,
                        AVG(comments.prob_neutral)*100, v_id, url
                        FROM comments right join video
                        ON comments.video_id = video.v_id
                        WHERE "searchQ"=%s
                        GROUP BY v_id, video.likes, video.dislikes, views, title
                        ORDER BY views desc;""", (search_q,))
        results = cursor.fetchall()

        return results

    except Exception as e:
        print("Exception in collectInputs:", e)
    finally:
        closeConnection(connection, cursor)


# create similarity matrix
def compute_cosine_similarity(results):
    try:
        # create DataFrame from Query result
        df = pd.DataFrame(results, columns=['likes', 'dislikes', 'views', 'title',
                                            'descr', 'clean_descr', 'channel_name',
                                            'duration', 'AVG(prob_pos)', 'AVG(prob_neg)',
                                            'AVG(prob_neutral)', 'v_id', 'url'])
        # create column 'text' to store a row's title and channel name
        text_list = []
        for index, row in df.iterrows():
            text = row['title'] + " " + row['clean_descr']
            text_list.append(text)
        df['text'] = text_list

        # transform text into count_matrix for similarity between words
        count = CountVectorizer()
        count_matrix = count.fit_transform(df['text'])

        # append df_num to df_text and compute cosine similarity
        cosine_sim = cosine_similarity(count_matrix, count_matrix)

        # generate recommendations
        for i in range(len(cosine_sim)):
            recommend(i, df, cosine_sim)

    except Exception as e:
        print("Exception in compute-cosine-similarity: ", e)


def euclidean_distance(results):
    # create DataFrame from Query result
    results_array = np.array(results)[:, [0, 1, 2, 8, 9, 10, 11]]

    # go through results. Wherever there is an entry of NoneType, replace with -1
    for x in range(0, len(results_array)):
        if results_array[x][3] is None:
            results_array[x][3] = -1
            results_array[x][4] = -1
            results_array[x][5] = -1

    # initialize empty array of Euclidean distances (n x n)
    euc_distances = np.zeros(shape=(len(results_array), len(results_array)))

    # nested loop through every entry in the results to compute euclidean distance between each result
    for x in range(0, len(results_array)):
        for y in range(0, len(results_array)):
            # only take columns 1:6 (exclude column of v_id). Save in euc_distances array
            d = distance.euclidean(results_array[x, 1:6], results_array[y, 1:6])
            euc_distances[x][y] = d

    # save as csv with video ID as column headers
    df = pd.DataFrame(euc_distances, columns=results_array[:, 6], index=results_array[:, 6])
    df.to_csv('euc_distances.csv')
    # np.savetxt('euc_distances.csv', euc_distances, delimiter=',', fmt='%d')


def recommend(index, df, cosine_sim):
    # generate recommendations based off index
    try:
        recommendations = []

        # create Series with similarity scores in descending for first entry
        score_series = pd.Series(cosine_sim[index]).sort_values(ascending=False)
        top_5_indexes = list(score_series.iloc[1:5].index)
        for x in range(0, len(top_5_indexes)):
            recommendations.append(df['url'][top_5_indexes[x]])
        # print(recommendations)
    except Exception as e:
        print("Exception in recommend:", e)


def rank_videos(results):
    results_array = np.array(results)
    tally = np.ones((len(results_array), 1))
    for x in range(0, len(results_array)):
        tally[x][0] = (results_array[x][0] - results_array[x][1] + results_array[x][2])
    # print(np.hstack((results_array, tally)))


def compute_video_similarity(search_q):
    results = collect_inputs(search_q)
    compute_cosine_similarity(results)
    euclidean_distance(results)
    rank_videos(results)


if __name__ == "__main__":
    compute_video_similarity("Generics")
    compute_video_similarity("Lists")
