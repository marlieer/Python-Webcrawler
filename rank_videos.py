# @Marlie Russell 2019 | YouTube Recommender
# Ranks videos in database for a particular search query. Ranks based on YouTube likes, dislikes, views, comment sentiment
import pandas as pd

from connectDb import connect
from cosine_similarity import matrix


# retrieve YouTube videos from database and rank
def rank(searchQ):
    try:
        cursor, connection = connect()
        cursor.execute("""SELECT video.likes, video.dislikes, views, title,
                                descr, clean_descr, channel_name,
                                AVG(comments.prob_pos),AVG(comments.prob_neg),
                                AVG(comments.prob_neutral), v_id, url, video.duration
                                FROM comments join video
                                ON comments.video_id = video.v_id
                                WHERE "searchQ" = 'binary tree'
                                AND video.duration = 'short'
                                GROUP BY v_id, video.likes, video.dislikes, views, title
                                ORDER BY views desc, video.likes desc;""")
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=['likes', 'dislikes', 'views', 'title', 'descr',
                                            'clean_descr', 'channel_name', 'AVG(prob_pos)', 'AVG(prob_neg)',
                                            'AVG(prob_neutral)', 'v_id', 'url', 'duration'])

        matrix(df)

    except Exception as e:
        print(e)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")


def main():
    rank("binary tree")

if __name__ == "__main__":
    main()
