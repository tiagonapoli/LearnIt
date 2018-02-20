#! /usr/bin/python3
import psycopg2
import os
import sys

'''
	./all.py PATH_TO_TABLEs
'''

args = sys.argv[1:]
PATH = ''

if len(args) > 0 and len(args[0]) > 0:
	PATH = args[0] 

if PATH[-1] == '/':
	PATH = PATH[:-1] 

data_path = PATH + '/data'
tables_path = PATH + '/tables'

os.system("cp -TRvf {} ../../data/".format(data_path))
os.system("./users.py {}".format(tables_path))
os.system("./languages.py {}".format(tables_path))
os.system("./topics.py {}".format(tables_path))
os.system("./words.py {}".format(tables_path))
os.system("./cards.py {}".format(tables_path))
os.system("./archives.py {}".format(tables_path))


