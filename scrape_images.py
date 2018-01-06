'''
CS.661: Computer Vision
Johns Hopkins University
Flynn, Michael

Python script to scrape images from Google CSE.

Usage:
    python scrape_images.py {directory} {num_queries}

'''

from apiclient.discovery import build
from PIL import Image

import cStringIO
import os
import sys
import urllib2


DEV_KEY = '<My dev key>'
CSE_ID = '<My CSE Id>'


def fetch_images(query, directory, num_requests=1, start_idx=0):
    '''
    Fetches images from Google search and stores them as {###}.jpg.

    Args:
        query (str): The query to search for on Google.
        directory (str): The location to store images.
    Args (optional):
        num_requests (int): How many calls to Google CSE should be made (with
            10 images grabbed per request).
        start_idx (int): The starting index to search from. Images will be
            named accordingly.
    '''

    if not os.path.exists(directory):
        os.makedirs(directory)

    service = build('customsearch', 'v1', developerKey=DEV_KEY)

    count = start_idx

    num_results = 10 # I believe this is the max number of results allowed
                     # per request

    for i in range(0, num_requests): # Make n number of requests, saving 10
                                     # images each
        res = service.cse().list(
            q = query,
            cx = CSE_ID,
            searchType = 'image',
            num = num_results,
            start = i*num_results+1,
        ).execute()

        for item in res['items']:

            try:
                filename = '{}/{:03d}.jpg'.format(directory, count)

                contents = urllib2.urlopen(item['link'], timeout=5).read()
                data = cStringIO.StringIO(contents)
                Image.open(data).convert('RGB').save(filename, 'JPEG')

                print 'Saved {}'.format(filename)
                count += 1

            except urllib2.URLError:
                # urllib2 either couldn't open link or timed out
                print 'ERROR: Failed to load URL'
            except:
                # Link probably returned non-image data (redirect, etc)
                print 'ERROR: Failed to read/save image'


if __name__ == '__main__':
    ''' Scrapes images for 6 different queries. '''

    base_directory = 'images'
    num_requests = 1

    if len(sys.argv) > 1: # 1st arg - where images are saved
        base_directory = sys.argv[1]
    if len(sys.argv) > 2: # 2nd arg - how many requests to make per query
        num_requests = int(sys.argv[2])

    queries = [
        'buildings',
        'cars',
        'faces',
        'food',
        'people',
        'trees',
    ]

    for query in queries:
        directory = '{}/{}'.format(base_directory, query)
        fetch_images(query, directory, num_requests=num_requests)
