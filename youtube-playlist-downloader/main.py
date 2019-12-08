'''
Provide command line interface for this package.

Command line usage:

python3 youtube_playlist_downloader
        [-r|--reauthenticate] [-p|--profile PROFILE]

    -r, --reauthenticate
        Reauthenticates even though prior credentials are stored
    -p PROFILE, --profile PROFILE
        Name to associate with output and credentials file names
'''

import argparse
import datetime
import json
import sys

from googleapiclient.errors import HttpError

import youtube

OUT_FILE_EXT = '.playlists.json'


def get_parsed_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-r',
        '--reauthenticate',
        required=False,
        action='store_true',
        help='Reauthenticate even if previous credentials exist.')

    parser.add_argument(
        '-p',
        '--profile',
        help='Provide profile name to use multiple google accounts.',
        default='default')

    return parser.parse_args(args)


def fetch_user_playlist_object(profile, reauthenticate):
    try:
        return youtube.download_user_playlists(profile, reauthenticate)
    except HttpError as e:
        print('An HTTP error %d occurred. \n'
              'It is possible that existing credentials are not valid, '
              'try --reauthenticate option.\n'
              'content:\n%s\n' % (e.resp.status, e.content))
    except Exception as e:
        print("Exception occured: " + str(e))

    return None


def get_output_filename(profile):
    return 'out/%s.%s%s' % (profile, datetime.date.today(), OUT_FILE_EXT)


def write_playlists_file(json_object, filename):
    try:
        with open(filename, "w") as outfile:
            json.dump(json_object, outfile, indent=4)
    except IOError as e:
        print(
            "IOError when writing to %s with error number: %d and message: %s"
            % (e.filename, e.errno, e.strerror))
    except Exception as e:
        print("Exception occured: " + str(e))


def main():
    parsed_args = get_parsed_args(sys.argv[1:])

    playlist_object = fetch_user_playlist_object(parsed_args.profile,
                                                 parsed_args.reauthenticate)

    if playlist_object is not None:
        output_filename = get_output_filename(parsed_args.profile)
        write_playlists_file(playlist_object, output_filename)
