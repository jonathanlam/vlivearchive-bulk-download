import logging, threading
import concurrent.futures
from main import *

MISSING_VIDEOS_REPORT = "missing_itzy.json"
DOWNLOAD_DIR = "itzy"

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
    report = open(MISSING_VIDEOS_REPORT, "r", encoding="utf-8")
    report = json.load(report)

    # get list of all video ids that have not been downloaded yet
    videoIdsToDownload = [videoId.split(".")[0] for videoId in report.keys()]
    print(videoIdsToDownload)

    # download the videos in parallel
    process_objects(videoIdsToDownload)