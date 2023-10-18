import logging
import os
import sys
import random
import re

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%d-%m-%Y %H:%M:%S'
)

try:
    from yt_dlp import YoutubeDL
except ImportError:
    logging.error("yt-dlp not installed! Please install it with pip.")
    sys.exit()

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    logging.error("moviepy not installed! Please install it with pip.")
    sys.exit()

try:
    from settings import *
except ImportError:
    logging.error("settings.py not found! Please create it in the same directory as main.py.")
    sys.exit()

if DOWNLOAD_ON_THREADS:
    import threading
    import time


class VideoDownloader:
    def __init__(self,
                 url,
                 auto_run=True,
                 video_info=None,
                 path=PATH,
                 mode=MODE,
                 highest_resolution=HIGHEST_RESOLUTION,
                 audio_bitrate=AUDIO_BITRATE,
                 audio_format=AUDIO_FORMAT,
                 video_format=VIDEO_FORMAT,
                 result_format=RESULT_FORMAT,
                 cache=CACHE,
                 create_folder_for_playlist=CREATE_FOLDER_FOR_PLAYLIST,
                 skip_existing_videos=SKIP_EXISTING_VIDEOS,
                 codec=CODEC,
                 preset=PRESET,
                 basic_options=BASIC_OPTIONS,
                 threads=THREADS,
                 start_of_title="",
                 download_on_threads = DOWNLOAD_ON_THREADS,
                 download_thread_timeout = TIMEOUT_FOR_THREADS
                ):
        self.id = random.randint(0, 1000000)
        self.path = path
        self.start_of_title = start_of_title
        self.mode = mode

        self.download_on_threads = download_on_threads
        self.download_thread_timeout = download_thread_timeout
        self.downloading_video = False
        self.downloading_audio = False

        self.started_merging = False

        self.highest_resolution = highest_resolution
        self.audio_bitrate = audio_bitrate

        self.audio_format = audio_format
        self.video_format = video_format
        self.result_format = result_format

        self.cache = cache
        self.create_folder_for_playlist = create_folder_for_playlist
        self.skip_existing_videos = skip_existing_videos

        self.codec = codec
        self.preset = preset
        self.threads = threads

        self._video_file = None

        self.basic_options = basic_options

        self.url = url
        if video_info is None:
            with YoutubeDL(BASIC_OPTIONS) as ydl:
                self.video_info = ydl.extract_info(self.url, download=False)
        else:
            self.video_info = video_info

        if auto_run:
            self.run()

    def run(self):
        logging.info(f"     -> Downloading video \"{self.start_of_title + self.video_info['title']}\" ({self.url})...")
        if self.skip_existing_videos:
            if os.path.exists(os.path.join(self.path, re.sub(r"[\\/:*?\"<>|]", "", self.start_of_title + self.video_info['title']) + '.mp4')):
                logging.info("          -> Video already exists! Skipping...")
                return
        if self.mode == "both":
            self.download_both()
        elif self.mode == "video":
            logging.info("          -> Downloading only video...")
            self.download_video(path=self.path)
        elif self.mode == "audio":
            logging.info("          -> Downloading only audio...")
            self.download_audio(path=self.path)

    def download_both(self):
        self.started_merging = False
        self.download()
        self.merge()

    def exit(self):
        logging.info(f"     -> Exiting video \"{self.start_of_title + self.video_info['title']}\" ({self.url})...")
        if self._video_file is not None:
            self._video_file.close()
            self._video_file = None
        if self.started_merging and REMOVE_UNFINISHED_DOWNLOADS:
            logging.info(f"          -> Video \"{self.start_of_title + self.video_info['title']}\" unfinished! Removing...")
            os.remove(os.path.join(self.path, re.sub(r"[\\/:*?\"<>|]", "", self.start_of_title + self.video_info['title']) + '.mp4'))
        logging.info("          -> Video exit complete!")

    def download(self):
        logging.info("          -> Downloading video...")
        if self.download_on_threads:
            self.video_download_thread = threading.Thread(target=self.download_video)
            self.video_download_thread.start()
            logging.info("                  > Started the thread for video download...")
        else:
            self.download_video()
        logging.info("          -> Downloading audio...")
        if self.download_on_threads:
            self.audio_download_thread = threading.Thread(target=self.download_audio)
            self.audio_download_thread.start()
            logging.info("                  > Started the thread for audio download...")
        else:
            self.download_audio()
        
        if self.download_on_threads:
            if not self.wait_until(lambda: not self.downloading_video and not self.downloading_audio, self.download_thread_timeout):
                logging.error(f"Thread to download timed out: Video finished: {not self.downloading_video}; Audio finished: {not self.downloading_audio}")
                logging.warning("If this error keeps occouring try to change the DOWNLOAD_THREAD_TIMEOUT variable")
                raise
            else:
                logging.info("                  ✓ Both threads finished succesfully")

    def download_video(self, path=None):
        self.downloading_video = True
        options = self.basic_options.copy()
        options["format"] = f"bestvideo[height<=?{self.highest_resolution}]"
        if self.video_format is not None:
            options["postprocessors"] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': self.video_format,
            }]
        options["outtmpl"] = f"{self.cache if path is None else path}/{self.start_of_title + self.format_title(self.video_info['title'])}{f'.video{self.id}' if path is None else '' }.%(ext)s"
        with YoutubeDL(options) as ydl:
            ydl._ies = {"Youtube": ydl.get_info_extractor('Youtube')}
            ydl.download([self.url])
            self.downloading_video = False
            logging.info("              ✓ Video download complete!")

    def download_audio(self, path=None):
        self.downloading_audio = True
        options = BASIC_OPTIONS
        options["format"] = f"bestaudio[abr<=?{self.audio_bitrate}]"
        if self.video_format is not None:
            options["postprocessors"] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
                'preferredquality': self.audio_bitrate,
            }]
        options["outtmpl"] = f"{CACHE if path is None else path}/{self.self.start_of_title + self.format_title(self.video_info['title'])}{f'.audio{self.id}' if path is None else ''}.%(ext)s"
        with YoutubeDL(options) as ydl:
            ydl._ies = {"Youtube": ydl.get_info_extractor('Youtube')}
            ydl.download([self.url])
            self.downloading_audio = False
            logging.info("              ✓ Audio download complete!")

    def format_title(self, title):
        return re.sub(r"[\\/:*?\"<>|]", "", title)

    def get_file(self, identifier):
        for file in os.listdir(CACHE):
            if identifier in file:
                return file
        return None

    def merge(self):
        logging.info("          -> Merging video and audio...")
        self._video_file = VideoFileClip(os.path.join(self.cache, self.get_file(f".video{self.id}.")))
        self._video_file.audio = AudioFileClip(os.path.join(self.cache, self.get_file(f".audio{self.id}.")))
        path = os.path.join(self.path, re.sub(r"[\\/:*?\"<>|]", "", self.start_of_title + self.video_info['title']) + "." + self.result_format)
        temp_path = os.path.join(self.cache, re.sub(r"[\\/:*?\"<>|]", "", self.start_of_title + self.video_info['title']) + "." + (self.audio_format if self.audio_format else "mp3"))
        self.started_merging = True
        self._video_file.write_videofile(path, codec=self.codec, logger=None, preset=self.preset, threads=self.threads, temp_audiofile=temp_path)
        logging.info("              ✓ Merge complete!")
        self._video_file.close()
        self._video_file = None
        self.started_merging = False
        os.remove(os.path.join(self.cache, self.get_file(f".video{self.id}.")))
        os.remove(os.path.join(self.cache, self.get_file(f".audio{self.id}.")))
        logging.info("          ✓ Temporary files removed!")

    def wait_until(self, somepredicate, timeout, period=0.25, *args, **kwargs):
        mustend = time.time() + timeout
        while time.time() < mustend:
            if somepredicate(*args, **kwargs): 
                return True
            time.sleep(period)
        return False


