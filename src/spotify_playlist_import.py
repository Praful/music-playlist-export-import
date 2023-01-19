"""
=============================================================================
File: spotify_playlist_import.py
Description: Import spotify playlist from CSV file.
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
References/examples:

- https://github.com/spotipy-dev/spotipy/tree/master/examples
- https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50
- https://developer.spotify.com/console/playlists/

"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


from utils import *
import argparse

DEFAULT_PLAYLIST_NAME = "Uploaded playlist from youtube_music_import"


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='Spotify Import')
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


def find_song(sp, artist, song):
    search_result = sp.search(f'track: {song} artist: {artist}', type='track')
    if 'tracks' in search_result and 'items' in search_result['tracks']:
        # first look at tracks
        for track in search_result['tracks']['items']:
            try:
                if artist_match(artist, track['artists']) and match(song, track['name']):
                    return track['id']

            except Exception as e:
                print('Error', e, track)

        # if not found, check singles on albums
        for track in search_result['tracks']['items']:
            if 'albums' in track:
                for album in track['albums']:
                    if album['album_type'] == 'single':
                        try:
                            if artist_match(artist, track['artists']) and match(song, track['name']):
                                return album['id']

                        except Exception as e:
                            print('Error', e, track)

    return None


def import_playlist(tracks, playlist_name, playlist_desc):

    # Generate your client id and secret from
    #  https://developer.spotify.com/dashboard/applications
    # This doesn't work when creating/updating a playlist:
    # auth_manager = SpotifyClientCredentials(
    # client_id='your id', client_secret='your secret')
    # sp = spotipy.Spotify(auth_manager=auth_manager)

    scope = "playlist-modify-private, playlist-modify-public, playlist-read-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    print(f'Importing playlist...')

    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(
        user_id, name=playlist_name, public=False, description=playlist_desc)
    success_count = fail_count = 0

    for artist, song in tracks:
        print(f'Adding song {song} by {artist}')

        id = None
        try:
            if (id := find_song(sp, artist, song)) is not None:
                result = sp.playlist_add_items(
                    playlist['id'], [id], position=None)
                success_count += 1
            else:
                print("*** Not found")
                fail_count += 1

        except Exception as e:
            print(f'Error adding {song} by {artist}', e, id)
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
