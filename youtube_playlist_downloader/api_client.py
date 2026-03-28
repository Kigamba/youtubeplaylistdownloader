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
"""This module is responsible for providing ApiClient class."""

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import google.auth.exceptions
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

MAX_FETCH_RESULTS = 50
NEXT_PAGE_TOKEN = "nextPageToken"
ITEMS = "items"


class ApiClient:
    """Api client responsible to communicate with YouTube"""

    def __init__(self):
        self.api_resource = None
        self.credentials = None

    def initialize(self, credentials):
        """Creates API resource"""
        self.credentials = credentials
        self.api_resource = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials,
            cache_discovery=False  # recommended in newer versions
        )

    def fetch_credentials(self, client_secret_file, token_file="token.pkl"):
        """
        Fetches and caches user credentials
        """

        creds = None

        # Load saved credentials
        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                creds = pickle.load(token)

        # If no valid creds, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except google.auth.exceptions.RefreshError:
                    creds = None

            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_file, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def fetch_user_playlists(self, next_page_token=None):
        """Fetches playlists for authenticated user"""
        result = self.api_resource.playlists().list(
            part='snippet,contentDetails,player,status',
            mine=True,
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token
        ).execute()

        return self.get_items_and_next_page_token(result)

    def fetch_videos_of_playlist(self, playlist_id, next_page_token=None):
        """Fetches videos in a playlist"""
        result = self.api_resource.playlistItems().list(
            part='snippet,contentDetails,status',
            playlistId=playlist_id,
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token
        ).execute()

        return self.get_items_and_next_page_token(result)

    @staticmethod
    def get_items_and_next_page_token(result):
        return result.get(ITEMS, []), result.get(NEXT_PAGE_TOKEN)