class PlaylistDownloader:
    def __init__(
            self, 
            url, 
            auto_run=True, 
            playlist_info=None, 
            number_the_videos_in_playlist=NUMBER_THE_VIDEOS_IN_PLAYLIST
        ):
        self.url = url
        if playlist_info is None:
            with YoutubeDL(BASIC_OPTIONS) as ydl:
                self.playlist_info = ydl.extract_info(self.url, download=False)
        else:
            self.playlist_info = playlist_info

        self.number_the_videos_in_playlist = number_the_videos_in_playlist
        self.videos = self.get_videos()
        self.current_video = None

        if auto_run:
            self.run()

    def exit(self):
        logging.info(f" -> Exiting Playlist {self.playlist_info['title']} ({self.url})...")
        if self.current_video is not None:
            self.current_video.exit()
        logging.info("  -> Playlist exit complete!")

    def get_videos(self):
        videos = []
        if CREATE_FOLDER_FOR_PLAYLIST:
            path = os.path.join(PATH, re.sub(r"[\\/:*?\"<>|]", "", self.playlist_info['title']))
        else:
            path = PATH
        for index, video in enumerate(self.playlist_info['entries']):
            if video is None:
                logging.warning(" -> Video is None! Skipping...")
                continue
            videos.append(VideoDownloader(video['webpage_url'], auto_run=False, video_info=video, path=path, start_of_title=f"{index + 1} - " if self.number_the_videos_in_playlist else ""))

        return videos

    def run(self):
        logging.info(f" -> Downloading playlist {self.playlist_info['title']} ({self.url})...")
        if CREATE_FOLDER_FOR_PLAYLIST and not os.path.exists(os.path.join(PATH, re.sub(r"[\\/:*?\"<>|]", "", self.playlist_info['title']))):
            path = os.path.join(PATH, re.sub(r"[\\/:*?\"<>|]", "", self.playlist_info['title']))
            os.mkdir(path)
            logging.info(f"     -> Created folder {path} for playlist!")
        for video in self.videos:
            self.current_video = video
            video.run()
        logging.info(" -> Playlist download complete!")


