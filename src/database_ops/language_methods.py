import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card
from database_ops.db_utils import treat_str_SQL


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

def erase_language(self, user_id, language):
	"""Erases a language from the database.
	
	Args:
		user_id: An integer representing the user's id.
		language: An string representing the language name.
	Returns:
		A string containing a message to the user. This string can be:
		- "'{}' removed successfully", if the operation succeeds.
		- "'{}' is not in your languages", if the language is not in the database.
		In the above examples {} means the language name.
	"""
	self.cursor.execute("SELECT language_name FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, treat_str_SQL(language)))
	rows = self.cursor.fetchall()
	if(len(rows) == 0):
		return "'{}' is not in your languages".format(language)

	self.cursor.execute("SELECT user_word_id FROM words WHERE user_id={} AND language='{}';".format(user_id, treat_str_SQL(language)))
	words = self.cursor.fetchall()

	for word in words:
		self.erase_word(user_id, word[0])

	self.cursor.execute("DELETE FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, treat_str_SQL(language)))
	self.conn.commit()
	return "'{}' removed successfully".format(language)


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