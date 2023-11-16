"""
=============================================================================
File: utils.py
Description: Helper functions
Author: Praful https://github.com/Praful/music-playlist-export-import
Licence: GPL v3
=============================================================================
"""

import contextlib
import csv
import sys
import re
import requests
import html
import time
import io
from pprint import pprint
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from difflib import SequenceMatcher as FuzzyMatch

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


def match(s1, s2):
    s1a, s2a = s1.lower(), s2.lower()
    #  print(s1,'/', s2, '/', FuzzyMatch(None, s1a, s2a).ratio() )
    return s1a in s2a or s2a in s1a or (FuzzyMatch(None, s1a, s2a).ratio() > 0.3)


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
            # pprint(html)
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


def read_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        result = [row for row in reader]

    del result[0]  # remove header
    print(f'Total tracks: {len(result)}')
    return result
