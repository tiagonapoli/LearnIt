import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card

import database_ops.word_ops
import database_ops.user_ops
import database_ops.topic_ops
import database_ops.language_ops
import database_ops.card_ops
import database_ops.archive_ops
import database_ops.specialword_ops



'''
	Database Implementation
'''


class Database():
	"""Class that controls the database operations.

	Uses Postgres as object-relational database management system
	
	Attributes:
		conn: Handles the connection to a Postgres database instance.
		cursor: Allows python code to execute Postgres command in a database session.
	"""

	def __init__(self, debug_mode):
		#try:
		arq = None
		if debug_mode:
			arq = open("../credentials/connect_str_debug.txt", "r")
		else:
			arq = open("../credentials/connect_str.txt", "r")
		connect_str = arq.read()
		self.DB_NAME = connect_str.split()[0][7:]
		self.DB_USER_NAME = connect_str.split()[1][5:]
		print("DB_NAME: {}".format(self.DB_NAME))
		print("DB_USER_NAME: {}".format(self.DB_USER_NAME))
		print(connect_str)
		arq.close()
		# use our connection values to establish a connection
		self.conn = psycopg2.connect(connect_str)
		# create a psycopg2 cursor that can execute queries
		self.cursor = self.conn.cursor()
		print("Connected with database!")
		
		self.word_ops = database_ops.word_ops.WordOps(self.conn, self.cursor, debug_mode)
		self.archive_ops = database_ops.archive_ops.ArchiveOps(self.conn, self.cursor, debug_mode)
		self.user_ops = database_ops.user_ops.UserOps(self.conn, self.cursor, debug_mode)
		self.topic_ops = database_ops.topic_ops.TopicOps(self.conn, self.cursor, debug_mode)
		self.language_ops = database_ops.language_ops.LanguageOps(self.conn, self.cursor, debug_mode)
		self.card_ops = database_ops.card_ops.CardOps(self.conn, self.cursor, debug_mode)
		self.specialword_ops = database_ops.specialword_ops.SpecialWordOps(self.conn, self.cursor, debug_mode)


	def __del__(self):
		self.conn.close()
		self.cursor.close()


	#==================WORD ops==================
	def get_highest_word_id(self, user_id):
		return self.word_ops.get_highest_word_id(user_id)

	def add_word(self, word):
		return self.word_ops.add_word(word)

	def erase_word(self, user_id, word_id):
		return self.word_ops.erase_word(user_id, word_id)
	
	def get_word(self, user_id, word_id):
		return self.word_ops.get_word(user_id, word_id)

	def get_all_words(self, user_id):
		return self.word_ops.get_all_words(user_id)

	def get_words_on_topic(self, user_id, language, topic):
		return self.word_ops.get_words_on_topic(user_id, language, topic)

	def check_word_existence(self, user_id, language, topic, foreign_word):
		return self.word_ops.check_word_existence(user_id, language, topic, foreign_word)

	#==================SPECIALWORD ops==================
	def erase_specialword(self, word):
		return self.specialword_ops.erase_specialword(word)

	def add_specialword(self, word):
		return self.specialword_ops.add_specialword(word)


	#==================USER ops==================
	def get_state(self, user_id):
		return self.user_ops.get_state(user_id)

	def set_state(self, user_id, state1, state2, state3):
		return self.user_ops.set_state(user_id, state1, state2, state3)

	
	def add_user(self, user_id, username):
		return self.user_ops.add_user(user_id, username)

	def get_known_users(self):
		return self.user_ops.get_known_users()

	def get_learning_words_limit(self, user_id):
		return self.user_ops.get_learning_words_limit(user_id)

	def get_review_cards_day_limit(self, user_id):
		return self.user_ops.get_review_cards_day_limit(user_id)

	def get_grade_waiting(self, user_id):
		return self.user_ops.get_grade_waiting(user_id)

	def set_grade_waiting(self, user_id, grade):
		return self.user_ops.set_grade_waiting(user_id, grade)

	def set_card_waiting(self, user_id, card_id):
		return self.user_ops.set_card_waiting(user_id, card_id)


	def get_card_waiting(self, user_id):
		return self.user_ops.get_card_waiting(user_id)

	def get_card_waiting_type(self, user_id):
		return self.user_ops.get_card_waiting_type(user_id)

	def set_card_waiting_type(self, user_id, card_waiting_type):
		return self.user_ops.set_card_waiting_type(user_id, card_waiting_type)

	def get_cards_per_hour(self, user_id):
		return self.user_ops.get_cards_per_hour(user_id)

	def set_cards_per_hour(self, user_id, cards_per_hour):
		return self.user_ops.set_cards_per_hour(user_id, cards_per_hour)

	def get_active(self, user_id):
		return self.user_ops.get_active(user_id)

	def set_active(self, user_id, active):
		return self.user_ops.set_active(user_id, active)

	def get_id_by_username(self, username):
		return self.user_ops.get_id_by_username(username)	

	def get_public(self, user_id):
		return self.user_ops.get_public(user_id)

	def set_public(self, user_id, public):
		return self.user_ops.set_public(user_id, public)

	def get_username(self, user_id):
		return self.user_ops.get_username(user_id)

	#==================TOPIC ops==================
	def add_topic(self, user_id, language, topic):
		return self.topic_ops.add_topic(user_id, language, topic)

	def get_all_topics(self, user_id, language):
		return self.topic_ops.get_all_topics(user_id, language)

	def erase_topic_empty_words(self, user_id, language, topic):
		return self.topic_ops.erase_topic_empty_words(user_id, language, topic)


	#=================CARD ops===================

	def get_highest_card_id(self, user_id):
		return self.card_ops.get_highest_card_id(user_id)


	def add_card(self, card):
		return self.card_ops.add_card(card)


	def get_card(self, user_id, user_card_id):
		return self.card_ops.get_card(user_id, user_card_id)


	def erase_card(self, user_id, user_card_id):
		return self.card_ops.erase_card(user_id, user_card_id)


	def set_supermemo_data(self, card):
		return self.card_ops.set_supermemo_data(card)

	def get_cards_on_topic(self, user_id, language, topic, get_default):
		return self.card_ops.get_cards_on_topic(user_id, language, topic, get_default)

	def get_all_cards(self, user_id):
		return self.card_ops.get_all_cards(user_id)


	def check_card_existence(self, user_id, card):
		return self.card_ops.check_card_existence(user_id, card)

	#==================ARCHIVE ops==================
	def erase_archive(self, user_id, card_id, counter):
		return self.archive_ops.erase_archive(user_id, card_id, counter)


	#==================LANGUAGE ops==================
	def add_language(self, user_id, language):
		return self.language_ops.add_language(user_id, language)

	def erase_language(self, user_id, language):
		return self.language_ops.erase_language(user_id, language)

	def get_user_languages(self, user_id):
		return self.language_ops.get_user_languages(user_id)


	def backup(self, PATH):
		try:
			if not os.path.exists(PATH):
				os.mkdir(PATH)
			if not os.path.exists(PATH + "/tables/"):
				os.mkdir(PATH + "/tables/")
			aux_path = PATH + "/tables"
			os.system("psql -U {} -d {} -c \"Copy (Select * From users) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/users.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From cards) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/cards.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From languages) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/languages.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From topics) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/topics.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From words) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/words.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From archives) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/archives.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From specialwords) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/specialwords.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			return "Backup made successfully"
		except Exception as e:
			print(e);
			return "Backup failed"

if __name__ == '__main__':
	
	test = Database()

	#create files to debug
	file = open('../data/ibagem.jpg', 'w')
	file.write('olar')
	file.close()

	file = open('../data/image.png', 'w')
	file.write('olar2')
	file.close()

	file = open('../data/ingreis.txt', 'w')
	file.write('olar3')
	file.close()

	file = open('../data/talao.txt', 'w')
	file.write('olar4')
	file.close()
	#Add user and languages
	print(test.add_user(42))
	print(test.add_user(84))

	#highest card/word id
	print("-----------------Highest Card/Word ID-----------------")
	print(test.get_highest_card_id(42))
	print(test.get_highest_word_id(84))

	#Get known users
	print("-----------------Get known Users-----------------")
	print(str(test.get_known_users()) + "\n\n")

	print(test.add_language(42,"Portuges"))
	print(test.add_language(42,"ingels"))
	
	#Get user languages
	print("-----------------Get user languages-----------------")
	print(str(test.get_user_languages(42)) + "\n\n")

	#Add words
	print("-----------------Add words-----------------")
	#word1
	word = Word(42,1,"Portuges", "Miscelania", "Camargao")
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", 1, 'image') 
	card.add_archive('../data/ibagem.jpg')
	word.set_card(card)
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", 2, 'audio') 
	card.add_archive('../data/image.png')
	card.add_archive('so pode sobrar euuu')
	word.set_card(card)
	print(test.add_word(word))

	#word2
	word = Word(42,2,"ingels", "wololo", "tiagao")
	card = Card(42,2,"ingels", "wololo", "tiagao", 3, 'image') 
	card.add_archive('../data/ingreis.txt')
	word.set_card(card)
	print(test.add_word(word))

	#word3
	word = Word(42,3,"Portuges", "MEGAS XLR", "thalao")
	card = Card(42,3,"Portuges", "MEGAS XLR", "thalao", 4, 'image') 
	card.add_archive('../data/talao.txt')
	word.set_card(card)
	print(test.add_word(word))

	#get_all_words
	print("\n-----------------LISTA-----------------\n")
	words = test.get_all_words(42)
	for word in words:
		print(word)

	#get_all_topics
	print("\n-----------------GET ALL TOPICS Portuges-----------------\n")
	print(str(test.get_all_topics(42, 'Portuges')))

	#get_words_on_topic
	print("\n-----------------GET WORDS ON TOPICS-----------------\n")
	words = test.get_words_on_topic(42, 'Portuges', 'Miscelania')
	print('----Miscelania----')
	for word in words:
		print(word)

	print('\n----MEGAS XLR----')
	words = test.get_words_on_topic(42, 'Portuges', 'MEGAS XLR')
	for word in words:
		print(word)


	#Get cards on topic
	print("\n-----------------GET CARDS ON TOPICS-----------------\n")
	cards = test.get_cards_on_topic(42, 'Portuges', 'Miscelania', True)
	print('----Miscelania com DEFAULT----')
	for card in cards:
		print(card)

	print('\n----MEGAS XLR sem DEFAULT----')
	cards = test.get_cards_on_topic(42, 'Portuges', 'MEGAS XLR', False)
	for card in cards:
		print(card)

	#erase_card Portuges
	print("-----------------Delete card-----------------\n\n")
	print(test.erase_card(42,1))

	#erase_language Ingels
	print("-----------------Delete language Ingels-----------------\n\n")
	print(test.erase_language(42, 'ingels'))

	words = test.get_all_words(42)
	for word in words:
		print(word)

	#erase_word thalao
	print("-----------------Delete word thalao-----------------\n\n")
	print(test.erase_word(42, 3))

	words = test.get_all_words(42)
	for word in words:
		print(word)

	#erase_archive 
	print("-----------------Erase archive-----------------\n\n")
	print(test.erase_archive(42,2,1))

	#get_word
	print("-----------------Get word test-----------------\n\n")
	print(test.get_word(42,1))

	print(test.backup())

