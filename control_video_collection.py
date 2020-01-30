# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import googleapiclient.discovery
from util import connect, closeConnection
from google_api_youtube_search import makeRequestCommentThread


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


# for using the YouTube API
def credentialVerification():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # credential verification for Google Youtube API
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyC7OpR3BhPly7MEiy_fQkU_6s7wIMBk77U"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)
    return youtube


# retrieve control YouTube videos
def retrieveVideos():
    youtube = credentialVerification()
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id="yDKWmNpw7gE, 3uk6rKXbG1M, p-aVhSEO8Ro, t_CbWtSSHMw, z7Tadx4XGjA"
    )
    response = request.execute()

    # connect to database
    cursor, connection = connect()

    # try:
        # collect data on search results
    for video in response['items']:
        VIEWS = video['statistics']['viewCount']
        LIKES = video['statistics']['likeCount']
        DISLIKES = video['statistics']['dislikeCount']
        FAV = video['statistics']['favoriteCount']
        TITLE = video['snippet']['title']
        DESCRP = video['snippet']['description']
        CHAN_ID = video['snippet']['channelId']
        CHAN_TITLE = video['snippet']['channelTitle']
        videoID = video['id']
        URL = "https://youtube.com/watch?v=" + videoID
        searchQ = 'control'

        print(VIEWS, LIKES, DISLIKES, FAV, TITLE, DESCRP, CHAN_ID, CHAN_TITLE, videoID, URL)

        cursor.execute(
            """INSERT INTO video (title, descr, views, likes, dislikes, v_id, channel_id, channel_name, "searchQ", url)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
            (TITLE, DESCRP, VIEWS, LIKES, DISLIKES,
             videoID, CHAN_ID, CHAN_TITLE,
             searchQ, URL))
        connection.commit()
        print("Inserted into Video Table")

        closeConnection(connection, cursor)
        cursor, connection = connect()
        makeRequestCommentThread(videoID, youtube, cursor, connection)


# run program to output titles of YouTube videos
def main():
    retrieveVideos()


if __name__ == "__main__":
    main()
