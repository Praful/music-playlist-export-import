"""
=============================================================================
File: youtube_music_import.py
Description: Import CSV playlist to YouTube Music
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
TODO:
- if playlist song not found on YouTube add other type of track eg video
"""

from utils import *
import argparse
from pprint import pprint
from ytmusicapi import YTMusic


DEFAULT_PLAYLIST_NAME = "Uploaded playlist from youtube_music_import"


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='YouTube Music Import')
    cmdline.add_argument('--csv', dest='input',
                         help='Filename of CSV playlist file (tab-separated - artist, song).  ')
    cmdline.add_argument('--name', type=str, default=DEFAULT_PLAYLIST_NAME,
                         help=f'Name of new playlist to create (default is {DEFAULT_PLAYLIST_NAME})')
    cmdline.add_argument('--description', type=str, default='',
                         help=f'Name of new playlist to create (default is same as name)')
    return cmdline


# return true if any of the (potentially mulitple) artists match
# with the input playlist's artist
def artist_match(orig_artist, artists):
    for artist in artists:
        if match(orig_artist, artist['name']):
            return True
    return False


def find_song(search_results, type, artist, song):
    for i, s in enumerate(search_results):
        try:
            if s['resultType'] == type and artist_match(artist, s['artists']) and match(song, s['title']):
                return i

            # video might have artist in title
            if s['resultType'] == 'video' and match(song, s['title']) and match(artist, s['title']):
                return i

        except:
            print('Error', s)

    return -1


def import_to_youtube(tracks, playlist_name, playlist_desc):
    # this lets user paste in connection string from command line
    # YTMusic.setup(filepath="headers_auth.json")

    # this assumes connection string are in json file
    ytmusic = YTMusic('headers_auth.json')

    playlistId = ytmusic.create_playlist(playlist_name, playlist_desc)
    for artist, song in tracks:
        # search_results = ytmusic.search(f'{artist} - {song}')
        search_results = ytmusic.search(f'{song} by {artist}')

        print(f'Adding song {song} by {artist}')

        song_index = find_song(search_results, 'song', artist, song)
        if song_index < 0:
            song_index = find_song(search_results, 'video', artist, song)

        if song_index > -1:
            # pass

            res = ytmusic.add_playlist_items(
                playlistId, [search_results[song_index]['videoId']])
            if res['status'] != 'STATUS_SUCCEEDED':
                print('-- Failed:', res)
        else:
            print("*** Not found")

    print('Finished')


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    playlist = read_csv(args.input)
    # print(playlist)

    desc = args.description if args.description != '' else args.name
    import_to_youtube(playlist, args.name, desc)


if __name__ == '__main__':
    main()
