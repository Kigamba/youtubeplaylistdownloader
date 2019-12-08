''' Authenticate user and use YouTube API to fetch user playlists. '''

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__),
                                   'resources/client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Credentials are stored for future once user gives permission to access
# their account
CREDENTIAL_FILE_EXT = '.credentials'
CREDENTIAL_FOLDER = "credentials/"

MAX_FETCH_RESULTS = 20
NEXT_PAGE_TOKEN = "nextPageToken"
ITEMS = "items"


class Playlist:
    VIDEOS_KEY = "videos"

    def __init__(self, json_object):
        self._json_object = json_object[1]
        self._json_object[Playlist.VIDEOS_KEY] = []

    def add_video_json_object(self, video_json_object):
        self._json_object[Playlist.VIDEOS_KEY].append(video_json_object)

    def get_id(self):
        return self._json_object['id']

    def get_json_object(self):
        return self._json_object


class PlaylistSet:
    def __init__(self):
        self._json_object = []

    def add_playlist(self, playlist):
        self._json_object.append(playlist.get_json_object())

    def get_json_object(self):
        return self._json_object


def add_videos_to_playlist(youtube, playlist):
    next_page_token = None
    while True:
        result = youtube.playlistItems().list(
            part='snippet,contentDetails,status',
            playlistId=playlist.get_id(),
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token).execute()
        partial_items = result[ITEMS]
        for video_json_object in enumerate(partial_items):
            playlist.add_video_json_object(video_json_object)

        next_page_token = result.get(NEXT_PAGE_TOKEN)
        if next_page_token is None:
            break


def get_authenticated_service(profile, reauthenticate):
    credentials = None
    file_name = CREDENTIAL_FOLDER + profile + CREDENTIAL_FILE_EXT
    if os.path.isfile(file_name):
        credentials = pickle.load(open(file_name, "rb"))
    if not credentials or reauthenticate:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()
        pickle.dump(credentials, open(file_name, "wb"))

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def fetch_user_playlists(youtube):
    user_playlists = PlaylistSet()
    next_page_token = None
    while True:
        result = youtube.playlists().list(
            part='snippet,contentDetails,player,status',
            mine=True,
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token).execute()
        partial_items = result[ITEMS]
        for item in enumerate(partial_items):
            playlist = Playlist(item)
            add_videos_to_playlist(youtube, playlist)
            user_playlists.add_playlist(playlist)

        next_page_token = result.get(NEXT_PAGE_TOKEN)
        if next_page_token is None:
            break
    return user_playlists.get_json_object()


def download_user_playlists(profile, reauthenticate):
    youtube = get_authenticated_service(profile, reauthenticate)
    return fetch_user_playlists(youtube)
