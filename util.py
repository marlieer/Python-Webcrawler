import re
import string
import psycopg2
import requests
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize


def cleanText(text):
    try:

        # convert to lower case
        text = text.lower()

        # remove punctuation and white spaces
        text = re.sub(r"[,.;@#?!&$]+\ *", " ", text)
        text = text.translate(str.maketrans('', '', string.punctuation)).strip()

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

        return text

    except Exception as e:
        print("Error in cleanText:", e)


# close database connection
def closeConnection(connection, cursor):
    if (connection):
        cursor.close()
        connection.close()
        print("Postgres connection closed")


def connect():
    try:
        connection_string = "dbname='homestead' user='homestead' password='secret' port='54320'"
        connection = psycopg2.connect(connection_string, sslmode='require')
        cursor = connection.cursor()

        print("connection open")

        return cursor, connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)


def getSentiment(text):
    try:
        data = {
            'text': text
        }

        response = requests.post('http://text-processing.com/api/sentiment/', data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Status code error')
    except Exception as e:
        print("Exception in getSentiment:", e)

