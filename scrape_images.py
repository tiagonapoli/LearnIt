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
from urllib.request import urlopen,Request
from io import StringIO

import urllib.error
import os
import sys
import socket

#URL RETRIEVE TIMEOUT
socket.setdefaulttimeout(1)
arq = open("google_credentials.txt", "r")
DEV_KEY,CSE_ID = arq.read().split(' ')
CSE_ID = CSE_ID.replace('\n','')
arq.close()

opener = urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)


def geturl(link,local):
	try:
		urllib.request.urlretrieve(link,local)
		print ('Saved {}'.format(local))
		return 1
	except:
		# Link probably returned non-image data (redirect, etc)
		print ('ERROR: Failed to read/save image')
		return 0

def get_image_type(name):
	aux = []
	for i in range(len(name)-1,-1,-1):
		if name[i] == '.':
			break
		aux.append(name[i])
	aux = aux[::-1]
	res = []
	if '?' in aux:
		pos = aux.index('?')
		res = aux[:pos:]
	else:
		res = aux
	res = ''.join(res)
	return res

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
	
	for i in range(0, num_requests): # Make n number of requests, saving 10
		res = service.cse().list(
            q = query,
            cx = CSE_ID,
            searchType = 'image',
            num = num_results,
            start = i*num_results+1,
		).execute()

		for item in res['items']:
			print(item['link'])
			url = item['link']
			filename = '{}/{}{:03d}.{}'.format(directory,query.replace(' ','_'),count, get_image_type(url))
			count += geturl(url,filename)
		
		return count



if __name__ == '__main__':
	''' Scrapes images for 6 different queries. '''
	d = urllib.request.urlopen("http://e360.yale.edu/assets/site/Trees_JeroenVanNieuwenhoveFlickr.jpg")
	#IDEAS: USE CONTENT-TYPE TO GET IMAGE TYPE!!!
	#CHECK CONTENT LENGTH - MAXIMUM
	print (d.info())
	'''
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
	'''
	
