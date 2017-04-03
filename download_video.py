from video_dl import VideoDownloader

video_url = raw_input("Please enter the url of your video source file:\n")
vid_dl = VideoDownloader(video_url)
vid_dl.download_video()
