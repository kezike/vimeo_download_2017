from urllib2 import Request, urlopen, URLError, HTTPError
# from urllib3 import
from retry import retry
import re

class VideoDownloader(object):
    # included these variables up here only
    # because retry cannot access 'self'
    num_tries = 1
    timeout = 0.01
    backoff = 2
    def __init__(self, vid_url, num_thr=5, par_thresh=50, to=0.01, bo=2, num_try=5):
        # regex for recognizing file urls
        url_regex_match = re.match("^http(s)?://([a-zA-Z0-9\-\.]+/)+[a-zA-Z0-9\-\.]+$", vid_url)
        if not url_regex_match:
            raise Exception("Invalid video url!")
        split_url = vid_url.split('/')
        self.file_name = split_url[-1]
        # url of video source file
        self.video_url = vid_url
        # number of threads avaialable for download
        self.num_threads = num_thr
        # min size in MB of file necessary
        # for parallel download
        self.parallel_threshold = par_thresh
        # connection timeout period
        self.timeout = to
        timeout = to
        # exponential backoff on subsequent timeout periods
        self.backoff = bo
        backoff = bo
        # number of times to try connection before retiring
        self.num_tries = num_try
        num_tries = num_try
        # ordered chunks of file downloaded
        self.chunks = []

    @retry(URLError, tries=num_tries, delay=timeout, backoff=backoff)
    def urlopen_retry(self):
        return urllib2.urlopen(self.vid_url)
    
    # connect to the server
    def connect_server(self):
        # check if server supports byte-range get request
        headers = {"Range": "bytes"}
        server_req = Request(self.video_url, None, headers)
        try:
            server_resp = urlopen(server_req)
        except HTTPError as err:
            print "Sorry, the server could not execute your request!"
            print "Error code:", err.code
            print "Attempting to reconnect you to the server..."
            self.urlopen_retry()
        except URLError as err:
            print "Sorry, we could not connect you to a server!"
            print "Error reason:", err.reason
            print "Attempting to reconnect you to the server..."
            self.urlopen_retry()
        return server_resp

    # download video in one serial request
    def download_video_ser(self):
        server_resp = self.connect_server()
        if type(server_resp) == HTTPError:
            print "Sorry, the server could not execute your request!"
            print "Error code:", server_resp.code
        elif type(server_resp) == URLError:
            print "Sorry, we could not connect you to a server!"
            print "Error reason:", server_resp.reason
        else:
            print "Downloading " + self.file_name + "..."
            file_obj = open(self.file_name, 'a')
            file_obj.write(server_resp.read())
            file_obj.close()
            print "Successfully downloaded " + self.file_name + '!'
    
    # download video in parallel requests
    def download_video_par(self):
        # TODO: parallelize this logic
        print "Downloading " + self.file_name + "..."
        file_obj = open(self.file_name, 'a')
        file_obj.write(server_resp.read())
        file_obj.close()
        print "Successfully downloaded " + self.file_name + '!'
        pass

    # inspect data about the server and download video
    def download_video(self):
        server_resp = self.connect_server()
        if type(server_resp) == HTTPError:
            print "Sorry, the server could not execute your request!"
            print "Error code:", server_resp.code
        elif type(server_resp) == URLError:
            print "Sorry, we could not connect you to a server!"
            print "Error reason:", server_resp.reason
        else:
            server_meta = server_resp.info()
            if "Accept-Rangesdewkjnf" in server_meta:
                if server_meta["Accept-Ranges"] == "bytes":
                    # download multiple chunks of video source file in parallel
                    self.download_video_par()
                else:
                    self.download_video_ser()
            else:
                # download entire video source file in one serial request
                self.download_video_ser()
        # print server_meta
        # print "Accept-Ranges:", server_meta["Accept-Ranges"]

vid_dl = VideoDownloader("https://storage.googleapis.com/vimeo-test/work-at-vimeo-2.mp4")
vid_dl.download_video()
