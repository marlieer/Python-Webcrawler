from util import connect, closeConnection
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import math
import pandas.io.sql as sqlio


def rankVideos():
    cursor, connection = connect()
    try:
        # retrieve video stats
        sql = "SELECT v_id, likes, dislikes, views FROM video;"
        df = sqlio.read_sql_query(sql, connection)
        connection = None

        # compute average views
        total_views = 0
        for i in range(0, len(df)):
            total_views += df.iat[i, 3]
        avg_views = total_views / len(df)

        # video ranking = [(likes-dislikes) / views]*log(views/avg_views)
        video_rankings = {}
        for i in range(0, len(df)):
            v_id = df.iat[i, 0]
            likes = df.iat[i, 1]
            dislikes = df.iat[i, 2]
            views = df.iat[i, 3]

            if views == 0:
                rank = 0
            else:
                rank = ((likes - dislikes) / views) * math.log(views / avg_views)

            video_rankings[v_id] = rank

        return video_rankings

    except Exception as e:
        print("Exception in rank videos: ", e)

    finally:
        closeConnection(connection, cursor)


def computeAverUserRatings(df):
    # compute average user ratings for later user
    avg_user_ratings = {}
    for i in range(0, len(df.index)):

        # compute average rating
        avg_rating = 0
        for j in range(0, len(df.columns)):
            avg_rating += df.iat[i, j]

        avg_rating /= len(df.columns)
        avg_user_ratings[df.index.values[i]] = avg_rating

    return avg_user_ratings


def predictMissingRating(user_id, user_index, video_id, df, avg_user_ratings, cos_sim):
    user_avg_rating = avg_user_ratings[user_id]

    # sort cosine similarity matrix row for the current user index
    user_similarity = cos_sim.iloc[user_index].sort_values(ascending=False)

    # gather similarity weights of first 5 similar users
    weights = {}    # dictionary: key=user_id, value=weight
    total_weight = 0
    user_ids = user_similarity.index.values    # u_id's of similar users

    # start at i=1 since i=0 is the current user who is 100% similar to itself
    for i in range(1, 10):
        # if there are less than 10 users, break
        if i >= len(df.index):
            break

        # if user-i has a rating for video
        if df.at[user_ids[i], video_id] != 0:
            # normalize user-similarities to be between [0, 1]
            w = ((user_similarity.at[user_ids[i]] + 1) / 2)
            total_weight += w
            weights[user_ids[i]] = w

    # if no similar users have rated this item, return 0
    if total_weight == 0:
        return 0

    # compute weighted ratings of similar users
    similar_user_ratings = 0
    # recall, key is user_id associated with that weight
    for k, v in weights.items():
        if df.at[k, video_id] != 0:
            # normalize weights to each other so they add to 1
            weight = v / total_weight
            similar_user_ratings += weight * (df.at[k, video_id] - avg_user_ratings[k])

    rating = user_avg_rating + similar_user_ratings

    return rating


def createMatrix():
    # connect to db to get num columns and rows and data
    cursor, connection = connect()
    try:
        # get all user id's (for rows)
        cursor.execute("SELECT id from users;")
        results = cursor.fetchall()
        index = []
        for r in results:
            index.append(r[0])

        # get all video id's (for columns)
        cursor.execute("SELECT v_id from video;")
        results = cursor.fetchall()
        columns = []
        for r in results:
            columns.append(r[0])

        # create empty matrix of users x videos
        df = pd.DataFrame(0, index=index, columns=columns, dtype=float)

        # get all user ratings on videos (for data)
        cursor.execute("SELECT u_id, v_id, rating from myvideos;")
        results = cursor.fetchall()
        for r in results:
            df.at[r[0], r[1]] = r[2]

        return df

    except Exception as e:
        print("Exception in createMatrix: ", e)

    finally:
        closeConnection(connection, cursor)


def estimateMissingRatings(df):
    # predict every user's video ratings if they have not already rated the video
    video_rankings = rankVideos()
    avg_user_ratings = computeAverUserRatings(df)
    cos_sim = pd.DataFrame(cosine_similarity(df), index=df.index.values, columns=df.index.values, dtype=float)
    for u in range(0, len(df.index)):
        for v in range(0, len(df.columns)):
            if df.iat[u, v] == 0:
                user_id = df.index.values[u]
                video_id = df.columns.values[v]

                r = predictMissingRating(user_id, u, video_id, df, avg_user_ratings, cos_sim)
                c = video_rankings[df.columns.values[v]]

                if r == 0:
                    df.iat[u, v] = c
                elif c == 0:
                    df.iat[u, v] = r
                elif c > 0 and r > 0:
                    df.iat[u, v] = c * r
                elif c < 0 and r < 0:
                    df.iat[u, v] = -c * r
                elif c > 0 and r < 0:
                    df.iat[u, v] = c * r
                elif c < 0 and r > 0:
                    df.iat[u, v] = c + r

                if df.iat[u, v] >= 0:
                    recommend(u, v, df)

    df.to_csv('rating_matrix.csv', index=True, header=True)


def recommend(u, v, df):
    user_id = int(df.index.values[u])
    video_id = str(df.columns.values[v])

    cursor, connection = connect()
    try:
        cursor.execute("SELECT v_id FROM recommendations WHERE u_id = %s and v_id = %s;", (user_id, video_id))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO recommendations (u_id, v_id, rank) VALUES (%s, %s, %s);",
                           (user_id, video_id, df.iat[u, v],))
            connection.commit()

    except Exception as e:
        print("Exception while inserting: ", e)

    finally:
        closeConnection(connection, cursor)


def beginRating():
    df = createMatrix()
    estimateMissingRatings(df)


if __name__ == "__main__":
    beginRating()
