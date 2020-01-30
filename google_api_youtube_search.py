# @Marlie Russell 2019 | YouTube Recommender

# Expanded from sample Python code for youtube.search.list and youtube.statistics.list
# https://developers.google.com/explorer-help/guides/code_samples#python
import os
import googleapiclient.discovery
from util import connect, closeConnection

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def credentialVerification():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # credential verification for Google Youtube API
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyC7OpR3BhPly7MEiy_fQkU_6s7wIMBk77U"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)
    return youtube


def makeRequestVideos(search_subject, video_id, youtube, dur):
    """
        Uses YouTube API to make a request for video data based on video ID parameter.
        Stores data in database

        :param search_subject: search subject of video (for database entry)
        :type search_subject: string

        :param video_id: video id of YouTube video
        :type video_id: string

        :param youtube: youtube API service instance
        :type youtube: googleapiclient.discovery built instance

        :param dur: duration of video (for database entry)
        :type dur: string


        :returns: void
    """

    # Form request parameter
    request = youtube.videos().list(
        part="statistics, snippet",
        id=video_id
    )

    try:
        cursor, connection = connect()
        response = request.execute()

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
        URL = "https://youtube.com/watch?v=" + video_id

        # make sure title matches search subject. If it doesn't, break out of loop
        if search_subject.lower() in TITLE.lower():
            # query to see if video is already in db. If yes, update stats, if no, insert
            cursor.execute("""SELECT * FROM video WHERE v_id = %s;""", (video_id,))
            if cursor.fetchone() is not None:
                cursor.execute(
                    """UPDATE video SET likes = %s, dislikes = %s,
                    fav_count = %s, com_count = %s, channel_id = %s,
                    channel_name = %s, "searchQ" = %s, duration = %s,
                    url = %s WHERE v_id = %s""",
                    (LIKES, DISLIKES, FAV, COMMENTS, CHAN_ID, CHAN_TITLE,
                     search_subject, dur, URL, video_id))
                connection.commit()

            else:
                cursor.execute(
                    """INSERT INTO video
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                    (TITLE, DESCRP, VIEWS, LIKES, DISLIKES, FAV,
                     COMMENTS, video_id, CHAN_ID, CHAN_TITLE,
                     search_subject, dur, URL))
                connection.commit()
                print("Inserted into Video Table")

            return True

        else:
            return False

    except KeyError as e:
        print("key error:", e)
    except Exception as e:
        print("Exception in MakeVideoRequest:", e)
    finally:
        closeConnection(connection, cursor)


def makeRequestCommentThread(video_id, youtube):
    """
       Uses YouTube API to make a request for the comment thread for a video.
       Stores data in database

       :param video_id: video id of YouTube video
       :type video_id: string
       
       :param youtube: youtube API service instance
       :type youtube: googleapiclient.discovery built instance

       :returns: boolean. True if video inserted into database. False if not
    """

    # make request for comment thread of video
    request = youtube.commentThreads().list(
        part="id,snippet",
        videoId=video_id,
    )

    try:
        cursor, connection = connect()

        response = request.execute()
        for comment in response['items']:
            c_id = comment['snippet']['topLevelComment']['id']
            author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            text = comment['snippet']['topLevelComment']['snippet']['textOriginal']
            likes = comment['snippet']['topLevelComment']['snippet']['likeCount']
            published_at = comment['snippet']['topLevelComment']['snippet']['publishedAt']
            updated_at = comment['snippet']['topLevelComment']['snippet']['updatedAt']


            # store comment thread information in the database
            # make a search to see if comment is already stored in database
            cursor.execute("""SELECT * FROM comments WHERE c_id = %s;""", (c_id,))

            # if comment is returned, update comment information
            if cursor.fetchone() is not None:
                cursor.execute(
                    """UPDATE comments SET text = %s, likes = %s,
                    updated_at = %s WHERE c_id = %s""",
                    (text, likes, updated_at, c_id))
                connection.commit()

            # otherwise, insert comment into database
            else:
                cursor.execute(
                    """INSERT INTO comments
                        VALUES(%s,%s,%s,%s,%s,%s,%s);""",
                    (c_id, text, likes, author,
                     video_id, published_at,
                     updated_at))
                connection.commit()
                print("Inserted Comment into database")

    except KeyError as e:
        print("key error:", e)
    except IndexError as e:
        print("Index error in MakeRequestCommentThreads:", e)
    except TypeError as e:
        print("type error:", e)
    except googleapiclient.errors.HttpError as e:
        print("Comments disabled:", e)
    except Exception as e:
        print("Exception in makeRequestCommentThreads", e)
    finally:
        closeConnection(connection, cursor)


def makeRequestVideoList(search_q, dur):
    """
        Uses YouTube API to make a request for a list of videos based on
        the search query parameter.

        :param search_q: search query subject for video list request
        :type search_q: string

        :param dur: filters video list to only contain videos of specified duration
            (ex. short, medium, long)
        :type dur: string


        :returns: void
    """

    # verify API credentials
    youtube = credentialVerification()

    # request parameters
    request = youtube.search().list(
        part="snippet,id",
        q='Intro to Java ' + search_q,
        type="video",
        maxResults=15,
        order="relevance",
        videoDuration=dur,
        regionCode="CA",
        relevanceLanguage="en"
    )
    response = request.execute()

    try:

        # collect data on search results
        for video in response['items']:
            VIDEO_ID = video['id']['videoId']

            # for each video, request more video information about each video result. Return true if added to database
            if makeRequestVideos(search_q, VIDEO_ID, youtube, dur):
                # for each video, request more comment information about each video result
                makeRequestCommentThread(VIDEO_ID, youtube)

    except IndexError as e:
        print("Index error in MakeRequestVideoList:", e)
    except Exception as e:
        print("Exception in makeRequestVideoList:", e)


def search(search_q):
    """
    call method makeRequestVideoList using the search query parameter
    as the search subject as well as an extension ("", " tutorial", " explain")
    to expand search results.
    Defines the length of the video to be searched (ie short, medium, long)

    :param search_q: string which is the search query for YouTube API
        to obtain videos on that subject
    :type search_q: string

    :returns: void
    """

    makeRequestVideoList(search_q, "short")
    makeRequestVideoList(search_q, "medium")
    makeRequestVideoList(search_q, "long")
