from flask import Flask, request, jsonify
import urllib2
import os
import random
import threading
from pydub import AudioSegment
from pydub.playback import play
from freesound import FreesoundClient

DATA_DIR = os.path.join(os.getcwd(), 'audio')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

fs_client = FreesoundClient()
api_key = os.getenv('FS_API_KEY', None)
if api_key is None:
    raise Exception('Enviornment variable FS_API_KEY not defined')
fs_client.set_token(api_key, "token")
app = Flask(__name__)

def get_fsid_from_url(url):
    return url.split('/')[-1].split('_')[0]

def download_file(url):
    sid = get_fsid_from_url(url)
    out_filename = '%s.ogg' % sid
    out_path = os.path.join(DATA_DIR, out_filename)
    if not os.path.exists(out_path):
        audiofile = urllib2.urlopen(url)
        with open(out_path,'wb') as output:
          output.write(audiofile.read())
    return out_path

def search_from_tags(tags):
    tags_filter = ' '.join(['tag:%s' % tag for tag in tags.split(',')])
    results_pager = fs_client.text_search(filter=tags_filter  + " duration:[1.0 TO 10.0]",fields="id,previews")
    if results_pager.results:
        s = random.choice(results_pager.results)
        return s['previews']['preview-hq-ogg']
    return None

def play_file(path, threaded=True):
    song = AudioSegment.from_ogg(path)
    if threaded:
        t = threading.Thread(target=play, args=(song,), kwargs={})
        t.start()
    else:
        play(song)

@app.route("/play")
def play_from_freesound():
    tags = request.args.get('tags', None)
    if tags is not None:
        url = search_from_tags(tags)
        if url is not None:
            path = download_file(url)
            play_file(path)
            return jsonify({'playing': True, 'url': url})
    return jsonify({'playing': False})

# The following endpoint has nothing to do with Freesound but it is fun ;)
@app.route("/voice")
def render_text():
    def run_say(text):
        os.system("say %s" % text)
    text = request.args.get('text', None)
    t = threading.Thread(target=run_say, args=(text,), kwargs={})
    t.start()
    return jsonify({'playing': True, 'text': text})

@app.route("/")
def docs():
    return """
    <h1>Freesound Remote Player API docs</h1>
    Hi, this is what you can do:
    <ul>
        <li style="margin-bottom: 10px;">
            <b>/</b>: This is where you are
        </li>
        <li style="margin-bottom: 10px;">
            <b>/play</b>: play a sound from Freesound.
            <br>Specify the tags that the sound must have using the 'tags' request parameter and separating the tags
            with commas (e.g. '?tags=hello,speech').
        </li>
        <li style="margin-bottom: 10px;">
            <b>/voice</b>: call the system's command 'say' to <i>say</i> whatever you want.
            <br>User the request parameter `text` to spacify the text to be said (e.g. `?text="this is really stupid"`)
            <br>NOTE: this endpoint has nothing to do with Freesound but it is fun
        </li>
    </ul>
    """

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv('PORT', 3333)))
