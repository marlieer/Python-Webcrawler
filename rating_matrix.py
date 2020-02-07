import numpy as np

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

        # append user_id of similar users to list
        for i in range(0, len(user_similarity)):

            # go through sorted list of a user's similarity to other users
            similar_users = []
            for user in sorted(user_similarity[i], reverse=True):

                # get the indexes of the highest similarity users in un-sorted list
                results = np.where(user_similarity[i] == user)

                # for every index, get the user_id from the original df
                # and append to similar_users list if it is not already added
                for r in results[0]:
                    if df.index.values[r] not in similar_users:
                        similar_users.append(df.index.values[r])

            text = (",".join(str(x) for x in similar_users[1:(round(len(similar_users)/2))]))
            print(text)
            print(int(df.index.values[i]))
            cursor.execute("""UPDATE users SET similar_users = %s where id = %s""",
                           (text, int(df.index.values[i])))
            connection.commit()

    except Exception as e:
        print("Exception in getValueforMatrixDimensions: ", e)

    finally:
        closeConnection(connection, cursor)


if __name__ == "__main__":
    createMatrix()
