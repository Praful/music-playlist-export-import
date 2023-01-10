"""
=============================================================================
File: bbc_playlist_export.py
Description: grab playlist from BBC site and store as CSV file
When scraping web pages, BeautifulSoup is usually enough. However, sometimes,
web pages are dynamically rendered using JavaScript. In that case, you have to
render the page before using BeautifulSoup. One way of doing this to use a 
headless browser via Selenium. For example, see
https://www.geeksforgeeks.org/scrape-content-from-dynamic-websites/.
Below, in function export1(), I use this technique using Firefox.
For that the driver executable (geckodriver.exe)
must be in the src folder. You'll probably also need to change the path to
the main Firefox browser. You can use a Chrome-based browser if you want.

export2() using the Radio 6 website to scrape a playlist. For this, you
need BeautifulSoup only.

In practice, you'll have to create your own export() function, depending
on the source of your playlist. However, if you create a CSV file 
(format <Artist><TAB><Song> with header), the youtube_music_import.py script
will import it to YouTube Music.

Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
"""
import os
import sys
sys.path.append(os.path.relpath("../src"))
from utils import *
from bs4 import BeautifulSoup
import argparse
from pprint import pprint

SOUP_PARSER = 'html.parser'
#  SOUP_PARSER = 'lxml'


# these are examples of a dynamic URL
# "https://www.bbc.co.uk/sounds/play/m001gjqs"
# "https://www.bbc.co.uk/sounds/play/m001g6wy"
PLAYLIST_URL_DYNAMIC_PAGE = "https://www.bbc.co.uk/sounds/play/m001gjqs"

PLAYLIST_URL_STATIC_PAGE = "https://www.bbc.co.uk/programmes/m001gjqs"


def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(prog='BBC playlist exporter')
    cmdline.add_argument('--csv', dest='output',
                         help='Filename of CSV file (tab-separated). The file will be appended '
                         'to if it exists (default output is to console)')
    cmdline.add_argument('--url', dest='url', type=str, default=PLAYLIST_URL_STATIC_PAGE,
                         help=f'URL of playlist (default is {PLAYLIST_URL_STATIC_PAGE})')
    cmdline.add_argument('--dynamic', dest='dynamic', type=bool, default=False,
                         help=f'URL of playlist (default is {False})')

    return cmdline


# Export BBC Morning After Mix from BBC Sounds
def export1(soup, output):
    print("Exporting...")
    tracks = soup.find_all('div', class_='sc-c-basic-tile__text')
    result = [track['title'].split(' - ') for track in tracks]

    print(f'Creating output for {result}:')
    write_csv(result, ['Artist', 'Song'], output)

    return result


def export2(soup, output):
    """
    Export BBC Morning After Mix from Radio 6 website
    """

    print("Exporting...")
    tracks = soup.find_all('div', class_='segment__track')
    result = [[track.h3.span.text, track.p.span.text] for track in tracks]

    print('Creating output')
    write_csv(result, ['Artist', 'Song'], output)
    print('Finished')

    return result


def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    print(args)

    print("getting page")

    html = GetPage(args.url, args.dynamic)
    soup = BeautifulSoup(html, SOUP_PARSER)

    if args.dynamic:
        # uses BBC Sounds
        playlist = export1(soup, args.output)
    else:
        # uses Radio 6 site
        playlist = export2(soup, args.output)

    # pprint(playlist)


if __name__ == '__main__':
    main()
