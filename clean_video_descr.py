# @Marlie Russell 2019 | YouTube Recommender
# Cleans video descriptions

import psycopg2
from comment_sentiment_analysis_API import cleanText
from connectDb import connect


# collect all the video descriptions in the database
def retrieveDescr():
    try:
        cursor, connection = connect()
        cursor.execute("""SELECT descr,v_id FROM video;""")
        results = cursor.fetchall()

        # clean the text for each description retrieved
        for result in results:
            text = result[0]
            clean_text = cleanText(text)
            if not (clean_text and clean_text.strip()):
                clean_text = ' '

            # update database with cleaned description
            cursor.execute("""UPDATE video SET clean_descr = %s
                WHERE v_id = %s""", (clean_text, result[1]))
            connection.commit()
            print("Success ", result[1])

    except IndexError as e:
        print("Index Error in retrieveComments:", e)
    except Exception as e:
        print("Error in retrieveComments:", e)
        print("\nComment ID:", result[1])

    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("connection closed")


def main():
    retrieveDescr()


if __name__ == "__main__":
    main()