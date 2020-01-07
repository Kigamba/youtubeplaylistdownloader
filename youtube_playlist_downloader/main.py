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
"""Provides functions to process command line arguments and execute."""

import argparse
import datetime
import json
import os
import sys

from .api_client import ApiClient
from .playlist_downloader import PlaylistDownloader

OUT_FOLDER = "out"
JSON_FORMAT = "json"
DEFAULT_FORMAT = "default"
JSON_FILE_EXT = '.playlists.json'
DEFAULT_FILE_EXT = ".playlists.txt"

CLIENT_SECRETS_FILE = 'secret/client_secret.json'

# Credentials are stored for future once user gives permission to access
# their account
CREDENTIAL_FILE_EXT = '.credential'
CREDENTIAL_FOLDER = "credentials"


def _non_empty_arg(arg):
    if arg.strip() == "":
        msg = "%s is an empty string" % arg
        raise argparse.ArgumentTypeError(msg)
    return arg


def _secretfile_arg(arg):
    arg = _non_empty_arg(arg)
    if (not os.path.isfile(arg)):
        msg = "%s file does not exist" % arg
        raise argparse.ArgumentTypeError(msg)
    return arg


def _get_parsed_args(args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--force',
        default=False,
        action='store_true',
        help=('Authenticate even if previous credentials exist for ' +
              'associated profile.'))

    parser.add_argument(
        '-p',
        '--profile',
        help=(
            'Provide profile name to associate with credentials and output ' +
            'files. This is useful for downloading playlists for multiple ' +
            'google accounts. Defaults to \'%(default)s\'.'),
        default='default',
        type=_non_empty_arg)

    parser.add_argument('-o',
                        '--outfolder',
                        help=('Provide folder path to write output files to.' +
                              'Defaults to \'%(default)s\'.'),
                        default=OUT_FOLDER,
                        type=_non_empty_arg)

    parser.add_argument(
        '-e',
        '--credentialfolder',
        help=('Provide folder path to read/write credential files. ' +
              "If '-c' is provided, this argument is ignored. "
              'Defaults to \'%(default)s\'.'),
        default=CREDENTIAL_FOLDER,
        type=_non_empty_arg)

    parser.add_argument('-c',
                        '--credential',
                        help=('Provide path to read/write credential file. ' +
                              'Defaults to \'%(default)s\'.'),
                        type=_non_empty_arg)

    parser.add_argument(
        '--format',
        help=('Provide output format. ' +
              'You can provide multiple formats by repeating this option. ' +
              'Defaults to [\'default\'].'),
        default=[],
        choices=["default", "json"],
        action='append')

    parser.add_argument(
        'secretfile',
        help=('Provide path to client secret file downloaded from "API and ' +
              'Services" for your app on Google Developer Console. ' +
              'Defaults to \'%(default)s\' for development.'),
        nargs='?',
        default=CLIENT_SECRETS_FILE,
        type=_secretfile_arg)

    parsed_args = parser.parse_args(args)

    if (len(parsed_args.format) == 0):
        parsed_args.format.append(DEFAULT_FORMAT)

    return parsed_args


def fetch_playlists(playlist_downloader, client_secret_file, profile,
                    credential_folder, credential_file, force_authenticate):
    """Fetches playlists object with provided profile and downloader.

    Args:
        playlist_downloader(`PlaylistDownloader`): Downloader used
            to fetch user playlists

        client_secret_file (`str`): Path to client secret associated
            with the app

        profile(`str`): Profile name to associate with credentials

        credential_folder (`str`): Folder to store credentials

        credential_file (`str`): File to store credentials

        force_authenticate(`bool`): Perform authentication even though
            credentials exist

    Returns:
        list: List of playlist results which are composed of simple data types
            so they can be simply encoded to json
    """

    credential_file = _get_credential_filename(profile, credential_folder,
                                               credential_file)

    try:
        return playlist_downloader.download_playlists(client_secret_file,
                                                      profile, credential_file,
                                                      force_authenticate)
    except Exception as e:
        print("Exception occured: %s.\n"
              "It is possible that existing credentials are not valid?\n"
              "Try --force option.\n" % (str(e)))

    return None


def _get_today():
    return str(datetime.date.today())


def get_output_filepath_prefix(profile, outfolder):
    """Derives file path from profile name to write playlists data.

    Args:
        profile(`str`): Profile name to associate with credentials

    Returns:
        str: Output file path
    """
    return '%s/%s.%s' % (outfolder, profile, _get_today())


def _get_credential_filename(profile, credential_folder, credential_file):
    if (credential_file is None):
        credential_file = credential_folder + "/" + profile + CREDENTIAL_FILE_EXT
    return credential_file


def _write_json_file(json_object, filename):
    with open(filename, "w") as outfile:
        json.dump(json_object, outfile, indent=4)


def _write_default_file(json_object, filename):
    with open(filename, "w") as outfile:
        for playlist in json_object:
            outfile.write('Playlist Title: %s, Id: %s, Count: %d\n'
                          '-----------------------------------------------\n' %
                          (playlist['snippet']['title'], playlist['id'],
                           playlist['contentDetails']['itemCount']))
            for video in playlist['videos']:
                outfile.write(
                    'Index: %d, Id: %s, Video Title: "%s"\n' %
                    (video[0], video[1]['id'], video[1]['snippet']['title']))
            outfile.write('===============================================\n')


def _get_json_filename(prefix):
    return prefix + JSON_FILE_EXT


def _get_default_filename(prefix):
    return prefix + DEFAULT_FILE_EXT


def _write_playlist_files(json_object, fileprefix, formats):
    os.makedirs(os.path.dirname(fileprefix), exist_ok=True)
    try:
        if JSON_FORMAT in formats:
            _write_json_file(json_object, _get_json_filename(fileprefix))
        if DEFAULT_FORMAT in formats:
            _write_default_file(json_object, _get_default_filename(fileprefix))
    except IOError as e:
        print(
            "IOError when writing to %s with error number: %d and message: %s"
            % (e.filename, e.errno, e.strerror),
            file=sys.stderr)
    except Exception as e:
        print("Exception occured: " + str(e), file=sys.stderr)


def main():
    """Provides main entrypoint for this module.

    Processes command line arguments,filename
    fetches youtube playlists ands saves it to a file.
    """

    playlist_downloader = PlaylistDownloader(ApiClient())

    _main(playlist_downloader, sys.argv[1:])


def _main(playlist_downloader, args):
    parsed_args = _get_parsed_args(args)

    playlist_object = fetch_playlists(playlist_downloader,
                                      parsed_args.secretfile,
                                      parsed_args.profile,
                                      parsed_args.credentialfolder,
                                      parsed_args.credential,
                                      parsed_args.force)
    if playlist_object is not None:
        outfileprefix = get_output_filepath_prefix(parsed_args.profile,
                                                   parsed_args.outfolder)
        _write_playlist_files(playlist_object, outfileprefix,
                              parsed_args.format)
