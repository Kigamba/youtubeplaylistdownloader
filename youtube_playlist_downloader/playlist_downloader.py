# Copyright 2020 Krunal Soni
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module provides classes to use ApiClient and provides final object.

It provides Playlist and PlaylistSet classes to store fechted results.
PlaylistDownloader communicates with YouTube with ApiClient and returns
final result to the caller.
"""
import base64
import os
import pickle


class Playlist:
    """Stores playlist data"""

    VIDEOS_KEY = "videos"
    """Key used to associate with list of videos"""
    def __init__(self, json_object):
        """Creates instance from provided playlist data

        Args:
            json_object (`dict`): Playlist fetched from YouTube api
        """
        self._json_object = json_object[1]
        self._json_object[Playlist.VIDEOS_KEY] = []

    def add_video_json_object(self, video_json_object):
        """Adds video data to the list of videos

        Args:
            video_json_object (`dict`): Video data fetched from YouTube api
        """
        self._json_object[Playlist.VIDEOS_KEY].append(video_json_object)

    def get_id(self):
        """Gets id associated with playlist

        Returns:
            [`str`]: Playlist id
        """
        return self._json_object['id']

    def get_json_object(self):
        """Gets associated playlist object that could be encoded to json

        Returns:
            `dict`: Dictionary object with playlist and its associated videos.
        """
        return self._json_object


class PlaylistSet:
    """Stores multiple playlists"""
    def __init__(self):
        """Creates empty set of playlists"""
        self._json_object = []

    def add_playlist(self, playlist):
        """Adds a playlist

        Args:
            playlist (`Playlist`): Playlist object
        """
        self._json_object.append(playlist.get_json_object())

    def get_json_object(self):
        """Gets associated list of playlists

        Returns:
            `list`: List of playlists
        """
        return self._json_object


class PlaylistDownloader:
    """Downloads playlists for a user using supplied ApiClient."""
    def __init__(self, api_client):
        """Initializes with supplied api client.

        Args:
            api_client (`ApiClient`): Client to use to communicate with YouTube
        """
        self.api_client = api_client

    @staticmethod
    def _load_credentials(filename):
        credentials = None
        if os.path.isfile(filename):
            with open(filename, "rb") as f:
                serialized = f.read()
            prep = base64.b64decode(serialized)
            credentials = pickle.loads(prep)
        return credentials

    @staticmethod
    def _save_credentials(filename, credentials):
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        prep = pickle.dumps(credentials)
        # Store it with base64 econding to easily allow transferring as text
        serialized = base64.b64encode(prep)
        with open(filename, "wb") as f:
            f.write(serialized)

    def _authenticate(self, client_secret_file, profile, credential_file,
                      force_authenticate):
        return self._ensure_credentials(client_secret_file, credential_file,
                                        force_authenticate)

    def _ensure_credentials(
            self,
            client_secret_file,
            credential_file,
            force_authenticate,
    ):
        credentials = None
        if not force_authenticate:
            credentials = self._load_credentials(credential_file)

        if credentials is None:
            credentials = self._fetch_and_save_credentials(
                client_secret_file, credential_file)

        return credentials

    def _fetch_and_save_credentials(self, client_secret_file, credential_file):
        credentials = self.api_client.fetch_credentials(client_secret_file)
        self._save_credentials(credential_file, credentials)
        return credentials

    def _add_videos_to_playlist(self, playlist):
        next_page_token = None
        while True:
            partial_items, next_page_token = self.api_client.fetch_videos_of_playlist(
                playlist.get_id(), next_page_token)
            for video_json_object in enumerate(partial_items):
                playlist.add_video_json_object(video_json_object)
            if next_page_token is None:
                break

    def _fetch_user_playlists(self):
        user_playlists = PlaylistSet()
        next_page_token = None
        while True:
            partial_items, next_page_token = self.api_client.fetch_user_playlists(
                next_page_token)
            for item in enumerate(partial_items):
                playlist = Playlist(item)
                self._add_videos_to_playlist(playlist)
                user_playlists.add_playlist(playlist)
            if next_page_token is None:
                break
        return user_playlists.get_json_object()

    def download_playlists(self, client_secret_file, profile, credential_file,
                           force_authenticate):
        """Downloads playlists using credentials for given profile

        Downloads playlists for the user associated with supplied credentials.
        If credentials do not exist or authentication is forced, user is
        authenticated first and new credentials are fetched and stored.

        Args:
            profile (`str`): Profile name associated with credentials

            client_secret_file (`str`): Path to client secret associated
                with the app

            credential_file (`str`): File to read/write credentials

            force_authenticate (`bool`): Authenticates regardless of existence
                of credentialsisCI = os.environ.get('CI')
        if isCI == "true"

        Returns:
            `list`: List of playlist data with simple datatypes that could
                be simply encoded to json
        """
        credentials = self._authenticate(client_secret_file, profile,
                                         credential_file, force_authenticate)
        self.api_client.initialize(credentials)
        return self._fetch_user_playlists()
