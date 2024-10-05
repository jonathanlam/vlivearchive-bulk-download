import logging, threading
import concurrent.futures
from main import *

BOARD_ID = 8527 # Jo Yuri
DOWNLOAD_DIR = "joyuri"

def process_object(vliveVideoId):
    # Define the function you want to run on each object here
    thread_name = threading.current_thread().name
    os.makedirs(f"{DOWNLOAD_DIR}/{thread_name}", exist_ok=True)
    
    #logging.info(f"Processing video {obj} on thread {thread_name}")

    print(f"{bcolors.WARNING}{vliveVideoId}{bcolors.ENDC}")
    video = Video(vliveVideoId)
    video.set_download_dir(f"{DOWNLOAD_DIR}/{thread_name}")
    video.download()
    # video.download(folder=f"{DOWNLOAD_DIR}/{thread_name}")
    

def process_objects(objects, max_workers=10):
    # Create a logger for each thread
    loggers = {}
    for i in range(max_workers):
        logger = logging.getLogger(f"thread-{i}")
        logger.setLevel(logging.INFO)
        loggers[i] = logger

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_object, obj) for obj in objects]

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                result = future.result()
            except Exception as exc:
                loggers[i % max_workers].error(f"Exception: {exc}", exc_info=True)
            else:
                loggers[i % max_workers].info(f"Finished processing object {i} on thread {threading.current_thread().name}")

   
if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    url = f"https://api.vlivearchive.com/board/{BOARD_ID}"
    req = requests.get(url)
    
    # get list of all video ids on the channel
    videoIds = [video['officialVideo']['videoSeq'] for video in req.json()['posts']]
    print(videoIds)

    # get list of all video ids that have not been downloaded yet
    videoIdsToDownload = [videoId for videoId in videoIds if not os.path.exists(os.path.join(DOWNLOAD_DIR, f"{videoId}.mp4"))]
    print(videoIdsToDownload)

    # download the videos in parallel
    process_objects(videoIdsToDownload)