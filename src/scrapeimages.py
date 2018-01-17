'''
CS.661: Computer Vision
Johns Hopkins University
Flynn, Michael

Python script to scrape images from Google CSE.

Usage:
    python scrape_images.py {directory} {num_queries}


Needs:
	pip -> google-api-python-client
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
arq = open("../credentials/google_credentials.txt", "r")
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
	return res

def fetch_images(query, directory, num_images=5):
	'''
    Fetches images from Google search and stores them as {###}.jpg.

    Args:
        query (str): The query to search for on Google.
        directory (str): The location to store images.
    Args (optional):
	'''

	if not os.path.exists(directory):
		os.makedirs(directory)
	service = build('customsearch', 'v1', developerKey=DEV_KEY)
	num_results = 10 # I believe this is the max number of results allowed
	
	try:
		res = service.cse().list(
						q = query,
						cx = CSE_ID,
						searchType = 'image',
						num = num_results,
						start = 1,
						).execute()
	except Exception as e:
		print("Error ocurred with google api")
		print(e)
		return 0
	
	count = 0;
	limit_size_bytes = 256000
	for item in res['items']:
	
		print(item['link'])
		url = item['link']
		
		try:
			site = urllib.request.urlopen(url)
		except Exception as e:
			print("Urlopen failed :(")
			print(e);
			continue

		info = site.info()
		content_type = info.get_content_maintype()
		extension = info.get_content_subtype()

		if (content_type != "image") or (not ('Content-Length' in info.keys())):
			continue

		if (extension != "jpg") and (extension != "jpeg"):
			continue

		size = int(info['Content-Length'])
		filename = '{}/{}{:03d}.{}'.format(directory,query.replace(' ','_'),count,extension)
		print("size = {}".format(size))
		
		if size > limit_size_bytes:
			continue

		count += geturl(url,filename)
		print()
		if count >= num_images:
			break
		
	return count




if __name__ == '__main__':
	''' Scrapes images for 6 different queries. '''
	
	base_directory = 'images'
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
		fetch_images(query, directory)
