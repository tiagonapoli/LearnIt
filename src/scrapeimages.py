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

import multiprocessing
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


class FetchImages(object):

	def __init__(self):
		pass


	def geturl(self, url, directory, query, file_id, limit_size_bytes):
			
		try:
			site = urllib.request.urlopen(url)
		except Exception as e:
			print("Urlopen failed :(")
			print(e);
			return 0

		info = site.info()
		content_type = info.get_content_maintype()
		extension = info.get_content_subtype()

		if (content_type != "image") or (not ('Content-Length' in info.keys())):
			return 0

		if (extension != "jpg") and (extension != "jpeg"):
			return 0

		size = int(info['Content-Length'])
		print("size = {}".format(size))
		filename = '{}/{}{:03d}.{}'.format(directory,query.replace(' ','_'), 
											file_id, extension)
		
		if size > limit_size_bytes:
			return 0
			
		print()
		
		try:
			print ('Saved {}'.format(filename))
			urllib.request.urlretrieve(url,filename)
			return 1
		except Exception as e:
			# Link probably returned non-image data (redirect, etc)
			print ('ERROR: Failed to read/save image {}\n'.format(url))
			print(e)
			return 0




	def fetch_images(self,query, directory, num_images=5):
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
		self.count = 0

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
	
		pool = multiprocessing.Pool(processes = 4)
		qtos = 0
		limit_size_bytes = 307200
		calls = []
		for item in res['items']:
			print(item['link'] + '\n')
			url = item['link']
			qtos += 1
			calls.append((url, directory, query, qtos, limit_size_bytes))
		
		results = [pool.apply_async(self.geturl, args=(a,b,c,d,e,)) for a,b,c,d,e in calls]
		output = [p.get() for p in results]

		return output.count(1)



if __name__ == '__main__':

	base_directory = 'images'
	queries = [
		'buildings',
		'cars',
		'faces',
		'food',
		'people',
		'trees']
	
	x = FetchImages()
	for query in queries:
		directory = '{}/{}'.format(base_directory, query)
		x.fetch_images(query, directory)
