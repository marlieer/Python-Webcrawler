from video_collection_and_processing import collect_and_process_videos
from util import connect
from rating_matrix import beginRating


def main():
    cursor, connection = connect()
    #
    # cursor.execute("SELECT search_q from searchlist;")
    # results = cursor.fetchall()
    #
    # for result in results:
    #     print(result[0])
    #     collect_and_process_videos(result[0])

    # collect_and_process_videos("Queues")
    # collect_and_process_videos("lambda expressions")
    #
    # beginRating()


if __name__ == "__main__":
    main()
