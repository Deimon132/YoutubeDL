# Youtube DL - Download Youtube Videos at highest quality
> Youtube DL is a tool that allows you to download Youtube videos at the highest quality possible.

This involves downloading video and audio separately and then combining them into a single file.
Since the best downloadable audio-video combination is only 720p,
videos with higher resolutions can also be downloaded.

## Installation
1. Download this repository as a zip file and extract it.
2. Install the required packages using `pip install yt-dlp moviepy`
3. Add the urls of the videos you want to download in the `urls.txt` file.
    - The `urls.txt` file has to have the path specified in the settings.py file.
      - default path is `./urls.txt`
    - Each url has to be on a new line.
    - You can also comment out lines by adding a `#` at the beginning of the line.
      - Example: `# https://www.youtube.com/watch?v=dQw4w9WgXcQ`
    - You can also download playlists by adding the playlist url.
4. Run the `main.py` file.
5. The videos will be downloaded in the `./downloads` folder.
    - The path can be changed in the settings.py file.
      - default path is `./downloads`

## Settings
The settings can be changed in the `settings.py` file.
- `PATH` - The path to download the videos to.
- `URLS_PATH` - The path to the urls file.
- `HIGHEST_RESOLUTION` - The highest resolution to download the videos in. If the video is not available in this resolution, the next highest resolution will be downloaded.
- `AUDIO_BITRATE` - The bitrate of the audio to download. The higher the bitrate, the better the audio quality.
- `MODE` - The downloading mode. Can be `audio`, `video` or `both`.
  - `audio` - Only the audio will be downloaded.
  - `video` - Only the video will be downloaded.
  - `both` - Both the audio and video will be downloaded and then combined into a single file.
- `AUDIO_FORMAT` - The audio format to download the audio in. None for automatic selection. Setting this might lower the quality of the audio.
- `VIDEO_FORMAT` - The video format to download the video in. None for automatic selection. Setting this might lower the quality of the video.
- `RESULT_FORMAT` - The format to combine the audio and video into.
- `CODEC` - The codec to use to combine the audio and video.
- `CHACHE` - The path to the cache folder. This is used to store the downloaded audio and video files. Before merging the audio and video. This has to be an empty folder, since all files in it are deleted.
- `CREATE_FOLDER_FOR_PLAYLIST` - Whether to create a folder for each playlist or not.
- `SKIP_EXISTING_VIDEOS` - Whether to skip the videos that have already been downloaded or not.
- `REMOVE_UNFINISHED_DOWNLOADS` - Whether to remove the videos that were not downloaded completely when the program was stopped or not.
- `THREADS` - The number of threads to use to download the videos. Higher number of threads will download the videos faster, but will also use more resources. None for automatic selection.
- `PRESET` - The preset to use to combine the audio and video. Higher presets will take longer to combine, but will also result in a smaller file size. More information about presets can be found [here](https://trac.ffmpeg.org/wiki/Encode/H.264#a2.Chooseapresetandtune).
- `BASIC_OPTIONS` - The basic yt-dl options to use to download the videos.

## Tips
- To ensure that the videos can be downloaded, add a `cookies.txt` file in the root directory of the project.
  - You can get the cookies.txt file using the [Get cookies.txt LOCALLY extension](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) for chrome on YouTube while logged in to your YouTube account.