import json
import os
import requests

BOARD_ID = 5745 # Itzy
DOWNLOAD_DIR = "itzy"

drive_file_id_mapping = open("file_id_mapping.json", "r", encoding="utf-8")
drive_file_id_mapping = json.load(drive_file_id_mapping)

def missing_video_list():
    url = f"https://api.vlivearchive.com/board/{BOARD_ID}"
    response = requests.get(url)
    data = response.json()
    
    expected_videos = [post['officialVideo']['videoSeq'] for post in data['posts']]
    missing_videos = []
    
    for video_id in expected_videos:
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
        if not os.path.exists(file_path):
            missing_videos.append(video_id)
    
    return missing_videos

if __name__ == "__main__":
    missing_videos = missing_video_list()
    if len(missing_videos) == 0:
        print("No missing videos found")
        exit()

    missing_videos_report = {}
    for video_id in missing_videos:
        file_key = f"{video_id}.mp4"
        if file_key in drive_file_id_mapping:
            missing_videos_report[file_key] = drive_file_id_mapping[file_key]
        else:
            print(f"File {file_key} not found in drive_file_id_mapping")

    report_filename = f"missing_{DOWNLOAD_DIR}.json"
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        json.dump(missing_videos_report, report_file, ensure_ascii=False, indent=4)
    print(f"Missing videos: {missing_videos_report}")
