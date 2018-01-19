import psycopg2
import os
import time
import datetime
from flashcard import Word
from flashcard import Card

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




	def get_state(self, user_id):
		"""Gets the current state information about the user

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A tuple containing two integers, the primary and secondary states of the user.
		"""
		self.cursor.execute("SELECT state, state2 FROM users WHERE id={}".format(user_id))
		row = self.cursor.fetchall()
		if len(row) == 0:
			return "User doesn't exist"
		return row[0]




	def get_highest_word_id(self, user_id):
		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={}".format(user_id))
		row = self.cursor.fetchall()
		if len(row) == 0:
			return "User doesn't exist"
		return row[0][0]



	def get_highest_card_id(self, user_id):
		self.cursor.execute("SELECT highest_card_id FROM users WHERE id={}".format(user_id))
		row = self.cursor.fetchall()
		if len(row) == 0:
			return "User doesn't exist"
		return row[0][0]





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

		self.cursor.execute("INSERT INTO users VALUES ({}, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT);".format(user_id))
		self.conn.commit()
		return "Welcome to LingoBot!\n" + "Use the command /add_language to add the languages you are interested in learning and then use the command /add_word to add words you are interested in memorizing.\n"




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
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			return "'{}' is not in your languages".format(language)

		self.cursor.execute("SELECT user_card_id FROM cards WHERE user_id={} AND language='{}';".format(user_id, language))
		rows = self.cursor.fetchall()

		for card_id in rows:
			self.cursor.execute("SELECT type, content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, card_id[0]))
			archives = self.cursor.fetchall()
			for archive in archives:
				print(archive[0] + " " + archive[1])
				if archive[0] != 'translation' and os.path.exists(archive[1]):
					try:
						print("Erased file {}".format(archive[1]))
						os.remove(archive[1])
					except Exception as e:
						print("ERROR in erase_language")
						print(e)

		self.cursor.execute("DELETE FROM languages WHERE user_id={} AND language_name='{}';".format(user_id, language))
		self.conn.commit()
		return "'{}' removed successfully".format(language)
	



	def erase_archive(self, user_id, card_id, counter):
		self.cursor.execute("SELECT type,content_path FROM archives WHERE user_id={} AND user_card_id={} AND counter={}"
						.format(user_id, card_id, counter))
		archives = self.cursor.fetchall()
		if len(archives) == 0:
			print("ERROR in erase_archive, dbapi")
			print("Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter))
			return "Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter); 

		for archive in archives:
			if archive[0] != 'translation' and os.path.exists(archive[1]):
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




	def add_card(self, card):
		
		user_id = card.get_user()
		word_id = card.get_word_id()
		language = card.get_language()
		content_type = card.get_type()
		foreign_word = card.get_word()
		topic = card.get_topic()

		self.cursor.execute("SELECT highest_card_id FROM users WHERE id={};".format(user_id))
		rows = self.cursor.fetchall()
		card_id = rows[0][0] + 1

		#Update user's highest_card_id
		self.cursor.execute("UPDATE users SET highest_card_id={} WHERE id={}".format(card_id, user_id))

		self.cursor.execute("INSERT INTO cards VALUES ({}, {}, '{}', '{}', '{}', {}, '{}', {}, {}, {}, '{}')"
			.format(user_id, word_id, language, topic, foreign_word,
					card_id, content_type,
					card.attempts, card.ef, card.interval,
				str(card.next_date.year) + '-' + str(card.next_date.month) + '-' + str(card.next_date.day)))

		self.conn.commit()

		counter = 0
		for path in card.archives:
			counter += 1
			self.cursor.execute("INSERT INTO archives VALUES ({}, {}, {}, '{}', '{}')"
									.format(user_id, card_id, counter, content_type, path))

		self.conn.commit()




	def erase_card(self, user_id, user_card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} AND user_card_id={}"
						.format(user_id, user_card_id))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			print("Error in erase_card, dbapi")
			print("Card {}, {} doesn't exist".format(user_id, user_card_id))
			return "Card {}, {} doesn't exist".format(user_id, user_card_id)

		# erasing archives of the card
		self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
		rows = self.cursor.fetchall()
		for row in rows:
			try:
				os.remove(row[0])
			except Exception as e:
				print(e)

		self.cursor.execute("DELETE FROM cards WHERE user_id={} AND user_card_id={}"
						.format(user_id, user_card_id))
		self.conn.commit()
		return "Card successfuly removed"



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
		language = word.get_language()
		foreign_word = word.get_word()
		topic = word.get_topic()
		cards = word.cards 

		self.cursor.execute("SELECT foreign_word FROM words WHERE user_id={} AND language='{}' AND foreign_word='{}';"
			.format(user_id, language, foreign_word))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "{} is already in your words".format(word.get_word())

		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={};".format(user_id))
		rows = self.cursor.fetchall()
		word_id = rows[0][0] + 1

		#Update user's highest_word_id
		self.cursor.execute("UPDATE users SET highest_word_id={} WHERE id={}".format(word_id, user_id))
		
		self.cursor.execute("INSERT INTO words VALUES ({}, {}, '{}', '{}', '{}')"
			.format(user_id, word_id, language, topic, foreign_word))


		self.conn.commit()
		
		for ctype, card in word.cards.items():
			if card == None:
				continue
			self.add_card(card)

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

		self.cursor.execute("SELECT user_card_id FROM cards WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()

		#erasing cards
		for card in rows:
			self.erase_card(user_id, card[0])

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

		known = []
		self.cursor.execute("SELECT id FROM users;")
		rows = self.cursor.fetchall()
		for row in rows:
			known.append(row[0])

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
		general_info = self.cursor.fetchall()
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} and user_word_id={};".format(user_id, word_id))
		cards_info = self.cursor.fetchall()

		general_info = general_info[0]
		word = Word(general_info[0], general_info[1], general_info[2], general_info[3], general_info[4])


		for card_info in cards_info:
			card = Card(card_info[0], card_info[1], card_info[2], card_info[3], card_info[4],
						card_info[5], card_info[6], 
						card_info[7], card_info[8], card_info[9], card_info[10])

			card_id = card_info[5]
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} and user_card_id={};".format(user_id, card_id))
			paths = self.cursor.fetchall()
			
			for archive in paths:
				card.add_archive(archive[0])

			word.set_card(card)

		return word




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
		row = self.cursor.fetchall()
		
		words = {}
		for word in row:
			words[word[1]] = Word(word[0], word[1], word[2], word[3], word[4])

		self.cursor.execute("SELECT * FROM cards WHERE user_id={};".format(user_id))
		row = self.cursor.fetchall()

		cards = {}
		for card in row:
			cards[card[5]] = Card(card[0], card[1], card[2], card[3], card[4], card[5], card[6], card[7], card[8], card[9], card[10])

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




	def set_supermemo_data(self, card):
		"""Updates on the database the information about the supermemo algorithm that are contained in a word.

		Args:
			word: A Word instance.
		"""
		self.cursor.execute("UPDATE cards SET attempts={}, easiness_factor={}, interval={}, next_date='{}' WHERE user_id={} AND user_card_id={};"
			.format(card.attempts, card.ef, card.interval, card.next_date.strftime('%Y-%m-%d'), card.get_user(), card.get_word_id()))
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
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", None, 'image') 
	card.add_archive('../data/ibagem.jpg')
	word.set_card(card)
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", None, 'audio') 
	card.add_archive('../data/image.png')
	card.add_archive('so pode sobrar euuu')
	word.set_card(card)
	print(test.add_word(word))

	#word2
	word = Word(42,2,"ingels", "wololo", "tiagao")
	card = Card(42,2,"ingels", "wololo", "tiago", 1, 'image') 
	card.add_archive('../data/ingreis.txt')
	word.set_card(card)
	print(test.add_word(word))

	#word3
	word = Word(42,3,"Portuges", "Miscelania", "thalao")
	card = Card(42,3,"Portuges", "Miscelania", "thalao", 1, 'image') 
	card.add_archive('../data/talao.txt')
	word.set_card(card)
	print(test.add_word(word))

	#get_all_words_info
	print("\n-----------------LISTA-----------------\n")
	words = test.get_all_words_info(42)
	for word in words:
		print(word)

	#erase_card Portuges
	print("-----------------Delete card-----------------\n\n")
	print(test.erase_card(42,1))

	#erase_language Ingels
	print("-----------------Delete language Ingels-----------------\n\n")
	print(test.erase_language(42, 'ingels'))

	words = test.get_all_words_info(42)
	for word in words:
		print(word)

	#erase_word thalao
	print("-----------------Delete word thalao-----------------\n\n")
	print(test.erase_word(42, 3))

	words = test.get_all_words_info(42)
	for word in words:
		print(word)

	#erase_archive 
	print("-----------------Erase archive-----------------\n\n")
	print(test.erase_archive(42,2,1))

	#get_word
	print("-----------------Get word test-----------------\n\n")
	print(test.get_word(42,1))

