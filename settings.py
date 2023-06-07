PATH = r"./downloads"
URLS_PATH = "./urls.txt"
HIGHEST_RESOLUTION = "1080"
AUDIO_BITRATE = "192"
MODE = "both"  # video, audio, both

AUDIO_FORMAT = None   # None for best
VIDEO_FORMAT = None  # None for best
RESULT_FORMAT = "mp4"
CODEC = "h264_nvenc"    # best for nvidia gpu

CACHE = "./cache"
CREATE_FOLDER_FOR_PLAYLIST = True
SKIP_EXISTING_VIDEOS = True
REMOVE_UNFINISHED_DOWNLOADS = True

THREADS = None  # None for auto
PRESET = "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo

BASIC_OPTIONS = {
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': True,
    'quiet': True,
    "no_warnings": True,
    "verbose": False,
    # "cookiefile": "cookies.txt",
}
