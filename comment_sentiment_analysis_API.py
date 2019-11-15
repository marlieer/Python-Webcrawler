import requests
import psycopg2
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import re


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
    try:
        data = {
          'text': text
        }

        response = requests.post('http://text-processing.com/api/sentiment/', data=data)

        if (response.status_code == 200):
            return response.json()
        else:
            raise Exception('Status code error')
    except Exception as e:
        print("Exception in getSentiment:", e)

# clean text before analyzing sentiment
def cleanText(text):
    try:
        print(text)
        # convert to lower case
        text = text.lower()

        #remove punctuation and white spaces
        text = re.sub(r"[,.;@#?!&$]+\ *", " ", text)
        text = text.translate(str.maketrans('','', string.punctuation)).strip()

        # tokenize and remove stop words with nltk
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(text)
        text = [i for i in tokens if not i in stop_words]

        # lemmatize
        lem = WordNetLemmatizer()
        text = [lem.lemmatize(i) for i in text]

        # stem
        stemmer = PorterStemmer()
        text = " ".join([stemmer.stem(i) for i in text])
        
        print (text)

    except Exception as e:
        print("Error in cleanText:", e)

# retrieve comments from database
def retrieveComments():
    try:
        cursor, connection = connectDb()
        cursor.execute("""SELECT text, c_id FROM comments
            WHERE text IS NOT NULL LIMIT 10""")
        results = cursor.fetchall()

        #get sentiment for each comment retrieved
        for result in results:
            text = result[0]
            clean_text = cleanText(text)
            if (not (clean_text and clean_text.strip())):
                continue
            sent_analysis = getSentiment(clean_text)
            sentiment = sent_analysis['label']
            prob_neg = sent_analysis['probability']['neg']
            prob_pos = sent_analysis['probability']['pos']
            prob_neutral = sent_analysis['probability']['neutral']

            cursor.execute("""UPDATE comments SET clean_text = %s,
                sentiment = %s,
                prob_pos = %s, prob_neg = %s, prob_neutral = %s
                WHERE c_id = %s""", (clean_text, sentiment, prob_pos, prob_neg,
                prob_neutral, result[1]))
            connection.commit()
            print("Updated comment ", result[1])

    except IndexError as e:
        print("i: ", i)
        print("Index Error in retrieveComments:", e)
    except Exception as e:
        print("Error in retrieveComments:", e)
        print("\nComment ID:" , result[1])
  
        
        
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("connection closed")
            
    
def main():
    retrieveComments()


if __name__=="__main__":
    main()
