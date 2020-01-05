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

import pytest

from youtube_playlist_downloader.playlist_downloader import PlaylistDownloader

from .mock_apli_client import MockApiClient


class TestPlaylistDownloader:
    @pytest.fixture
    def playlist_downloader(self):
        return PlaylistDownloader(MockApiClient())

    @pytest.mark.parametrize("credentials", [MockApiClient.CREDENTIALS, None])
    def test_save_load_credentials(self, tmpdir, playlist_downloader,
                                   credentials):
        testfile = str(tmpdir.join("testFile"))
        playlist_downloader._save_credentials(testfile, credentials)
        assert playlist_downloader._load_credentials(testfile) == credentials

    def test_load_credentials_from_nonexistent_file(self, tmpdir,
                                                    playlist_downloader):
        testfile = str(tmpdir.join("testFile"))
        assert playlist_downloader._load_credentials(testfile) is None

    def test_fetch_and_save_credentials(self, tmpdir, playlist_downloader):
        testfile = str(tmpdir.join("testFile"))
        credentials = playlist_downloader._fetch_and_save_credentials(
            None, testfile)
        assert credentials == MockApiClient.CREDENTIALS
        playlist_downloader._load_credentials(
            testfile) == MockApiClient.CREDENTIALS

    def test_ensure_credentials_existing(self, tmpdir, playlist_downloader):
        testfile = str(tmpdir.join("testFile"))
        playlist_downloader._save_credentials(testfile, "specific_credentials")
        assert playlist_downloader._ensure_credentials(
            None, testfile, False) == "specific_credentials"

    def test_ensure_credentials_force_authenticate(self, tmpdir,
                                                   playlist_downloader):
        testfile = str(tmpdir.join("testFile"))
        playlist_downloader._save_credentials(testfile, "specific_credentials")
        assert playlist_downloader._ensure_credentials(
            None, testfile, True) == MockApiClient.CREDENTIALS

    def test_ensure_credentials_non_existing(self, tmpdir,
                                             playlist_downloader):
        testfile = str(tmpdir.join("testFile"))
        assert playlist_downloader._ensure_credentials(
            None, testfile, False) == MockApiClient.CREDENTIALS
