from flask import Flask, request, jsonify
import urllib2
import os
import random
import multiprocessing
import subprocess
import pydub
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import get_player_name
import tempfile
from freesound import FreesoundClient

DATA_DIR = os.path.join(os.getcwd(), 'audio')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


running_voice_processes = list()
running_sound_processes = list()


# monkeypath pydub's _play_with_ffplay so we can store process objects
# Without that we could not stop processes when calling panic
def _my_play_with_ffplay(seg):
    tmp = tempfile.NamedTemporaryFile("w+b", suffix=".wav", delete=False)
    seg.export(tmp.name, "wav")
    proc = subprocess.Popen([get_player_name(), "-nodisp", "-autoexit", tmp.name])
    running_sound_processes.append(proc)
pydub.playback._play_with_ffplay = _my_play_with_ffplay


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

def search_from_id(fsid):
    id_filter = 'id:%s' % fsid
    results_pager = fs_client.text_search(filter=id_filter,fields="id,previews")
    if results_pager.results:
        # Should only have one result...
        s = random.choice(results_pager.results)
        return s['previews']['preview-hq-ogg']
    return None

def play_file(path):
    song = AudioSegment.from_ogg(path)
    play(song)
    #p = multiprocessing.Process(target=play, args=(song,), kwargs={})
    #running_sound_processes.append(p)
    #p.start()

@app.route("/play")
def play_from_freesound():
    tags = request.args.get('tags', None)
    if tags is not None:
        url = search_from_tags(tags)
        if url is not None:
            path = download_file(url)
            play_file(path)
            return jsonify({'playing': True, 'url': url})
    fsid = request.args.get('fsid', None)
    if fsid is not None:
        url = search_from_id(fsid)
        if url is not None:
            path = download_file(url)
            play_file(path)
            return jsonify({'playing': True, 'url': url})

    return jsonify({'playing': False})

# The following endpoint has nothing to do with Freesound but it is fun ;)
@app.route("/voice")
def render_text():
    text = request.args.get('text', None)
    voice = request.args.get('voice', 'Fred')
    proc = subprocess.Popen(["say", "-v", voice] + text.split(' '))
    running_voice_processes.append(proc)
    return jsonify({'playing': True, 'text': text, 'voice': voice})

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
            <br>Alternatively specify the id of the sound with the 'id' request parameter (e.g. '?id=1234').
        </li>
        <li style="margin-bottom: 10px;">
            <b>/voice</b>: call the system's command 'say' to <i>say</i> whatever you want.
            <br>Use the request parameter `text` to specify the text to be said (e.g. `?text="this is really stupid"`)
            <br>Use the request parameter `voice` to specify a voice to be used to read the text (e.g. `?voice="Agnes"`).
            List of <a href="https://github.com/ffont/freesound-remote-player/issues/1">available voices</a>.
            <br>NOTE: this endpoint has nothing to do with Freesound but it is fun
        </li>
        <li style="margin-bottom: 10px;">
            <b>/panic</b>: Stop all sounds being played
        </li>
    </ul>
    <p>
    Contribute to the server here: <a href="https://github.com/ffont/freesound-remote-player">https://github.com/ffont/freesound-remote-player</a>
    </p>
    """

@app.route("/panic")
def panic():
    global running_voice_processes
    global running_sound_processes
    for p in running_voice_processes:
        p.kill()
    for p in running_sound_processes:
        p.kill()
    response = {
        'n_voice_processes_killed': len(running_voice_processes),
        'n_sound_processes_killed': len(running_sound_processes)
    }
    running_voice_processes = list()
    running_sound_processes = list()
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 3333)))
