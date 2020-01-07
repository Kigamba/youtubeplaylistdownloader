# YouTube Playlist Downloader

This package provides a script to download YouTube playlists for a user.
It has been tested with both *CPython* and *PyPy*.

To use it, you will need to have access to OAuth 2.0 client credentials 
for Google developer project. You can follow *Before You Start* section in
[Getting Started](https://developers.google.com/youtube/v3/getting-started)
page. Once your project is created, create OAuth 2.0 client credentials
in [console](https://console.developers.google.com/apis/credentials).
Download *\*.json* file and use it as a *secretfile* positional argument
at command line. The command by default saves user OAuth tokens in `credentials`
 folder in the working directory. Next time when the script runs from that directory,
reauthentication is not necessary for corresponding profile,
unless `--force` option is used.
Credential folder can also be provided with `-e` option.
Credential file path could also be provided with `c` option,
and that will override other options.

Here are few commands you can:
```bash
youtube_playlist_downloader -h # For help
youtube_playlist_downloader \
    --profile joe4939 \
    --outfolder myplaylists \
    --format json \
    --format default \
    my_app_client_secret.json
```

## Installation
```bash
pip install youtube-playlist-downloader
```
