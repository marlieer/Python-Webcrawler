# -*- coding: utf-8 -*-

# Expanded from sample Python code for youtube.search.list and youtube.statistics.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python
import psycopg2
import os
import googleapiclient.discovery

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# connect to Database
def connectDb():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "97humoreske",
                                      host = "127.0.0.1",
                                      port = "5433",
                                      database = "Honours")
        cursor = connection.cursor()
        
        return cursor, connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to Postgres", error)

# close database connection
def closeConnection(connection, cursor):
        if (connection):
            cursor.close()
            connection.close()
            print("Postgres connection closed")

def credentialVerification():
# Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # credential verification for Google Youtube API
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyC7OpR3BhPly7MEiy_fQkU_6s7wIMBk77U"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)
    return youtube


# search for video statistics and data and comments
def makeRequestVideos(searchSubject,videoID, youtube, cursor, connection, dur):
    # Form request parameter
    request = youtube.videos().list(
        part="statistics, snippet",
        id = videoID
        )
    response = request.execute()
    try:
        # collect data on video
        VIEWS = response['items'][0]['statistics']['viewCount']
        LIKES = response['items'][0]['statistics']['likeCount']
        DISLIKES = response['items'][0]['statistics']['dislikeCount']
        FAV = response['items'][0]['statistics']['favoriteCount']
        COMMENTS = response['items'][0]['statistics']['commentCount']
        TITLE = response['items'][0]['snippet']['title']
        DESCRP = response['items'][0]['snippet']['description']
        CHAN_ID = response['items'][0]['snippet']['channelId']
        CHAN_TITLE = response['items'][0]['snippet']['channelTitle']

        # query to see if video is already in db. If yes, update stats, if no, insert
        cursor.execute("""SELECT * FROM "Video" WHERE v_id = %s;""", (videoID,))
        if (cursor.fetchone() is not None):
            cursor.execute(
                """UPDATE "Video" SET likes = %s, dislikes = %s,
                fav_count = %s, com_count = %s, channel_id = %s,
                channel_name = %s, "searchQ" = %s, duration = %s WHERE v_id = %s""",
                (LIKES,DISLIKES,FAV,COMMENTS, CHAN_ID,CHAN_TITLE,
                searchSubject,dur, videoID))
            connection.commit()
            print("Updated data base")
           
        else:
            cursor.execute(
                    """INSERT INTO "Video"
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                    (TITLE, DESCRP, VIEWS, LIKES, DISLIKES, FAV,
                     COMMENTS, videoID, CHAN_ID, CHAN_TITLE, searchSubject,dur))
            connection.commit()
            print("Inserted into database")
    
    except KeyError as e:
        print ("key error:", e)
    except:
        print("Something else went wrong")
       
# search for video results
def makeRequestVideoList(searchSubject,dur):
        youtube = credentialVerification()
        request = youtube.search().list(
            part="snippet,id",
            q=searchSubject,
            type="video",
            maxResults=30,
            videoDuration=dur,
        )
        response = request.execute()
        cursor, connection = connectDb()

        # collect data on search results
        for i in range(0,30):
            VIDEO_ID = response['items'][i]['id']['videoId']

            #for each video, request more video information
            makeRequestVideos(searchSubject,VIDEO_ID, youtube,cursor,connection,dur)

        closeConnection(connection,cursor)


def search(searchQ):
    makeRequestVideoList(searchQ,"short")
    makeRequestVideoList(searchQ + "tutorial","short")
    makeRequestVideoList(searchQ + "explain","short")
    makeRequestVideoList(searchQ,"medium")
    makeRequestVideoList(searchQ+ "explain","medium")
    makeRequestVideoList(searchQ + "tutorial","medium")
    makeRequestVideoList(searchQ,"long")
    makeRequestVideoList(searchQ +"explain","long")
    makeRequestVideoList(searchQ + "tutorial","long")
    
def main():
# run program to output titles of YouTube videos
    search("binary tree tutorial")

if __name__ == "__main__":
    main()
