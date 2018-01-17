import psycopg2
import os
import time
import datetime
from flashcard import TimeControl

class Database:
	"""Class that controls the database operations.

	Uses Postgres as object-relational database management system
	
	Attributes:
		conn: Handles the connection to a Postgres database instance.
		cursor: Allows python code to execute Postgres command in a database session.
	"""

	def __init__(self):
		try:
			arq = open("../credentials/connect_str.txt", "r")
			connect_str = arq.read()
			arq.close()
			print(connect_str)
			# use our connection values to establish a connection
			self.conn = psycopg2.connect(connect_str)
			# create a psycopg2 cursor that can execute queries
			self.cursor = self.conn.cursor()
			print("Connected with database!")
		except Exception as e:
			print("Uh oh, can't connect. Invalid dbname, user or password?")
			print(e)

	def __del__(self):
		self.conn.close()
		self.cursor.close()

	def add_user(self, user_id):
		"""Adds a new user to the database.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Welcome to LingBot", if the user was not registered.
			- "Welcome back to LingoBot", if the user was already registered.
		"""

		self.cursor.execute("SELECT id from users WHERE id={};".format(user_id))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "Welcome back to LingoBot!"

		self.cursor.execute("INSERT INTO users VALUES ({}, DEFAULT, DEFAULT, DEFAULT, DEFAULT);".format(user_id))
		self.conn.commit()
		return "Welcome to LingoBot!\n" + "Use the command \\add_language to add the languages you are interested in learning and then use the command \\add_word to add words you are interested in memorizing.\n"

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
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, language))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == language:
				return "'{}' is already added".format(language)

		self.cursor.execute("INSERT INTO languages VALUES ({}, '{}');".format(user_id, language))
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
		self.cursor.execute("SELECT language_name FROM languages WHERE language_name={};".format(language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			return "'{}' is not in your languages".format(language)

		self.cursor.execute("DELETE FROM languages WHERE user_id={} AND language_name={};".format(user_id, language))
		self.conn.commit()
		return "'{}' removed successfully".format()

	def add_word(self, user_id, lst):
		"""Adds a new word to the database.
		
		Args:
			user_id: An integer representing the user's id.
			lst: A list containing: language, word in foreign language, word in english, path to content 1,
				path to content 2, ..., path to content n

		Returns:
			A string containing a message to the user. This string can be:
			- "Word and content added successfully!", if the operation succeeds.
			- "{} is already in your words".
			In the above example, {} means the word which is beeing added.
		"""
		
		language = lst[0]
		foreign_word = lst[1]
		english_word = lst[2]
		content_type = lst[3]

		self.cursor.execute("SELECT foreign_word FROM words WHERE user_id={} AND language='{}' AND foreign_word='{}';"
			.format(user_id, language, foreign_word))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "{} is already in your words"

		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={};".format(user_id))
		rows = self.cursor.fetchall()
		user_word_id = rows[0][0] + 1

		#Update user's highest_word_id
		self.cursor.execute("UPDATE users SET highest_word_id={} WHERE id={}".format(user_word_id, user_id))
		
		fc = TimeControl()
		self.cursor.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}', {}, {}, {}, {}, '{}')"
			.format(user_id, language, foreign_word, english_word, user_word_id,
				fc.attempts, fc.ef, fc.interval,
				str(fc.next_date.year) + '-' + str(fc.next_date.month) + '-' + str(fc.next_date.day)))
		
		self.conn.commit()

		counter = 0
		# From the fourth element on we have the paths to the contents
		for i in range(4, len(lst)):
			content_path = lst[i]
			self.cursor.execute("INSERT INTO content VALUES ({}, '{}', '{}', {}, '{}', {}, '{}');"
				.format(user_id, language, foreign_word, user_word_id, content_type, counter, content_path))
			counter += 1

		self.conn.commit()
		return "Word and content added successfully!"

	def erase_word(self, user_id, word_id):
		"""Erases a word from the database.

		Args:
			user_id: An integer representing the user's id.
			word_id: An integer representing the word's id between all the user's words.

		Returns:
			A string containing a message to the user. This string can be:
			- "Word erased successfully!", if the operation succeeds.
			- "Invalid word", if the operation fails.
		"""
		self.cursor.execute("SELECT * FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()
		
		if len(rows) == 0:
			return "Invalid word"

		# erasing content of the word
		self.cursor.execute("SELECT content_path FROM content WHERE user_id={} user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()
		for row in rows:
			os.remove(row[0])

		# erasing the word from the database
		self.cursor.execute("DELETE FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))

		self.conn.commit()
		return "Word erased successfully!"

	def get_known_users(self):
		"""Gets all the columns of all users in the database
		
		Returns:
			A list of tuples with the following information about the users:
			- An integer representing the user's id.
			- An integer representing the number of messages the user will receive per day.
			- An integer representing the current primary state of the user.
			- An integer representing the current secondary state of the user.
		"""

		known = set()
		self.cursor.execute("SELECT id FROM users;")
		rows = self.cursor.fetchall()
		for row in rows:
			known.add(row[0])

		return known

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

	def get_word(self, user_id, word_id):
		"""Gets all the information about the select word of the user.
		
		Args:
			user_id: An integer representing the user's id.
			word_id: An integer representing the word's id between the user's words.

		Returns:
			A tuble with the following information:
			- An integer representing the user's id.
			- A string containing the language that the word belongs.
			- A string containing the word in the foreign language.
			- A string containing the translation in english of the word.
			- An integer representing the id of the word between the user's words.
			- An integer containing the number of attempts the user did for this word.
			- A real number representing the current easiness factor of the word.
			- A real number representing the interval time between consecutive send of the word.
			- A string representing the date of the next send of the word, in the form yyyy-mm-dd.
		"""
		self.cursor.execute("SELECT * FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()
		return rows[0]

	def get_all_words_info(self, user_id):
		"""Gets all the information about all the words of the user
	
		Args:
			user_id: An integer representing the user's id.

		Returns:
			A list of tuples with the following information about the words:
			- An integer representing the user's id.
			- A string containing the language that the word belongs.
			- A string containing the word in the foreign language.
			- A string containing the translation in english of the word.
			- An integer representing the id of the word between the user's words.
			- An integer containing the number of attempts the user did for this word.
			- A real number representing the current easiness factor of the word.
			- A real number representing the interval time between consecutive send of the word.
			- A string representing the date of the next send of the word, in the form yyyy-mm-dd.
		"""
		self.cursor.execute("SELECT * FROM words WHERE user_id={};".format(user_id))
		rows = self.cursor.fetchall()
		return rows

	def get_content_type_and_paths(self, user_id, word_id):
		"""Gets all the content associated with a word"""
		self.cursor.execute("SELECT type, content_path FROM content WHERE user_id={} AND user_word_id={}"
			.format(user_id, word_id))
		rows = self.cursor.fetchall()
		return rows


	def set_supermemo_data(self, word):
		"""Updates on the database the information about the supermemo algorithm that are contained in a word.

		Args:
			word: A Word instance.
		"""
		self.cursor.execute("UPDATE words SET attempts={}, easiness_factor={}, interval={}, next_date='{}' WHERE user_id={} AND user_word_id={};"
			.format(word.attempts, word.ef, word.interval, word.next_date.strftime('%Y-%m-%d'), word.user_id, word.word_id))
		self.conn.commit()

	def set_state(self, user_id, state, state2):
		"""Updates on the database the state information about the user
			
		Args:
			user_id: An integer representing the user's id.
			state: An integer representing the user's primary state.
			state2: An integer representing the user's secondary state.
		"""
		self.cursor.execute("UPDATE users SET state={}, state2={} WHERE id={}".format(state, state2, user_id))
		self.conn.commit()

	def get_state(self, user_id):
		"""Gets the current state information about the user

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A tuple containing two integers, the primary and secondary states of the user.
		"""
		self.cursor.execute("SELECT state, state2 FROM users WHERE id={}".format(user_id))
		rows = self.cursor.fetchall()
		return rows[0]

	def get_highest_word_id(self, user_id):
		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={}".format(user_id))
		rows = self.cursor.fetchall()
		return rows[0][0]
