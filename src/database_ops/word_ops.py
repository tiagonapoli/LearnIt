import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card
from database_ops.db_utils import treat_str_SQL, create_card_with_row, create_word_with_row
from utilities import utils
import database_ops.topic_ops
import database_ops.card_ops
import database_ops.specialword_ops


class WordOps():

	def __init__(self, conn, cursor):
		self.conn = conn
		self.cursor = cursor
		self.topic_ops = database_ops.topic_ops.TopicOps(conn,cursor)
		self.card_ops = database_ops.card_ops.CardOps(conn,cursor)
		self.specialword_ops = database_ops.specialword_ops.SpecialWordOps(self.conn, self.cursor)


	def get_highest_word_id(self, user_id):
		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={}".format(user_id))
		row = self.cursor.fetchall()
		if len(row) == 0:
			return "User doesn't exist"
		return row[0][0]

	def add_word(self, word):
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
		user_id = word.get_user()
		word_id = word.get_word_id()
		language = word.get_language()
		foreign_word = word.get_word()
		topic = word.get_topic()
		cards = word.cards 

		self.cursor.execute("SELECT foreign_word FROM words WHERE user_id={} AND language='{}' AND topic='{}' AND foreign_word='{}';"
			.format(user_id, treat_str_SQL(language), treat_str_SQL(topic) ,treat_str_SQL(foreign_word)))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "{} is already in your words".format(word.get_word())

		self.topic_ops.add_topic(user_id, language, topic)

		#Update user's highest_word_id
		self.cursor.execute("UPDATE users SET highest_word_id={} WHERE id={}".format(word_id, user_id))
		
		self.cursor.execute("INSERT INTO words VALUES ({}, {}, '{}', '{}', '{}')"
			.format(user_id, word_id, treat_str_SQL(language), treat_str_SQL(topic), treat_str_SQL(foreign_word)))

		self.conn.commit()
		
		for ctype, card in word.cards.items():
			if card == None:
				continue
			self.card_ops.add_card(card)

		if utils.check_special_word(word.get_word()):
			self.specialword_ops.add_specialword(word)

		return "Word '{}' and content added successfully!".format(foreign_word)

	def check_word_existence(self, user_id, language, topic, foreign_word):
		self.cursor.execute("SELECT user_word_id FROM words WHERE user_id={} AND language='{}' AND topic='{}' AND foreign_word='{}';"
			.format(user_id, treat_str_SQL(language), treat_str_SQL(topic) ,treat_str_SQL(foreign_word)))
		rows = self.cursor.fetchall()
		if len(rows) > 0:
			return True, rows[0][0]
		return False, -1

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

		self.cursor.execute("SELECT language,topic,foreign_word FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			return "Invalid word"

		language = rows[0][0]
		topic = rows[0][1]
		word_text = rows[0][2]

		self.cursor.execute("SELECT user_card_id FROM cards WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()

		#erasing cards
		for card in rows:
			self.card_ops.erase_card(user_id, card[0])

		# erasing the word from the database
		self.cursor.execute("DELETE FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		self.conn.commit()

		if utils.check_special_word(word_text):
			self.specialword_ops.erase_specialword(word_text)

		#maybe erase topic
		self.cursor.execute("SELECT topic FROM words WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			self.topic_ops.erase_topic_empty_words(user_id, language, topic)

		if os.path.exists('../data/{}/{}'.format(user_id, word_id)):
				try:
					os.rmdir('../data/{}/{}'.format(user_id, word_id))
					print("Erased directory {}".format('../data/{}/{}'.format(user_id, word_id)))
				except Exception as e:
					print("ERROR in erase_word - directory {}".format('../data/{}/{}'.format(user_id, word_id)))
					print(e)

		return "Word {} erased successfully!".format(word_text)


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
		general_info = self.cursor.fetchall()
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} and user_word_id={};".format(user_id, word_id))
		cards_info = self.cursor.fetchall()

		general_info = general_info[0]
		word = create_word_with_row(general_info)


		for card_info in cards_info:
			card = create_card_with_row(card_info)

			card_id = card_info[5]
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} and user_card_id={};".format(user_id, card_id))
			paths = self.cursor.fetchall()
			
			for archive in paths:
				card.add_archive(archive[0])

			word.set_card(card)

		return word


	def get_all_words(self, user_id):
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
		row = self.cursor.fetchall()
		
		words = {}
		for word in row:
			words[word[1]] = create_word_with_row(word)

		self.cursor.execute("SELECT * FROM cards WHERE user_id={};".format(user_id))
		row = self.cursor.fetchall()

		cards = {}
		for card in row:
			cards[card[5]] = create_card_with_row(card)

		self.cursor.execute("SELECT * FROM archives WHERE user_id={};".format(user_id))
		row = self.cursor.fetchall()

		for archive in row:
			cards[archive[1]].add_archive(archive[4])

		for card_id, card in cards.items():
			words[card.get_word_id()].set_card(card)

		ret = []
		for word_id, word in words.items():
			ret.append(word)

		return ret


	def get_words_on_topic(self, user_id, language, topic):
		self.cursor.execute("SELECT user_id,user_word_id FROM words WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
		words = self.cursor.fetchall()

		ret = []
		for word in words:
			ret.append(self.get_word(word[0],word[1]))

		return ret


	