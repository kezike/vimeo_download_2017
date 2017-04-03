from urllib2 import Request, urlopen, URLError, HTTPError
from urllib3 import HTTPConnectionPool, HTTPSConnectionPool
import urllib3.connectionpool as conn_pool
from retry import retry
import re

class VideoDownloader(object):
    # included these variables up here only
    # because retry cannot access 'self'
    num_tries = 1
    timeout = 0.01
    backoff = 2
    def __init__(self, vid_url, num_thr=5, par_thresh=2000000, to=0.01, bo=2, num_try=5, fp_thresh=200000000):
        # regex for recognizing file urls
        url_regex_match = re.match("^http(s)?://([a-zA-Z0-9\-\.]+/)+[a-zA-Z0-9\-\.]+$", vid_url)
        if not url_regex_match:
            raise Exception("Invalid video url format!")
        split_url = vid_url.split('/')
        self.file_name = split_url[-1]
        # url of video source file
        self.video_url = vid_url
        # number of threads avaialable for download
        self.num_threads = num_thr
        # min size in bytes of file necessary
        # for partial download requests
        self.partial_thresh = par_thresh
        # connection timeout period
        self.timeout = to
        timeout = to
        # exponential backoff on subsequent timeout periods
        self.backoff = bo
        backoff = bo
        # number of times to try connection before retiring
        self.num_tries = num_try
        num_tries = num_try
        # download data size (bytes) threshold before file persistance
        self.file_persist_thresh = fp_thresh
        # ordered chunks of file downloaded
        self.chunks = []
        # request header
        self.headers = {"Range": "bytes"}
        # response header field for video content size
        self.content_size_field = "x-goog-stored-content-length"
        # video content size (to be set during server info request)
        self.content_size = None

    @retry(URLError, tries=num_tries, delay=timeout, backoff=backoff)
    def urlopen_retry(self):
        return urllib2.urlopen(self.video_url)
    
    # connect to the server
    def connect_server(self):
        # check if server supports byte-range get request
        server_req = Request(self.video_url, None, self.headers)
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
        # expect connect_server to raise exception where necessary
        server_resp = self.connect_server()
        print "Beginning serial download of " + self.file_name + "..."
        file_obj = open(self.file_name, 'a')
        file_obj.write(server_resp.read())
        file_obj.close()
        print "Successfully downloaded " + self.file_name + '!'
    
    # intermediately write downloaded chunks to file
    def file_persist(self):
        file_obj = open(self.file_name, 'a')
        [file_obj.write(chunk) for chunk in self.chunks]
        self.chunks = []
        file_obj.close()

    # download video in partial requests
    def download_video_par(self):
        print "Beginning partial download requests for " + self.file_name + "..."
        server_req = Request(self.video_url)
        range_min = 0
        range_max = self.partial_thresh - 1
        chunk_num = 0
        cumulative_data_size = 0
        data_size_since_last_persist = 0
        while range_max - range_min > 0:
            server_req.headers['Range'] = 'bytes=%s-%s' % (range_min, range_max)
            server_resp = urlopen(server_req)
            num_bytes_retrieved = server_resp.headers.get('Content-Range')
            self.chunks.append(server_resp.read())
            cumulative_data_size += range_max - range_min
            data_size_since_last_persist += range_max - range_min
            range_min = min(range_min + self.partial_thresh, self.content_size)
            range_max = min(range_max + self.partial_thresh, self.content_size)
            if data_size_since_last_persist >= self.file_persist_thresh:
                print "Intermediately writing downloaded data to " + self.file_name + "..."
                self.file_persist()
                data_size_since_last_persist = 0
                download_progress = cumulative_data_size * 100.0 / float(self.content_size)
                print "Download progress: " + str(download_progress) + '%'
                print "Continuing download..."
        self.file_persist()
        print "Successfully downloaded " + self.file_name + '!'

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
            self.content_size = int(server_meta[self.content_size_field])
            if "Accept-Ranges" in server_meta:
                if server_meta["Accept-Ranges"] == "bytes" and self.content_size >= self.partial_thresh:
                    # download multiple chunks of video source file in partial requests
                    self.download_video_par()
                else:
                    self.download_video_ser()
            else:
                # download entire video source file in one serial request
                self.download_video_ser()
