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

import json

import pytest

from youtube_playlist_downloader import main
from youtube_playlist_downloader.playlist_downloader import (Playlist,
                                                             PlaylistDownloader
                                                             )

from .mock_apli_client import MockApiClient

CLIENT_SECRET_SAMPLE_FILE = ("secret/client_secret.json.sample")
TEST_PROFILE = "pytest"


class TestClass:
    def create_format_list(self, defaultformat=False, jsonformat=False):
        list = []
        if defaultformat is True:
            list.append(main.DEFAULT_FORMAT)
        if jsonformat is True:
            list.append(main.JSON_FORMAT)
        return list

    @pytest.mark.parametrize(
        "arguments",
        [["--profile"], ["--profile", " "], ["--format", "invalidformat"],
         ["invalidsecretfile"], None])
    def test_get_parsed_args_system_exit_2(self, arguments):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main._get_parsed_args(arguments)
        self.assert_system_exit_status(pytest_wrapped_e, 2)

    @pytest.mark.parametrize(
        "arguments",
        [[
            '-f', '-p', 'test', '-o', 'testout', '--format', 'json',
            CLIENT_SECRET_SAMPLE_FILE
        ],
         [
             '--profile', 'test', '--force', '--outfolder', 'testout',
             '--format', 'json', CLIENT_SECRET_SAMPLE_FILE
         ]])
    def test_get_parsed_args_valid(self, arguments):
        args = main._get_parsed_args(arguments)
        assert args.profile == "test"
        assert args.force
        assert args.outfolder == "testout"
        assert args.format == self.create_format_list(jsonformat=True)

    def test_get_parsed_args_default(self):
        args = main._get_parsed_args([CLIENT_SECRET_SAMPLE_FILE])
        assert args.profile == "default"
        assert not args.force
        assert args.outfolder == main.OUT_FOLDER
        assert args.format == self.create_format_list(defaultformat=True)

    def test_get_parsed_multiple_formats(self):
        args = main._get_parsed_args([
            '--format', 'default', '--format', 'json',
            CLIENT_SECRET_SAMPLE_FILE
        ])
        assert args.profile == "default"
        assert not args.force
        assert args.outfolder == main.OUT_FOLDER
        assert args.format == self.create_format_list(defaultformat=True,
                                                      jsonformat=True)

    def assert_system_exit_status(self, e, status):
        assert e.type == SystemExit
        assert e.value.code == status

    def test_write_playlists_to_file_valid(self, tmpdir):
        outfileprefix = str(tmpdir.join("testFile"))
        jsonobj = [{
            "id":
            "testid",
            "snippet": {
                "title": "testtite"
            },
            "contentDetails": {
                "itemCount": 1
            },
            "videos": [[
                0, {
                    "id": "testvideoid",
                    "snippet": {
                        "title": "testvideotitle"
                    }
                }
            ]]
        }]
        main._write_playlist_files(
            jsonobj, outfileprefix,
            self.create_format_list(defaultformat=True, jsonformat=True))
        with open(main._get_json_filename(outfileprefix), "r") as read_file:
            data = json.load(read_file)
            assert data == jsonobj
        with open(main._get_default_filename(outfileprefix), "r") as read_file:
            data = read_file.readlines()
            assert data[
                0] == 'Playlist Title: testtite, Id: testid, Count: 1\n'
            assert data[
                2] == 'Index: 0, Id: testvideoid, Video Title: "testvideotitle"\n'

    def test_write_playlists_to_file_invalid_json(self, tmpdir, capsys):
        outfile = str(tmpdir.join("testFile"))
        main._write_playlist_files(object(), outfile,
                                   self.create_format_list(jsonformat=True))
        captured = capsys.readouterr()
        assert captured.err.startswith("Exception")

    def test_get_output_filename_valid(self, tmpdir):
        fileprefix = main.get_output_filepath_prefix("test", str(tmpdir))
        assert "test" in fileprefix
        assert fileprefix.endswith(main._get_today())

    def assert_credentials_and_playlist(self, outfolder):
        credentials = PlaylistDownloader._load_credentials(
            PlaylistDownloader._get_filename(TEST_PROFILE))
        assert credentials == MockApiClient.CREDENTIALS

        outfileprefix = main.get_output_filepath_prefix(
            TEST_PROFILE, outfolder)
        with open(main._get_json_filename(outfileprefix), "r") as infile:
            json_object = json.load(infile)
            for playlist in json_object:
                assert len(playlist.get(
                    Playlist.VIDEOS_KEY)) == MockApiClient.MAX_RESULTS

        with open(main._get_default_filename(outfileprefix), "r") as infile:
            obj = infile.readlines()
            assert len(obj) > MockApiClient.MAX_RESULTS

    def test_main(self, tmpdir):
        downloader = PlaylistDownloader(MockApiClient())
        secretfile = str(tmpdir.join("secretfile"))
        with open(secretfile, 'w'):
            pass
        outfolder = str(tmpdir)
        options = [
            "--profile", TEST_PROFILE, "-o", outfolder, "--format", "default",
            "--format", "json", secretfile
        ]
        main._main(downloader, options)
        self.assert_credentials_and_playlist(outfolder)

        options.insert(0, "-f")
        main._main(downloader, options)
        self.assert_credentials_and_playlist(outfolder)
