# Freesound Remote Player

This repository contains a server and simple cli tool to play Freesound sounds from your terminal.
Both the server and the client are implemented in Python.

## Running the server (`server.py`)

The server is a [Flask](http://flask.pocoo.org) application and uses [pydub](https://github.com/jiaaro/pydub) for playing audio. You can install these requirements with:

```
pip install pydub Flask
```

In order to play audio, `pydub` depends on either ffmpeg or libav.
Please check the [instructions](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up) on `pydub`repository for installing these dependencies. Should be as simple as `apt-get install libav-tools libavcodec-extra-53` or similar.

The server needs to be configured before running using environment variables:

 * `FS_API_KEY`: Freesound api key (request one at https://freesound.org/apiv2/apply)
 * `PORT` (optional): Port where the server will be listening

You can export variables and start the server in a single command:

```
export FS_API_KEY="YOUR_KEY"; python server.py
```


## Running the client (`freesound-cli-player.py`)

This script will accepts a number of arguments and makes a request to the remote player server.
`freesound-cli-player.py` can be distributed separately from the server and has no python requirements.
For the client to work `HOST` and `PORT` must be configured and point to a reachable Freesound Remote Player server.

Example usage:
```
python freesound-cli-player dogs barking
```
