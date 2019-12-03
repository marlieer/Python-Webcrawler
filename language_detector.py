# from detectlanguage API. Detects language of text

import detectlanguage
from connectDb import connect


def detect_language(text, v_id, cursor, connection):

    # use API to detect language of title
    try:
        detectlanguage.configuration.api_key = "eea8968a48d7b6af0a3de993f7f401e0"
        json = detectlanguage.detect(text)[0]

        # update database with language data (language, isReliable, confidence level"
        cursor.execute(
            """UPDATE video SET language = %s, is_reliable = %s,
            confidence = %s WHERE v_id = %s""",
            (json['language'], json['isReliable'], json['confidence'], v_id))
        connection.commit()

    except Exception as e:
        print("Exception in detect_language:", e)


# retrieve titles from database to detect language
def retrieve_titles():
    try:
        cursor, connection = connect()
        cursor.execute("""SELECT title, clean_descr, v_id 
                        FROM video      
                        WHERE "searchQ"='binary tree';""")
        results = cursor.fetchall()
        # send each title to detect_language
        for result in results:
            detect_language(result[0] + " " + result[1], result[2], cursor, connection)

    except Exception as e:
        print("Exception in retrieve_titles:", e)

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")


def main():
    retrieve_titles()


if __name__ == "__main__":
    main()
