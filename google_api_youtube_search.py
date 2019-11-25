# @Marlie Russell 2019 | YouTube Recommender

# Expanded from sample Python code for youtube.search.list and youtube.statistics.list
# https://developers.google.com/explorer-help/guides/code_samples#python
import psycopg2
import os
import googleapiclient.discovery
from connectDb import connect

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


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


# search for video statistics and data
def makeRequestVideos(searchSubject,videoID, youtube, cursor, connection, dur):
    # Form request parameter
    request = youtube.videos().list(
        part="statistics, snippet",
        id = videoID
        )
   
    try:
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
        URL = "https://youtube.com/watch?v=" + videoID

        # query to see if video is already in db. If yes, update stats, if no, insert
        cursor.execute("""SELECT * FROM video WHERE v_id = %s;""", (videoID,))
        if (cursor.fetchone() is not None):
            cursor.execute(
                """UPDATE video SET likes = %s, dislikes = %s,
                fav_count = %s, com_count = %s, channel_id = %s,
                channel_name = %s, "searchQ" = %s, duration = %s,
                url = %s WHERE v_id = %s""",
                (LIKES,DISLIKES,FAV,COMMENTS, CHAN_ID,CHAN_TITLE,
                searchSubject,dur, URL, videoID))
            connection.commit()
            #print("Updated Video table")
           
        else:
            cursor.execute(
                    """INSERT INTO video
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                    (TITLE, DESCRP, VIEWS, LIKES, DISLIKES, FAV,
                     COMMENTS, videoID, CHAN_ID, CHAN_TITLE,
                     searchSubject,dur, URL))
            connection.commit()
            print("Inserted into Video Table")
    
    except KeyError as e:
        print ("key error:", e)
    except Exception as e:
        print("Exception in MakeVideoRequest:", e)


# retrieve comment threads for a video
def makeRequestCommentThread(VIDEO_ID, youtube, cursor, connection):
    request = youtube.commentThreads().list(
        part="id,snippet",
        videoId=VIDEO_ID,
    )

    try:
        response = request.execute()
        for comment in response['items']:
            c_id = comment['snippet']['topLevelComment']['id']
            author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            text = comment['snippet']['topLevelComment']['snippet']['textOriginal']
            likes = comment['snippet']['topLevelComment']['snippet']['likeCount']
            published_at = comment['snippet']['topLevelComment']['snippet']['publishedAt']
            updated_at = comment['snippet']['topLevelComment']['snippet']['updatedAt']

            cursor.execute("""SELECT * FROM comments WHERE c_id = %s;""", (c_id,))
            if (cursor.fetchone() is not None):
                cursor.execute(
                    """UPDATE comments SET text = %s, likes = %s,
                    updated_at = %s WHERE c_id = %s""",
                    (text,likes,updated_at, c_id))
                connection.commit()
                #print("Updated Comment in data base")
               
            else:
                cursor.execute(
                        """INSERT INTO comments
                        VALUES(%s,%s,%s,%s,%s,%s,%s);""",
                        (c_id, text, likes, author,
                         VIDEO_ID, published_at,
                         updated_at))
                connection.commit()
                print("Inserted Comment into database")
            
    except KeyError as e:
        print("key error:", e)
    except IndexError as e:
        print("Index error in MakeRequestCommentThreads:", e)
    except TypeError as e:
        print ("type error:", e)
    except googleapiclient.errors.HttpError as e:
        print("Comments disabled:", e)
    except Exception as e:
        print("Exception in makeRequestCommentThreads", e)
        
       
# search for video results
def makeRequestVideoList(searchSubject,dur):
        youtube = credentialVerification()
        request = youtube.search().list(
            part="snippet,id",
            q=searchSubject,
            type="video",
            maxResults=50,
            videoDuration=dur,
        )
        response = request.execute()
        cursor, connection = connect()

        try:
        # collect data on search results
            for video in response['items']:
                VIDEO_ID = video['id']['videoId']

                #for each video, request more video information
                makeRequestVideos(searchSubject,VIDEO_ID,
                                  youtube,cursor,connection,dur)
                makeRequestCommentThread(VIDEO_ID, youtube,cursor,connection)
        
        except IndexError as e:
            print("Index error in MakeRequestVideoList:", e)
        except Exception as e:
            print("Exception in makeRequestVideoList:", e)
        
        finally:
            closeConnection(connection,cursor)
        


def search(searchQ):
    makeRequestVideoList(searchQ,"short")
    makeRequestVideoList(searchQ + " tutorial","short")
    makeRequestVideoList(searchQ + " explain","short")
    makeRequestVideoList(searchQ,"medium")
    makeRequestVideoList(searchQ+ " explain","medium")
    makeRequestVideoList(searchQ + " tutorial","medium")
    makeRequestVideoList(searchQ,"long")
    makeRequestVideoList(searchQ +" explain","long")
    makeRequestVideoList(searchQ + " tutorial","long")
    
def main():
# run program to output titles of YouTube videos
    search("binary tree")

if __name__ == "__main__":
    main()
