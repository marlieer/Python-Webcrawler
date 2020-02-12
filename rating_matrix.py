from util import connect, closeConnection
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def computeAverUserRatings(df):
    # compute average user ratings for later user
    avg_user_ratings = []
    for i in range(0, len(df.index)):

        # compute average rating
        avg_rating = 0
        for j in range(0, len(df.columns)):
            avg_rating += df.iat[i, j]

        avg_rating /= len(df.columns)
        avg_user_ratings.append(avg_rating)

    return avg_user_ratings


def predictMissingRating(u, v, df):

    avg_user_ratings = computeAverUserRatings(df)
    user_avg_rating = avg_user_ratings[u]
    user_similarity = cosine_similarity(df)

    similar_user_ratings = 0
    for k in range(0, len(user_similarity[u])):
        if df.iat[u, k] != 0:
            weight = user_similarity[u][k]
            similar_user_ratings += weight * (df.iat[k, v] - avg_user_ratings[k])

    rating = user_avg_rating + similar_user_ratings
    if rating > user_avg_rating:
        user_id = int(df.index.values[u])
        video_id = str(df.columns.values[v])

        cursor, connection = connect()
        try:
            cursor.execute("SELECT v_id FROM recommendations WHERE u_id = %s;", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO recommendations (u_id, v_id) VALUES (%s, %s);",
                               (user_id, video_id,))
                connection.commit()

        except Exception as e:
            print("Exception while inserting: ", e)

        finally:
            closeConnection(connection, cursor)


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
        cursor.execute("SELECT id, u_id, v_id, rating from myvideos;")
        results = cursor.fetchall()
        for r in results:
            df.at[r[1], r[2]] = r[3]

        return df

    except Exception as e:
        print("Exception in createMatrix: ", e)

    finally:
        closeConnection(connection, cursor)


def estimateMissingRatings(df):

    for u in range(0, len(df.index)):
        for v in range(0, len(df.columns)):
            if df.iat[u, v] == 0:
                df.iat[u, v] = predictMissingRating(u, v, df)

    df.to_csv('rating_matrix.csv', index=True, header=True)


if __name__ == "__main__":
    estimateMissingRatings(createMatrix())
