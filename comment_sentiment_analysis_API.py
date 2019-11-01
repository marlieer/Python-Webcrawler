import requests
import psycopg2

# connect to database
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


# sent curl request to get sentiment and probability
def getSentiment(text):
    data = {
      'text': text
    }

    response = requests.post('http://text-processing.com/api/sentiment/', data=data)
    return response.json()


# retrieve comments from database
def retrieveComments():
    try:
        cursor, connection = connectDb()
        cursor.execute("""SELECT text, c_id FROM comments
            WHERE text IS NOT NULL""")
        results = cursor.fetchall()

        #get sentiment for each comment retrieved
        for result in results:
            text = result[0]
            sent_analysis = getSentiment(text)
            sentiment = sent_analysis['label']
            prob_neg = sent_analysis['probability']['neg']
            prob_pos = sent_analysis['probability']['pos']
            prob_neutral = sent_analysis['probability']['neutral']

            cursor.execute("""UPDATE comments SET sentiment = %s,
                prob_pos = %s, prob_neg = %s, prob_neutral = %s
                WHERE c_id = %s""", (sentiment, prob_pos, prob_neg,
                prob_neutral, result[1]))
            connection.commit()
            print("Updated Comments table with sentiment")

    except IndexError as e:
        print("i: ", i)
        print("Index Error in retrieveComments:", e)

        print("Error in retrieveComments:", e)
        
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("connection closed")
            
    
def main():
    retrieveComments()


if __name__=="__main__":
    main()
