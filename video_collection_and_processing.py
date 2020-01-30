import detectlanguage
from util import cleanText, getSentiment, connect, closeConnection
from google_api_youtube_search import search


def clean_video_description(search_q):
    """
    cleans video description stored in database and stores cleaned
    text in the database under clean_descr

    :return: void
    """

    try:
        cursor, connection = connect()
        cursor.execute("""SELECT descr,v_id FROM video WHERE "searchQ" = %s;""", (search_q,))
        results = cursor.fetchall()

        # clean the text for each description retrieved
        for result in results:
            text = result[0]
            clean_text = cleanText(text)
            if not (clean_text and clean_text.strip()):
                clean_text = ' '

            # update database with clean description
            cursor.execute("""UPDATE video SET clean_descr = %s
                WHERE v_id = %s""", (clean_text, result[1]))
            connection.commit()
            print("Success ", result[1])

    except Exception as e:
        print("Error in cleanVideoDescription:", e)
    finally:
        closeConnection(connection, cursor)


def detect_language(search_q):
    """
        Uses detectlanguage API to determine language of video based on video title and cleaned description
        API returns json result with string: predicted language, boolean: isReliable and double: confidence level
        Updates video table in database with detectlanguage data

       :returns: void
    """
    try:
        cursor, connection = connect()
        cursor.execute("""SELECT title, clean_descr, v_id 
                         FROM video      
                         WHERE "searchQ" = %s;""", (search_q,))
        results = cursor.fetchall()

        # configure language detection API
        detectlanguage.configuration.api_key = "eea8968a48d7b6af0a3de993f7f401e0"

        # for each result from the database, detect language from title and clean description
        for result in results:
            text = result[0] + " " + result[1]
            v_id = result[2]
            json = detectlanguage.detect(text)[0]

            # update database with language data (language, isReliable, confidence level)
            cursor.execute(
                """UPDATE video SET language = %s, is_reliable = %s,
                confidence = %s WHERE v_id = %s""",
                (json['language'], json['isReliable'], json['confidence'], v_id))
            connection.commit()

    except Exception as e:
        print("Exception in detect_language:", e)
    finally:
        closeConnection(connection, cursor)


def retrieve_comments_for_cleaning(search_q):
    """
        retrieves comments from the database and preps them for cleaning
        calls cleanText from util
        checks comments after cleaning and inserts clean text into database

        :return: void
        """
    try:
        cursor, connection = connect()
        cursor.execute("""SELECT text, c_id FROM comments
            JOIN video ON video.v_id = comments.video_id
            WHERE text IS NOT NULL AND "searchQ" = %s""", (search_q,))
        results = cursor.fetchall()

        # get sentiment for each comment retrieved
        for result in results:
            try:
                text = result[0]

                # clean the text
                clean_text = cleanText(text)

                # if clean text returns null, update database with null and -1 values
                if not (clean_text and clean_text.strip()):
                    sentiment = 'null'
                    prob_neg, prob_pos, prob_neutral = -1

                    cursor.execute("""UPDATE comments SET clean_text = %s,
                                    sentiment = %s,
                                    prob_pos = %s, prob_neg = %s, prob_neutral = %s
                                    WHERE c_id = %s""", (clean_text, sentiment, prob_pos, prob_neg,
                                                         prob_neutral, result[1]))
                    connection.commit()

                # if clean_text returns something, analyze the sentiment
                else:
                    sent_analysis = getSentiment(clean_text)
                    sentiment = sent_analysis['label']
                    prob_neg = sent_analysis['probability']['neg']
                    prob_pos = sent_analysis['probability']['pos']
                    prob_neutral = sent_analysis['probability']['neutral']

                    # update the database
                    cursor.execute("""UPDATE comments SET clean_text = %s,
                        sentiment = %s,
                        prob_pos = %s, prob_neg = %s, prob_neutral = %s
                        WHERE c_id = %s""", (clean_text, sentiment, prob_pos, prob_neg,
                                             prob_neutral, result[1]))
                    connection.commit()

            except Exception as e:
                print("Exception in loop in retrieve comments: ", e)

    except IndexError as e:
        print("Index Error in retrieveComments:", e)
    except Exception as e:
        print("Error in retrieveComments:", e)
    finally:
        closeConnection(connection, cursor)


def collect_and_process_videos(search_q):
    search(search_q)
    clean_video_description(search_q)
    detect_language(search_q)
    retrieve_comments_for_cleaning(search_q)


if __name__ == "__main__":
    collect_and_process_videos("Skip List")
