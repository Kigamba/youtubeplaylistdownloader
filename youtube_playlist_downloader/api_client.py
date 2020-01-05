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

SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

MAX_FETCH_RESULTS = 20
NEXT_PAGE_TOKEN = "nextPageToken"
ITEMS = "items"


class ApiClient:
    """Api client responsible to communicate with YouTube"""
    def __init__(self):
        self.api_resource = None

    def initialize(self, credentials):
        """Creates api resource to communicate with YouTube.

        Args:
            credentials (`oauth2client.Credentials` or
                `google.auth.credentials.Credentials`): Credentials used to
                with api
        """
        self.api_resource = build(API_SERVICE_NAME,
                                  API_VERSION,
                                  credentials=credentials)

    def fetch_credentials(self, client_secret_file):
        """Fetches credentials by authenticate a user.

        Args:
            client_secret_file (`str`): File to client secret associated
                with the app. File contains the OAuth 2.0 information for
                the application, including its client_id and client_secret.
        Returns:
            `oauth2client.Credentials` or
                `google.auth.credentials.Credentials`: Credentials to be used
        """

        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file, SCOPES)
        return flow.run_console()

    def fetch_user_playlists(self, next_page_token):
        """Fetches playlists for a user from given page token

        Args:
            next_page_token (`str`): Page token being used to fetch limited
                results in batch

        Returns:
        [`tuple` (`list`, `str`)]: Tuple of list of items and next page token
            to fetch more results. None if all results are fetched.
        """
        result = self.api_resource.playlists().list(
            part='snippet,contentDetails,player,status',
            mine=True,
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token).execute()
        return self.get_items_and_next_page_token(result)

    """Fetches data for videos for given playlist id and page token

    Returns:
        [`tuple` (`list`, `str`)]: Tuple of list of items and next page token
            to fetch more results. None if all results are fetched.
    """
    def fetch_videos_of_playlist(self, playlist_id, next_page_token):
        result = self.api_resource.playlistItems().list(
            part='snippet,contentDetails,status',
            playlistId=playlist_id,
            maxResults=MAX_FETCH_RESULTS,
            pageToken=next_page_token).execute()
        return self.get_items_and_next_page_token(result)

    @staticmethod
    def get_items_and_next_page_token(result):
        return result[ITEMS], result.get(NEXT_PAGE_TOKEN)
