"""
=============================================================================
File: youtube_music_import.py
Description: Import CSV playlist to YouTube Music
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
"""

from bs4 import BeautifulSoup
import requests
import re
import sys
import traceback
import collections
from collections.abc import Sequence
import argparse
import csv
import contextlib
import io
import time
import html
from pprint import pprint
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from ytmusicapi import YTMusic
from difflib import SequenceMatcher as FuzzyMatch


DEFAULT_PLAYLIST_NAME = "Uploaded playlist from youtube_music_import"

TAB = '\t'


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


def match(s1, s2):
    s1a, s2a = s1.lower(), s2.lower()
    return s1a in s2a or s2a in s1a or FuzzyMatch(None, s1a, s2a).ratio() > 0.7


def import_to_youtube(tracks, playlist_name, playlist_desc):
    # this lets user paste in connection string from command line
    # YTMusic.setup(filepath="headers_auth.json")

    # this assumes connection string are in json file
    ytmusic = YTMusic('headers_auth.json')

    playlistId = ytmusic.create_playlist(playlist_name, playlist_desc)
    for artist, song in tracks:
        search_results = ytmusic.search(f'{artist} - {song}')

        print('Adding ', search_results[0]['artists']
              [0]['name'], search_results[0]['title'])

        song_index = -1
        for i, s in enumerate(search_results):
            try:
                if s['resultType'] == 'song' and match(artist, s['artists'][0]['name']) and match(song, s['title']):
                    song_index = i
                    break

            except:
                print('Error', s)

        if song_index > -1:
            res = ytmusic.add_playlist_items(
                playlistId, [search_results[song_index]['videoId']])
            if res['status'] != 'STATUS_SUCCEEDED':
                print('-- Failed:', res)
        else:
            print("**", artist, song, "not found")
    
    print('Finished')


def read_playlist(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        result = [row for row in reader]

    del result[0]  # remove header
    print(f'Total tracks: {len(result)}')
    return result


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    playlist = read_playlist(args.input)
    # playlist = read_playlist('./playlist1.csv')
    print(playlist)

    desc = args.description if args.description !='' else args.name
    import_to_youtube(playlist, args.name, desc)


if __name__ == '__main__':
    main()
