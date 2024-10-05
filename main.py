import os, requests, json, zipfile, time
import time

DOWNLOAD_DIR = "downloads" # you can change this to the name of the channel
QUEUE_FILE = "queue.json"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

drive_file_id_mapping = json.load(open("file_id_mapping.json", encoding="utf-8"))

class Video:

    def __init__(self, id: str):
        self.id = id
        file = f"{id}.mp4"
        self._download_dir = DOWNLOAD_DIR
        if file in drive_file_id_mapping:
            self.drive_file_id = drive_file_id_mapping[file]
            self._in_drive = True
        else:
            self._in_drive = False

    def set_download_dir(self, download_dir):
        self._download_dir = download_dir

    def download(self):
        if self._in_drive:
            req = Takeout(self.drive_file_id)
            req.download_file(folder=self._download_dir)
            req.unzip(folder=self._download_dir)
        else:
            # print(f"{bcolors.FAIL}Video {self.id} not found in drive_file_id_mapping.{bcolors.ENDC}")
            url = f"https://api.vlivearchive.com/download/{self.id}.mp4"
            print(bcolors.OKGREEN + url + bcolors.ENDC)
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(f"{self._download_dir}/{self.id}.mp4", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

class Takeout:
    def __init__(self, drive_file_id):
        self._drive_file_id = drive_file_id
    
    def download_file(self, folder=DOWNLOAD_DIR):
        job_id = self._create_zip(self._drive_file_id)
        print(f"{bcolors.OKCYAN}File {self._drive_file_id}, Job {job_id}{bcolors.ENDC}")
        archive = self._check_status(job_id)
        if archive is None:
            print(f"{bcolors.FAIL}Creating ZIP failed.{bcolors.ENDC}")
            return

        url = archive['storagePath']
        filename = archive['fileName']
        #sizeOfContents = int(archive['sizeOfContents'])
        #if sizeOfContents > 4000000000:
        #    print("file too large, skipping")
        #    return

        print(bcolors.OKGREEN + url + bcolors.ENDC)

        # download file from url with default file name
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(f"{folder}/{filename}", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    def _create_zip(self, drive_file_id: str) -> str:
        # creates a zip file containing the file with id drive_file_id
        # Returns the job ID
        url = "https://takeout-pa.clients6.google.com/v1/exports?key=AIzaSyD_InbmSFufIEps5UAt2NmB_3LvBH3Sz_8"
        payload = {"archiveFormat": None,
                   "archivePrefix": "drive-download",
                   "conversions": None,
                   "items": [{"id": drive_file_id}],
                   "locale": None}

        r = requests.post(url, json=payload)
        r = json.loads(r.text)
        return r['exportJob']['id']


    def _check_status(self, job_id):
        # checks the status on the export every 5 seconds
        # and returns the archive when done
        url = "https://takeout-pa.clients6.google.com/v1/exports/" + \
            job_id + "?key=AIzaSyD_InbmSFufIEps5UAt2NmB_3LvBH3Sz_8"

        try:
            r = requests.get(url)
        except:
            print(f"{bcolors.FAIL}Request failed. Retrying...{bcolors.ENDC}")
            time.sleep(5)
            return self._check_status(job_id)

        r = json.loads(r.text)

        if 'exportJob' not in r:
            time.sleep(5)
            return self._check_status(job_id)

        if r['exportJob']['status'] == "FAILED":
            return None

        if r['exportJob']['status'] == "SUCCEEDED":
            return r['exportJob']['archives'][0]
        else:
            print(r['exportJob']['status'], end=" ", flush=True)
            time.sleep(5)
            return self._check_status(job_id)

    def unzip(self, folder=DOWNLOAD_DIR):
        for item in os.listdir(folder):
            if item.endswith(".zip"):
                try:
                    zip_ref = zipfile.ZipFile(f"{folder}/{item}")
                    zip_ref.extractall(folder)
                    zip_ref.close()
                    os.remove(f"{folder}/{item}")
                except:
                    print(f"{bcolors.FAIL}{item} not a zip file or is corrupted/incomplete download{bcolors.ENDC}")
                
    def rename_files(self, folder=DOWNLOAD_DIR):
        for item in os.listdir(folder):
            if "[" not in item:
                # video is already renamed
                continue
        
            if item.endswith(".mp4"):
                videoSeq = getVidSeq(item)
                os.rename(f"{folder}/{item}", f"{folder}/{videoSeq}.mp4")
            else:
                print(f"{bcolors.FAIL}{item} is not an mp4 file{bcolors.ENDC}")

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    vid = Video(267577)
    vid.download()
        
if __name__ == "__main__":
    main()