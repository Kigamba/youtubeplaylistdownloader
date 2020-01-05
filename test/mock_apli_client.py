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


class MockApiClient:
    MAX_RESULTS = 5
    RESULTS_PER_FETCH = 2
    CREDENTIALS = "test_credentials"

    def __init__(self):
        pass

    def initialize(self, credentials):
        pass

    def fetch_credentials(self, client_secret_file):
        return self.CREDENTIALS

    def _create_playlist(self, next_page_token):
        return {
            "id": next_page_token,
            "snippet": {
                "title": "testtite"
            },
            "contentDetails": {
                "itemCount": 1
            }
        }

    def _create_video(self, next_page_token):
        return {"id": next_page_token, "snippet": {"title": "testvideotitle"}}

    def _fetch_results(self, next_page_token, is_playlist):
        if (next_page_token is None):
            next_page_token = 0

        results = []
        for i in range(self.RESULTS_PER_FETCH):
            if (next_page_token < self.MAX_RESULTS):
                if is_playlist is True:
                    results.append(self._create_playlist(next_page_token))
                else:
                    results.append(self._create_video(next_page_token))
                next_page_token += 1

        if (next_page_token >= self.MAX_RESULTS):
            next_page_token = None

        return results, next_page_token

    def fetch_user_playlists(self, next_page_token):
        return self._fetch_results(next_page_token, True)

    def fetch_videos_of_playlist(self, playlist_id, next_page_token):
        return self._fetch_results(next_page_token, False)
