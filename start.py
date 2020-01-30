from video_collection_and_processing import collect_and_process_videos
from compute_video_similarity import compute_cosine_similarity
import requests
import json


# get modules for a particular course
def getModules(course_id, token):
    try:
        url = "https://canvas.ubc.ca/api/v1/courses/{}/modules?include=items&access_token={}".format(course_id, token)

        response = requests.get(url)

        items = []
        # append module item names to list
        if response.status_code == 200:
            for module in response.json():
                for item in module['items']:
                    items.append(item['title'])

        return items

    except Exception as e:
        print("Exception in getModules: ", e)


def main():
    with open('settings.sample.json', 'r') as settings:
        data = settings.read()
        obj = json.loads(data)
    items = getModules(obj['course_id'], obj['token'])

    for item in items:
        collect_and_process_videos(item)
        compute_cosine_similarity(item)
        # print(item)


if __name__ == "__main__":
    main()
