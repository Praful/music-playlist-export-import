"""
=============================================================================
File: spotify_playlist_export.py
Description: Export spotify playlist to CSV file.
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
References/examples:

- https://github.com/spotipy-dev/spotipy/tree/master/examples

- https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50

- 
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


from utils import *
import argparse


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='Spotify playlist exporter')
    cmdline.add_argument('--csv', dest='output',
                         help='Filename of CSV file (tab-separated). The file will be appended '
                         'to if it exists (default output is to console)')
    cmdline.add_argument('--url', dest='name', type=str,
                         help=f'URL of playlist (copied from Spotify website eg https://open.spotify.com/playlist/2c2rOfPMCEdjYzmfS0AHev)')

    return cmdline


# Spotify paginates output (in groups of 100); the sp.next() goes through
# all the pages and returns all the tracks not just the first 100.
def get_playlist_tracks(sp, playlist_id):
    # results = sp.user_playlist_tracks(username,playlist_id)
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def export(url, output):

    auth_manager = SpotifyClientCredentials(
        client_id='x', client_secret='y')

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # test
    if not url:
        url = 'https://open.spotify.com/playlist/2c2rOfPMCEdjYzmfS0AHev'

    playlist_URI = url.split("/")[-1].split("?")[0]

    playlist_info = sp.user_playlist(
        user=None, playlist_id=playlist_URI, fields="name")
    print(f'Exporting playlist {playlist_info["name"]} ...')

    tracks = get_playlist_tracks(sp, playlist_URI)

    result = []
    for track in tracks:

        # URI
        track_uri = track["track"]["uri"]

        # Track name
        track_name = track["track"]["name"]

        # Main Artist
        artist_uri = track["track"]["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)

        # Name, popularity, genre
        artist_name = track["track"]["artists"][0]["name"]
        artist_pop = artist_info["popularity"]
        artist_genres = artist_info["genres"]

        # Album
        album = track["track"]["album"]["name"]

        # Popularity of the track
        track_pop = track["track"]["popularity"]

        # print(artist_name, 'track:', track["track"]["name"])
        result.append([artist_name, track["track"]["name"]])

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
    print(args)

    playlist = export(args.name, args.output)

    # pprint(playlist)


if __name__ == '__main__':
    main()
