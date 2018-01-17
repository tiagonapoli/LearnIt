from dbapi import Database
from datetime import datetime
from flashcard import Card

class RuntimeData: 
	"""Class that do all the runtime data management.
		Includes methods that encapsulates the access to the database.

		Attributes:
			db: A Database instance.
			known_users: A list of User instances.
			loop: A dictionary that associates each user with a list of objects that weren't yet processed.
				Auxiliary structure to some bot message handler.
			temp_user: An auxiliary dictionary structure to some bot message handlers. Keeps a list of temporary items.
			map_state: A dictionary that associates an integer state with a string state.
			map_stateInv: A dictionary that associates an string state to a integer state.
			counter_user: An auxiliary dictionary struct to some bot message handlers. 
	"""

	def __init__(self):
		self.db = Database()
		self.known_users = self.db.get_known_users()
		self.loop = {}
		self.temp_user = {}
		self.map_state = {0 : '0',
						1 : 'WAITING_ANS',
						2 : 'WAITING_POLL_ANS',
						3 : '1_0',
						4 : '1_1',
						5 : '1_2',
						6 : '1_3',
						7 : '1_3-opt1',
						8 : '1_3-opt1_1',
						9 : '1_3-opt2',
						10: '1_3-opt2_1',
						11: '1_3-opt3',
						12: '1_3-opt3_1',
						13: '2_0',
						14: 'LOCKED'
						}
		self.map_stateInv = {}
		self.counter_user = {}
		
		for key,val in self.map_state.items():
			self.map_stateInv[val] = key

	def add_user(self,user_id):
		"""Register a new user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Welcome to LingBot", if the user was not registered.
			- "Welcome back to LingoBot", if the user was already registered.
		"""
		self.known_users.add(user_id)
		return self.db.add_user(user_id)
	
	def add_word(self,user_id):
		"""Adds a new word to the user's words.
	
		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Word and content added successfully!", if the operation succeeds.
			- "{} is already in your words".
			In the above example, {} means the word which is beeing added.
		"""
		lista = self.temp_user[user_id]
		print("lista[{}] = ".format(user_id) + str(lista))
		return self.db.add_word(user_id,lista)
	
	def get_user_languages(self, user_id):
		"""Gets all the languages added by the user.
		
		Args:
			user_id: An integer representing the user's id.

		Returns:
			A list of tuples with the following information abot the languages added by the user:
			- An integer representing the user's id.
			- A string containing the name of the language.
		"""
		return self.db.get_user_languages(user_id)
	
	def add_language(self, user_id, language):
		"""Register a new language to the user.

		Args:
			user_id: An integer representing the user's id.
			language: A string containing the language name.

		Returns:
			A string containing a message to the user. This string can be:
			- "'{}' added successfully to your languages", if the language was successfuly added.
			- "'{}'' is already added", if the language was already added before.
			In the above examples {} means the language name.
		""" 
		return self.db.add_language(user_id,language)

	def erase_word(self,user_id, word_id):
		return self.db.erase_word(user_id, word_id)

	def get_state(self, user_id):
		"""Gets the primary state of the user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			An integer representing the primary state of the user.
		"""

		st1,st2 = self.db.get_state(user_id)
		st1 = self.map_state[st1]
		print("id:{}  state:{}".format(user_id,st1))
		return st1

	def get_state2(self, user_id):
		"""Gets the secondary state of the user
		
		Args:
			user_id: An integer representing the user's id.

		Returns:
			An integer representing the secondary state of the user.
		"""

		st1,st2 = self.db.get_state(user_id)
		return st2

	def set_state(self, user_id, new_state, new_state2=0):
		"""Updates the primary and secondary state of some user
			
		Args:
			user_id: An integer representing the user's id.
			new_state: An integer representing the new primary state of the user.
			new_state2: An integer representing the new secondary state of the user.
		"""
		print("{} NEW STATE {} {}".format(user_id, new_state, new_state2))
		self.db.set_state(user_id, self.map_stateInv[new_state], new_state2)

	def get_word_info(self, user_id, word_id):
		"""Gets the Card instance corresponding to some word
	
		Args:
			user_id: An integer representing the user's id.
			word_id: An integer representing the id of a word between all the user's words.

		Returns:
			A Word instace identified by the user_id and the word_id.
		"""
		info = self.db.get_word(user_id, word_id)
		content_info = self.db.get_content_type_and_paths(user_id, word_id)
		card_type = content_info[0][0]
		paths = []
		for content_type,content_path in content_info:
			paths.append(content_path)

		word = Card(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], datetime.combine(info[8], datetime.min.time()),
			card_type, paths)
		return word

	def get_all_words_info(self, user_id):
		"""Gets all the information about all the words of a user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A list of Word instances.
		""" 

		rows = self.db.get_all_words_info(user_id)
		words = []
		for row in rows:
			word_id = row[4]
			content_info = self.db.get_content_type_and_paths(user_id, word_id)
			card_type = content_info[0][0]
			paths = []
			for content_type,content_path in content_info:
				paths.append(content_path)

			words.append(Card(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], datetime.combine(row[8], datetime.min.time())),
				card_type, paths)
		return words

	def set_supermemo_data(self, word_id):
		"""Sets the data of some word about the supermemo algorithm.

		Args:
			word_id: An integer representing the id of a word between all the user's words.
		"""
		self.db.set_supermemo_data(word_id)

	def reset_all_states(self):
		"""Sets the states of all users to the initial state"""

		for user in self.known_users:
			self.set_state(user, '0')

	def get_highest_word_id(self, user_id):
		return self.db.get_highest_word_id(user_id)

	def not_locked(self, user_id):
		if self.get_state(user_id) == 'LOCKED':
			return False
		return True
