from video_collection_and_processing import collect_and_process_videos
from compute_video_similarity import compute_cosine_similarity
from util import connect


def main():
    cursor, connection = connect()

    cursor.execute("SELECT search_q from searchlist;")
    results = cursor.fetchall()

    for result in results:
        print(result[0])
        collect_and_process_videos(result)
        compute_cosine_similarity(result)


if __name__ == "__main__":
    main()
