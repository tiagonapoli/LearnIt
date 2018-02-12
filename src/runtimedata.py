from dbapi import Database
from datetime import datetime
from flashcard import Word,Card
import fsm
import abc


class User:

	def __init__(self, user_id, database_reference):
		self.db = database_reference
		self.user_id = user_id
		self.temp_word = None
		self.temp_card = None
		self.temp_words_list = None
		self.btn_set = None
		self.keyboard_options = None
		self.receive_queue = None
		self.cards_to_review = None
		self.temp_language = None
		self.counter = None
		self.review_card_number = None
		self.pos = None


	def get_state(self):
		"""Gets the primary state of the user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			An integer representing the primary state of the user.
		"""

		st = self.db.get_state(self.user_id)
		ret = (st[0],)
		for i in range(1,3):
			if(st[i] == -1):
				break
			ret = ret + (st[i],)

		if len(ret) == 1:
			ret = ret[0]

		print("id:{}  state:{}".format(self.user_id,ret))
		return ret


	def set_state(self, state):
		"""Updates the primary and secondary state of some user
			
		Args:
			user_id: An integer representing the user's id.
			new_state: An integer representing the new primary state of the user.
			new_state2: An integer representing the new secondary state of the user.
		"""

		if type(state) != tuple:
			state = (state, -1, -1)
		else:
			while len(state) < 3:
				state = state + (-1,)

		print("{} NEW STATE {} {} {}".format(self.user_id, state[0], state[1], state[2]))
		self.db.set_state(self.user_id, state[0], state[1], state[2])


	def get_card(self, card_id):
		return self.db.get_card(self.user_id, card_id)


	def add_word(self, word):
		"""Adds a new word to the user's words.
	
		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Word and content added successfully!", if the operation succeeds.
			- "{} is already in your words".
			In the above example, {} means the word which is beeing added.
		"""
		print("---Word to add user {}---".format(word.user_id))
		print(word)
		return self.db.add_word(word)


	def erase_word(self, word_id):
		return self.db.erase_word(self.user_id, word_id)


	def add_language(self, language):
		"""Register a new language to the user.

		Args:
			user_idd: An integer representing the user's id.
			language: A string containing the language name.

		Returns:
			A string containing a message to the user. This string can be:
			- "'{}' added successfully to your languages", if the language was successfuly added.
			- "'{}'' is already added", if the language was already added before.
			In the above examples {} means the language name.
		""" 
		return self.db.add_language(self.user_id,language)


	def get_languages(self):
		"""Gets all the languages added by the user.
		
		Args:
			user_id: An integer representing the user's id.

		Returns:
			A list of tuples with the following information abot the languages added by the user:
			- An integer representing the user's id.
			- A string containing the name of the language.
		"""
		return self.db.get_user_languages(self.user_id)
	

	def get_word(self, word_id):
		"""Gets the Card instance corresponding to some word
	
		Args:
			user_id: An integer representing the user's id.
			word_id: An integer representing the id of a word between all the user's words.

		Returns:
			A Word instace identified by the user_idd and the word_id.
		"""
		return self.db.get_word(self.user_id, word_id)


	def get_all_words(self):
		"""Gets all the information about all the words of a user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A list of Word instances.
		""" 
		return self.db.get_all_words(self.user_id)


	def get_words_on_topic(self, language, topic):
		return self.db.get_words_on_topic(self.user_id, language, topic)


	def get_string_words_on_topic(self, language, topic):
		lst = self.db.get_words_on_topic(self.user_id, language, topic)
		ret = []
		for word in lst:
			ret.append(word.get_word())
		return ret


	def set_supermemo_data(self, card):
		"""Sets the data of some word about the supermemo algorithm.

		Args:
			word_id: An integer representing the id of a word between all the user's words.
		"""
		self.db.set_supermemo_data(card)


	def get_highest_word_id(self):
		return self.db.get_highest_word_id(self.user_id)


	def get_highest_card_id(self):
		return self.db.get_highest_card_id(self.user_id)


	def get_all_topics(self, language):
		return self.db.get_all_topics(self.user_id,language)


	def not_locked(self):
		return self.get_state() != fsm.LOCKED

	def get_id(self):
		return self.user_id


	def set_card_waiting(self, card_id):
		self.db.set_card_waiting(self.user_id, card_id)


	def get_card_waiting(self):
		return self.db.get_card_waiting(self.user_id)

	def get_cards_on_topic(self, language, topic, get_default):
		return self.db.get_cards_on_topic(self.user_id, language, topic, get_default)
	

	def erase_language(self, language):
		return self.db.erase_language(self.user_id,language)






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
		known_users = self.db.get_known_users()
		self.users = {}
		for user_id in known_users:
			self.users[user_id] = User(user_id,self.db) 
		
	def get_user(self,user_id):
		return self.users[user_id]


	def reset_all_states(self):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			user.set_state(fsm.IDLE)
	

	def add_user(self,user_id):
		"""Register a new user.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Welcome to LingBot", if the user was not registered.
			- "Welcome back to LingoBot", if the user was already registered.
		"""
		if not user_id in self.users.keys():
			self.users[user_id] = User(user_id, self.db)
			return self.db.add_user(user_id)
		return "User already exists."


	def check_user_existence(self, user_id):
		return (user_id in self.users.keys())


	
	def backup(self):
		return self.db.backup()

	