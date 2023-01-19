"""
=============================================================================
File: youtube_music_export.py
Description: Export YouTube Music playlist to CSV
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
TODO:
- if playlist song not found on YouTube add other type of track eg video
"""

import argparse
from pprint import pprint
from utils import *
from ytmusicapi import YTMusic


DEFAULT_PLAYLIST_NAME = "Uploaded playlist from youtube_music_import"


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='YouTube Music playlist exporter')
    cmdline.add_argument('--csv', dest='output',
                         help='Filename of CSV file (tab-separated).')
    cmdline.add_argument('--url', dest='url', type=str,
                         help=f'URL of playlist (copied from YouTube Music website eg https://music.youtube.com/playlist?list=RDCLAK5uy_kVXmNQjiBEKjCGifBWc3eTMg8Fwjc6K8M')

    return cmdline


def export_playlist(url, output):
    ytmusic = YTMusic('headers_auth.json')

    # test
    if not url:
        url = 'https://music.youtube.com/playlist?list=RDCLAK5uy_kVXmNQjiBEKjCGifBWc3eTMg8Fwjc6K8M'

    playlistId = url.split('?list=')[1]

    playlist = ytmusic.get_playlist(playlistId, None)

    print(f'Exporting playlist {playlist["title"]} ...')

    result = []
    for t in playlist['tracks']:
        result.append([t['artists'][0]['name'], t['title']])

    print(f'{len(result)} tracks in playlist')
    print(f'Creating output...')
    write_csv(result, ['Artist', 'Song'], output)
    print('Finished')

    return result


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    playlist = export_playlist(args.url, args.output)
    # print(playlist)


if __name__ == '__main__':
    main()
