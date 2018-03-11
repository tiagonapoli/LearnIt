#! /usr/bin/python3
import psycopg2
import os
import sys

args = sys.argv[1:]
debug_mode = int(args[1])
PATH = args[0]

print("CARDS")
try:
	if debug_mode == 1:
		arq = open("../../credentials/connect_str_debug.txt", "r")
	else:
		arq = open("../../credentials/connect_str.txt", "r")	
	connect_str = arq.read()
	DB_NAME = connect_str.split()[0][7:]
	DB_USER_NAME = connect_str.split()[1][5:]
	arq.close()
	# use our connection values to establish a connection
	conn = psycopg2.connect(connect_str)
	# create a psycopg2 cursor that can execute queries
	cursor = conn.cursor()
	cursor.execute("COPY cards FROM '{}/cards.csv' WITH CSV HEADER DELIMITER AS ','".format(PATH))
	conn.commit()
except Exception as e:
	print(e)
	print("EXCEPTION ON CARDS")




