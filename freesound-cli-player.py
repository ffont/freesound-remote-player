import sys
import urllib
import json

HOST = '10.80.26.190'
PORT = 3333
BASE_URL = 'http://%s:%i/' % (HOST, PORT)
PLAY_URL = BASE_URL + 'play'
VOICE_URL = BASE_URL + 'voice'
PANIC_URL = BASE_URL + 'panic'

"""
TODO: this should really be turned into a proper command line app
For now you can either:
    python freesound-cli-player.py tag1 tag2 tag3
or:
    python freesound-cli-player.py tag1,tag2,tag3
for playing a random sound from Freesound with the given tags...

or you can also
    python freesound-cli-player.py read a text you want to be read
to use system's 'say' command to read something. So basically if first argument is
'read' then instead of playing a Freesound sound the server will read the folloing arguments...

or you can also stop all playing things
    python freesound-cli-player.py stop
"""

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args):
        if args[0] == 'read':
            # Read following arguments
            url = VOICE_URL + '?text="%s"' % ' '.join(args[1:])
        elif args[0] == 'stop':
            # Stop all things
            url = PANIC_URL
        else:
            # Play fs sound with tags
            tags = ','.join(args)
            url = PLAY_URL + '?tags=' + tags
        print url
        response = urllib.urlopen(url)
        print json.loads(response.read())
        print ''
