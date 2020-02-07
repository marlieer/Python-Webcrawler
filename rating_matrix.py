from util import connect, closeConnection
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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
        df = pd.DataFrame(0, index=index, columns=columns)

        # get all user ratings on videos (for data)
        cursor.execute("SELECT id, u_id, v_id, rating from myvideos;")
        results = cursor.fetchall()
        for r in results:
            df.at[r[1], r[2]] = r[3]
        df.to_csv('rating_matrix.csv', index=True, header=True)

        # computer user similarity
        user_similarity = cosine_similarity(df)
        print(user_similarity[3])
        print(df.iloc[3])

    except Exception as e:
        print("Exception in getValueforMatrixDimensions: ", e)

    finally:
        closeConnection(connection, cursor)


if __name__ == "__main__":
    createMatrix()