class DownloadManager:
    def __init__(self, url_file, auto_run=True):
        self.url_file = url_file

        self.check_errors()
        self.warn()

        self.urls = self.get_urls()
        self.classified_objects = self.classify_urls()
        self.current_object = None

        if auto_run:
            self.run()

    def check_errors(self):
        if not os.path.exists(PATH):
            raise NotADirectoryError(f"Path {PATH} does not exist! Please make sure the path is correct!")
        if not os.path.isfile(self.url_file):
            raise FileNotFoundError(f"Url file {self.url_file} does not exist! Please make sure the url file is correct!")

    def warn(self):
        if not "cookiefile" in BASIC_OPTIONS.keys() or not os.path.isfile(BASIC_OPTIONS["cookiefile"]):
            logging.warning("No cookies file found or set in the BASIC OPTIONS! This may cause problems with downloading some videos!")
        if not os.path.exists(CACHE):
            logging.warning(f"No cache folder found! Creating cache folder at {CACHE} ...")
            os.mkdir(CACHE)

    def classify_urls(self):
        logging.info("=> Classifying urls...")
        classified_url_elements = []
        for url in self.urls:
            with YoutubeDL(BASIC_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                if "_type" in info.keys() and info["_type"] == "playlist":
                    classified_url_elements.append(PlaylistDownloader(url, auto_run=False, playlist_info=info))
                    logging.info(f"  + Playlist \"{info['title']}\" with {len(info['entries'])} videos found!")
                else:
                    classified_url_elements.append(VideoDownloader(url, auto_run=False, video_info=info))
                    logging.info(f"  - Video \"{info['title']}\" found!")
        return classified_url_elements

    def exit(self):
        logging.info("=> Exiting...")
        if self.current_object is not None:
            self.current_object.exit()
            self.clear_cache()
            for file in os.listdir("."):
                if file.endswith(".mp3"):
                    os.remove(file)
        logging.info("=> Exit complete!")

    def run(self):
        logging.info("=> Starting downloads...")
        for element in self.classified_objects:
            self.clear_cache()
            self.current_object = element
            element.run()
        logging.info("=> Downloads complete!")

    def clear_cache(self):
        for file in os.listdir(CACHE):
            os.remove(os.path.join(CACHE, file))
    logging.debug("              -> Cache cleared!")

    def get_urls(self):
        urls = []
        with open(self.url_file, "r") as file:
            for line in file.readlines():
                if line.strip() != "":
                    if not line.strip().startswith("#"):
                        urls.append(line.strip())
                    else:
                        logging.info(f"- Skipping line \"{line.strip().removeprefix('#')}\"")
        return urls


if __name__ == "__main__":
    downloader = DownloadManager(URLS_FILE, auto_run=False)
    try:
        downloader.run()
    except KeyboardInterrupt:
        downloader.exit()
        sys.exit(0)
