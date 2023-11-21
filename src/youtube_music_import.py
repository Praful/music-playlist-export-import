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
import ytmusicapi
#  from ytmusicapi.ytmusic import YTMusic
from ytmusicapi.ytmusic import YTMusic  # noqa: E402
import traceback

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


# ytmusic and type are ignore now; leave in case they're reinstated
def find_song(ytmusic, search_results, type, artist, song):
    def song_title(res):
        title = res["title"]
        if res["resultType"] == "video":
            title_split = title.split("-")
            if len(title_split) == 2:
                title = title_split[1]
        return title

    #  print(f'{song} by {artist}, {type} ==========================')
    #  pprint(search_results)
    score = {}
    #  videoids = {}
    for i, s in enumerate(search_results):
        try:
            #  print("------------------------------------")
            #  pprint(s)
            if s['resultType'] in ['song', 'album', 'video'] and 'videoId' in s:
                title = song_title(s)
                # if we have a good match, return the videoId
                if artist_match(artist, s['artists']) and match(song, title):
                    return s['videoId']
                else:
                    # store fuzzy match score and later pick the best
                    for a in s['artists']:
                        ratio = fuzzy_match_ratio(
                            song, title, artist, a['name'])
                        current = score.get(s['videoId'], 0)
                        if ratio > current:
                            #  videoids[s['videoId']] = s
                            score[s['videoId']] = ratio

        except Exception as e:
            print('Error', e, s)
            traceback.print_exc()

    # max score return key
    if len(score) > 0:
        #  print('========= score', score)
        max_score_key = max(score, key=lambda k: score[k])
        #  print('========= max score', max_score_key)
        #  print(f'For {song} by {artist} picked:')
        #  print(videoids[max_score_key])
        return max_score_key
    else:
        return None


def failed_response_reason(res):
    try:
        actions = res['actions'][0]
        text = actions['addToToastAction']['item']['notificationActionRenderer']['responseText']['runs'][0]['text']
        return text
    except:
        return None


def print_failed_response(res):
    reason = failed_response_reason(res)
    if reason is None:
        print('-- Failed, full error:', res)
    else:
        print('-- Failed:', reason)


def import_playlist(tracks, playlist_name, playlist_desc):
    # This lets user paste in connection string from command line.
    # You can uncomment this line the first time you run the script so that the
    # headers_auth.json file is created. Remember to comment it out again.
    #  ytmusicapi.setup(filepath="headers_auth.json")

    SUCCESS = 'STATUS_SUCCEEDED'

    # this assumes connection string are in json file
    ytmusic = YTMusic('headers_auth.json')
    videoIdSet = set()

    print('\nSearching YouTube for songs...\n')

    for artist, song in tracks:
        try:
            search_results = ytmusic.search(f'{song} by {artist}')
            #  search_results = ytmusic.search(
            #  f'{song} by {artist}', filter='songs', ignore_spelling=True)

            print(f'{song} by {artist}')
            videoId = find_song(ytmusic, search_results, 'song', artist, song)

            if videoId is None:
                videoId = find_song(
                    ytmusic, search_results, 'video', artist, song)

            if videoId is not None:
                videoIdSet.add(videoId)
            else:
                print("*** Not found")

        except Exception as e:
            print('Error searching song', e)
            traceback.print_exc(file=sys.stdout)

    print('\nCreating YouTube playlist\n')
   #  print(videoIdSet)
    #  return
    playlistId = ytmusic.create_playlist(playlist_name, playlist_desc)
    res = ytmusic.add_playlist_items(playlistId, list(videoIdSet))
    if res['status'] == SUCCESS:
        print(
            f"Success: {len(videoIdSet)} out {len(tracks)} added to new playlist {playlist_name} at")
        print(f"https://music.youtube.com/playlist?list={playlistId}")
    else:
        print_failed_response(res)


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
