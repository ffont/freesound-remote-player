import sys
import urllib
import json

HOST = '10.80.26.190'
PORT = 3333
BASE_URL = 'http://%s:%i/' % (HOST, PORT)
PLAY_URL = BASE_URL + 'play'

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args):
        tags = ','.join(args)
        url = PLAY_URL + '?tags=' + tags
        response = urllib.urlopen(url)
        print json.loads(response.read())
