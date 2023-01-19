"""
=============================================================================
File: youtube_music_import.py
Description: Import CSV playlist to YouTube Music
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
TODO:

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


# return true if any of the (potentially multiple) artists match
# with the input playlist's artist
def artist_match(orig_artist, artists):
    for artist in artists:
        if match(orig_artist, artist['name']):
            return True
    return False


def find_song(ytmusic, search_results, type, artist, song):
    for i, s in enumerate(search_results):
        try:
            if s['resultType'] == type and artist_match(artist, s['artists']) and match(song, s['title']):
                # for singles on albums, there is no videoId; we have to get the audioPlaylistId
                # for the single from the album
                if type == 'album' and s['type'] == 'Single':
                    album = ytmusic.get_album(s['browseId'])
                    return album['audioPlaylistId']
                else:
                    return s['videoId']

            # video might have artist in title
            if s['resultType'] == 'video' and match(song, s['title']) and match(artist, s['title']):
                return s['videoId']

        except Exception as e:
            print('Error', e, s)

    return None


def import_playlist(tracks, playlist_name, playlist_desc):
    # this lets user paste in connection string from command line
    # YTMusic.setup(filepath="headers_auth.json")

    SUCCESS = 'STATUS_SUCCEEDED'

    # this assumes connection string are in json file
    ytmusic = YTMusic('headers_auth.json')
    success_count = fail_count = 0

    playlistId = ytmusic.create_playlist(playlist_name, playlist_desc)
    for artist, song in tracks:
        search_results = ytmusic.search(f'{song} by {artist}')

        print(f'Adding song {song} by {artist}')

        audioPlaylistId = None
        videoId = find_song(ytmusic, search_results, 'song', artist, song)

        if videoId is None:
            audioPlaylistId = find_song(
                ytmusic, search_results, 'album', artist, song)

        if videoId is None and audioPlaylistId is None:
            videoId = find_song(
                ytmusic, search_results, 'video', artist, song)

        if videoId is not None:
            res = ytmusic.add_playlist_items(playlistId, [videoId])
            if res['status'] != SUCCESS:
                print('-- Failed:', res)
                fail_count += 1
            else:
                success_count += 1
        elif audioPlaylistId is not None:
            res = ytmusic.add_playlist_items(
                playlistId, source_playlist=audioPlaylistId)
            if res['status'] != SUCCESS:
                print('-- Failed:', res)
                fail_count += 1
            else:
                success_count += 1
        else:
            print("*** Not found")
            fail_count += 1

    print(
        f'Finished: imported {success_count}, failed {fail_count}, total {len(tracks)}')


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    playlist = read_csv(args.input)
    # print(playlist)

    desc = args.description if args.description != '' else args.name
    import_playlist(playlist, args.name, desc)


if __name__ == '__main__':
    main()
