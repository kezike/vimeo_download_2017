import urllib2

# Inspects data about server
def inspect_server(server_url):
  video_response = urllib2.urlopen(server_url)
  video = video_response.read()
  # perhaps return tuple of server data
  return None

def download_video(file_path):
  (server_url, video_file) = file_path.split()
  server_report = inspect_server(server_url)
