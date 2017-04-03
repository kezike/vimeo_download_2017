Vimeo Video Download Challenge

Problem Description
Vimeo typically provides users with the feature of downloading the original source file of uploaded videos. This project is an experimental solution to a bug in this feature; namely, that Vimeo can only provide the url of video source files. The task is to restore this feature in an ad hoc solution that enables users to download a video source file given a source url hosting the file.

VideoDownloader API
Constrtuctor Parameters:
- vid_url = url of video source file (REQUIRED)
- num_thr = number of threads avaialable for download (OPTIONAL)
- par_thresh = min size in bytes of file necessary for partial download requests (OPTIONAL)
- to = connection timeout period in seconds (OPTIONAL)
- bo = exponential backoff on subsequent timeout periods (OPTIONAL)
- num_try = number of times to try connection before retiring (OPTIONAL)
- fp_thresh = download data size (bytes) threshold before file persistance (OPTIONAL)

Methods:
- urlopen_retry(URLError, tries, delay, backoff):
  - Specification: Retry server connection some specified number of times after a timeout period that exponentially builds up over time
  - Parameters:
    - tries = number of times to try connection before resigning connection attempts
    - delay = amount of time (in seconds) to wait between connection attempts
    - backoff = multiplicative factor of delay between subsequent connection attempts

- connect_server()
  - Specification: Connect to the server to which the video url points; raises HTTPError and URLError for failed connection attempts

- download_video_atom()
  - Specification: Download video in one atomic request

- download_video_par()
  - Specification: Download video in partial requests

- download_video()
  - Specification: Inspect data about the server and download video source file; decides whether to call download_video_atom() or download_video_par() based on size of video file and capability for server to download service partial requests

System Use
Here are the steps for using the VideoDownloader to download a video source file given its URL:
- Run "python download_video.py" in the command line
- When prompted, enter a valid url for the video source file of interest.
- If everything is working correctly, you will receive progress information during download.
- When download is complete, the video file will be downloaded in the working directory in the name at the suffix of the provided URL.
- Enjoy your video!
