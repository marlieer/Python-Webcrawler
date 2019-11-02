# referencing kaggle.com
# YouTube comment sentiment analysis using texblob
import youtube_sentiment as yt
import psycopg2
import warnings
warnings.filterwarnings("ignore")

def connectDb():
    try:
            connection = psycopg2.connect(user = "marlie",
                                          password = "secret",
                                          host = "127.0.0.1",
                                          port = "5433",
                                          database = "honours")
            cursor = connection.cursor()
            print("connection open")
            
            return cursor, connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)


def getSentiment():
    try:
        cursor, connection = connectDb()
        cursor.execute("""SELECT video_id FROM comments WHERE text IS NOT NULL""")
        results = cursor.fetchall()

        for video_id in results:
            print(video_id)
            sent_model = "lr_sentiment_basic.pkl"
            api_key = "AIzaSyC7OpR3BhPly7MEiy_fQkU_6s7wIMBk77U"
            max_pages_comments = 1
            
            print(yt.video_summary(api_key,videoId, max_pages_comments, sent_model))

    except IndexError as e:
        print("Index Error in GetSentiment:", e)
        
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("connection closed")
        

def main():
    getSentiment()


if __name__=="__main__":
    main()
