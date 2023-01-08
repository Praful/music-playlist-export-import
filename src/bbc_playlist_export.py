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

SOUP_PARSER = 'html.parser'
#  SOUP_PARSER = 'lxml'


# these are examples of a dynamic URL
# "https://www.bbc.co.uk/sounds/play/m001gjqs"
# "https://www.bbc.co.uk/sounds/play/m001g6wy"
PLAYLIST_URL_DYNAMIC_PAGE = "https://www.bbc.co.uk/sounds/play/m001gjqs"

PLAYLIST_URL_STATIC_PAGE = "https://www.bbc.co.uk/programmes/m001gjqs"

TAB = '\t'


@contextlib.contextmanager
def smart_open(filename=None, filemode='w'):
    """
    Return handle to file (if specified) or sys output
    From https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely/17603000
    """

    if filename and filename != '-':
        #  fh = open(filename, 'w')
        fh = io.open(filename, newline='', mode=filemode, encoding="utf-8")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def isBlank(myString):
    return not (myString and myString.strip())


def contains(s, search_for_list, case_sensitive=re.IGNORECASE):
    """
    Return index if s contains any string in search_for_list.
    Return -1 if string not found.
    """
    for i, search_for in enumerate(search_for_list):
        if re.search(search_for, s, case_sensitive):
            return i

    return -1


def GetPage(url, dynamic=False):
    """
    Fetch page from web
    """
    def page_found(code):
        return code == 200

    if not dynamic:
        page = requests.get(url)

        if not page_found(page.status_code):
            print(f'Status {page.status_code} for {url}')

        html = page.content
    else:
        try:
            firefox_options = Options()
            firefox_options.headless = True
            firefox_options.binary = 'C:/Program Files/Firefox Developer Edition/firefox.exe'
            ser = Service(r"./geckodriver.exe")
            driver = webdriver.Firefox(service=ser, options=firefox_options)
            driver.get(url)

            # Ensure the page is fully loaded; there are better ways to do this but
            # this is good enough. For more info , see:
            #    https://www.selenium.dev/documentation/webdriver/waits/
            time.sleep(4)

            # Render the dynamic content to static HTML
            html = driver.page_source
        finally:
            driver.quit()

    return html


def clean_string(s):
    """
    Remove unnecessary characters from beginning and end of s
    """
    if result := s:
        # replace stuff like &amp with &, etc
        result = html.unescape(result)

        result = result.strip(' -:,.–‘’')

        # remove initial <p>
        if match1 := re.search(r'<p>(.*)', result, re.IGNORECASE):
            result = match1.group(1)

        # remove trailing </p>
        if match2 := re.search(r'(.*)</p>', result, re.IGNORECASE):
            result = match2.group(1)

    return result


def write_csv(rows, header, filename=None, delim=TAB):
    """
    Create a CSV of episodes scraped
    """
    with smart_open(filename, 'a') as output:
        writer = csv.writer(
            output, delimiter=delim, lineterminator='\r\n')
        writer.writerow(header)
        [writer.writerow(r) for r in rows]


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

    print(f'Creating output for {result}:')
    write_csv(result, ['Artist', 'Song'], output)

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

    # uses BBC Sounds
    # playlist = export1(soup, args.output)

    # uses Radio 6 site
    playlist = export2(soup, args.output)
    # pprint(playlist)


if __name__ == '__main__':
    main()
