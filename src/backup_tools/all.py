#! /usr/bin/python3
import psycopg2
import os
import sys

'''
	./all.py PATH_TO_TABLEs -debug
'''

print("Debug mode? (1/0)")
debug_mode = input()
debug_mode = int(debug_mode)

print("Debug Mode = {}".format(debug_mode))

args = sys.argv[1:]
PATH = ''

if len(args) > 0 and len(args[0]) > 0:
	PATH = args[0] 

if PATH[-1] == '/':
	PATH = PATH[:-1] 

data_path = PATH + '/data'
tables_path = PATH + '/tables'

dest = '../../data/'
if debug_mode == 1:
	dest = '../../data_debug/'


os.system("cp -TRvf {} {}".format(data_path, dest))
os.system("./users.py {} {}".format(tables_path, debug_mode))
os.system("./subjects.py {} {}".format(tables_path, debug_mode))
os.system("./topics.py {} {}".format(tables_path, debug_mode))
os.system("./study_items.py {} {}".format(tables_path, debug_mode))
os.system("./cards.py {} {}".format(tables_path, debug_mode))


