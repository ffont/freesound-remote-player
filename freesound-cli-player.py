import sys
import urllib
import json
from optparse import OptionParser

DEFAULT_HOST = '10.80.26.190'
DEFAULT_PORT = 3333

usage = """python freesound-cli-player.py [<options>] [<command>] [<args>]

Available commands:
    id     Play Freesound sound with the id provided as argument
    tags   Play Freesound sound with tags provided as arguments
    read   Use system's 'say' command to read the text provided as arguments
    stop   Stop all things being played in ther remote server

If no command is provided, 'tags' is taken by default.
Example usage:
> python freesound-cli-player.py tags dogs barking
> python freesound-cli-player.py tags dogs,barking
> python freesound-cli-player.py id 1234
> python freesound-cli-player.py read this will read the text in arguments
> python freesound-cli-player.py read "quoted text will also be read"
> python freesound-cli-player.py stop
> python freesound-cli-player.py dogs barking"""

parser = OptionParser(usage=usage)
parser.add_option("-H", "--host", dest="host",
                  help="Host of the remote server, defaults to %s" % DEFAULT_HOST, default=DEFAULT_HOST)
parser.add_option("-P", "--port", dest="port",
                  help="Port of the remote server, defaults to %s" % DEFAULT_PORT, default=DEFAULT_PORT)

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    if len(args) == 0:
        # No arguments and no command (command is first argument)
        parser.print_help()
        sys.exit()
    elif len(args) == 1:
        command = args[0]
        arguments = []
    else:
        command = args[0]
        arguments = args[1:]

    base_url = 'http://%s:%i/' % (options.host, options.port)

    def send_request(url):
        print url
        response = urllib.urlopen(url)
        print json.loads(response.read())
        print ''

    def run_stop(arguments):
        url = base_url + 'panic'
        send_request(url)

    def run_tags(arguments):
        tags = ','.join(arguments)
        url = base_url + 'play?tags=' + tags
        send_request(url)

    def run_id(arguments):
        fsid = arguments[0]
        url = base_url + 'play?fsid=' + fsid
        send_request(url)

    def run_read(arguments):
        url = base_url + 'voice?text="%s"' % ' '.join(arguments)
        send_request(url)

    available_commands = [element.replace('run_', '') for element in dir() if element.startswith('run_')]
    if command in available_commands:
        locals()['run_%s' % command](arguments)
    else:
        # There is no valid command, use default command 'tags' and assume command is omitted
        # Also reassign command to arguments are there is no command
        arguments = [command] + arguments
        run_tags(arguments)
