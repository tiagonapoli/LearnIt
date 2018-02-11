import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card

def add_language(self, user_id, language):
	"""Adds a new language to the database.
		
	Args:
		user_id: An integer representing the user's id.
		language: An string representing the language name.

	Returns:
		A string containing a message to the user. This string can be:
		- "'{}' added successfully to your languages", if the language was successfuly added.
		- "'{}'' is already added", if the language was already added before.
		In the above examples {} means the language name.
	"""
	self.cursor.execute("SELECT language_name FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, treat_str_SQL(language)))
	rows = self.cursor.fetchall()
	for row in rows:
		if row[0] == language:
			return "'{}' is already added".format(language)

	self.cursor.execute("INSERT INTO languages VALUES ({}, '{}');".format(user_id, treat_str_SQL(language)))
	self.conn.commit()
	return "'{}' added successfully to your languages".format(language)



def erase_archive(self, user_id, card_id, counter):
	self.cursor.execute("SELECT type,content_path FROM archives WHERE user_id={} AND user_card_id={} AND counter={}"
					.format(user_id, card_id, counter))
	archives = self.cursor.fetchall()
	if len(archives) == 0:
		print("ERROR in erase_archive, dbapi")
		print("Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter))
		return "Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter); 

	for archive in archives:
		if (archive[0] == 'image' or archive[0] == 'audio') and os.path.exists(archive[1]):
			try:
				os.remove(archive[1])
				print("Erased file {}".format(archive[1]))
			except Exception as e:
				print("ERROR in erase_language - Archive {}".format(archive[1]))
				print(e)

	self.cursor.execute("DELETE FROM archives WHERE user_id={} AND user_card_id={} AND counter={}"
					.format(user_id, card_id, counter))
	self.conn.commit()
	return "Archive successfuly removed"



def get_user_languages(self, user_id):
	"""Gets all the languages that the user added
	
	Args:
		user_id: An integer representing the user's id.

	Returns:
		A list of tuples with the following information abot the languages added by the user:
		- An integer representing the user's id.
		- A string containing the name of the language.
	"""

	languages = []
	self.cursor.execute("SELECT language_name FROM languages WHERE user_id={};".format(user_id))
	rows = self.cursor.fetchall()
	for row in rows:
		languages.append(row[0])

	return languages