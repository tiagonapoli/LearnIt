import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card

import database_ops.word_ops
import database_ops.user_methods
import database_ops.topic_methods
import database_ops.language_methods
import database_ops.card_methods
import database_ops.archive_methods



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

	def __init__(self):
		try:
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
			self.word_ops = database_ops.word_ops.WordOps(self.conn, self.cursor)

		except Exception as e:
			print("Uh oh, can't connect. Invalid dbname, user or password?")
			print("Exception: {}".format(e))


	def __del__(self):
		self.conn.close()
		self.cursor.close()


	#==================WORD METHODS==================
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



	#==================USER METHODS==================
	get_state = database_ops.user_methods.get_state
	set_state = database_ops.user_methods.set_state
	add_user = database_ops.user_methods.add_user
	get_known_users = database_ops.user_methods.get_known_users


	#==================TOPIC METHODS==================
	add_topic = database_ops.topic_methods.add_topic
	get_all_topics = database_ops.topic_methods.get_all_topics
	get_words_on_topic = database_ops.topic_methods.get_words_on_topic
	erase_topic_empty_words = database_ops.topic_methods.erase_topic_empty_words


	#==================LANGUAGE METHODS==================
	add_language = database_ops.language_methods.add_language
	erase_language = database_ops.language_methods.erase_language
	get_user_languages = database_ops.language_methods.get_user_languages


	#==================CARD METHODS==================
	get_highest_card_id = database_ops.card_methods.get_highest_card_id
	add_card = database_ops.card_methods.add_card
	get_card = database_ops.card_methods.get_card
	erase_card = database_ops.card_methods.erase_card
	set_card_waiting = database_ops.card_methods.set_card_waiting
	get_card_waiting = database_ops.card_methods.get_card_waiting


	#==================ARCHIVE METHODS==================
	erase_archive = database_ops.archive_methods.erase_archive


	def backup(self):
		try:
			if not os.path.exists("../backup/"):
				os.mkdir("../backup/")
			if not os.path.exists("../backup/tables/"):
				os.mkdir("../backup/tables/")
			os.system("psql -U {} -d {} -c \"Copy (Select * From users) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/users.csv".format(self.DB_USER_NAME, self.DB_NAME))
			os.system("psql -U {} -d {} -c \"Copy (Select * From cards) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/cards.csv".format(self.DB_USER_NAME, self.DB_NAME))
			os.system("psql -U {} -d {} -c \"Copy (Select * From languages) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/languages.csv".format(self.DB_USER_NAME, self.DB_NAME))
			os.system("psql -U {} -d {} -c \"Copy (Select * From topics) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/topics.csv".format(self.DB_USER_NAME, self.DB_NAME))
			os.system("psql -U {} -d {} -c \"Copy (Select * From words) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/words.csv".format(self.DB_USER_NAME, self.DB_NAME))
			os.system("psql -U {} -d {} -c \"Copy (Select * From archives) To STDOUT With CSV HEADER DELIMITER ',';\" > ../backup/tables/archives.csv".format(self.DB_USER_NAME, self.DB_NAME))
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

