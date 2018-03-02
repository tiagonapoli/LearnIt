from dbapi import Database
import datetime
import fsm
import os
from utilities import utils, logging_utils
from random import shuffle
import logging



class User:

	def __init__(self, user_id, database_reference):
		self.db = database_reference
		self.user_id = user_id
		self.username = self.db.get_username(self.user_id)
		self.temp_word = None
		self.temp_card = None
		self.temp_words_list = None
		self.temp_topics_list = None
		self.btn_set = None
		self.keyboard_options = None
		self.receive_queue = None
		self.cards_to_review = None
		self.temp_language = None
		self.temp_user = None
		self.counter = None
		self.review_card_number = None
		self.pos = None

	def get_username(self):
		return self.username

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

		print("get state - id:{}  state:{}".format(self.user_id,ret))
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
			A list of tuples with the following information about the languages added by the user:
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

	def get_all_cards(self):
		return self.db.get_all_cards(self.user_id)

	def get_cards_on_word(self, word_id):
		cards = self.db.get_word(self.user_id, word_id).get_cards()
		return cards

	def get_cards_expired(self, now):
		cards = self.get_all_cards()
		ret = []
		for card in cards:
			if card.get_next_date() <= now.date():
				ret.append(card)
		shuffle(ret)
		ret.sort()
		return ret

	def working_hours(self, hour):
		return True

	def get_grade_waiting(self):
		return self.db.get_grade_waiting(self.user_id)

	def set_grade_waiting(self, grade):
		return self.db.set_grade_waiting(self.user_id, grade)

	def get_card_waiting_type(self):
		return self.db.get_card_waiting_type(self.user_id)

	def set_card_waiting_type(self, card_waiting_type):
		return self.db.set_card_waiting_type(self.user_id, card_waiting_type)

	def get_learning_words_limit(self):
		return self.db.get_learning_words_limit(self.user_id)

	def get_review_cards_limit(self):
		return self.db.get_review_cards_day_limit(self.user_id)

	def check_card_existence(self, card):
		return self.db.check_card_existence(self.user_id, card)

	def get_cards_per_hour(self):
		return self.db.get_cards_per_hour(self.user_id)

	def set_cards_per_hour(self, cards_per_hour):
		return self.db.set_cards_per_hour(self.user_id, cards_per_hour)

	def get_active(self):
		return self.db.get_active(self.user_id)

	def set_active(self, active):
		return self.db.set_active(self.user_id, active)

	def get_public(self):
		return self.db.get_public(self.user_id)

	def set_public(self, public):
		return self.db.set_public(self.user_id, public)

	def check_word_existence(self, language, topic, foreign_word):
		return self.db.check_word_existence(self.user_id, language, topic, foreign_word)


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

	def __init__(self, debug_mode):
		self.debug_mode = debug_mode
		self.db = Database(debug_mode)
		known_users = self.db.get_known_users()
		self.users = {}
		for user_id in known_users:
			self.users[user_id] = User(user_id,self.db) 
		

	def get_user(self,user_id):
		return self.users[user_id]


	def get_known_users(self):
		known_users = self.db.get_known_users()
		for user_id in known_users:
			if not (user_id in self.users.keys()):
				self.users[user_id] = User(user_id,self.db)
		return known_users


	def reset_all_states(self):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			user.set_state(fsm.IDLE)
			user.set_card_waiting(0)

	def reset_all_states_exception(self, bot):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			if user.get_state() == fsm.LOCKED:
				try:
					bot.send_message(user_id, "An error in the server ocurred, the operation was canceled")
				except Exception as e:
					print(e)
				user.set_state(fsm.IDLE)
				user.set_card_waiting(0)

	def reset_state_exception(self, bot, user_id):
		"""Sets the states of all users to the initial state"""
		if user_id in self.users.keys():
			user = self.users[user_id]
			try:
				bot.send_message(user_id, "An error in the server ocurred, the operation was canceled")
			except Exception as e:
				print(e)
			user.set_state(fsm.IDLE)
			user.set_card_waiting(0)

	def reset_all_states_turn_off(self, bot):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			if user.get_state() != fsm.IDLE:
				try:
					bot.send_message(user_id, "The bot is turning off, the operation is being canceled. Sorry for the inconvenience.")
				except Exception as e:
					print(e)
			user.set_state(fsm.IDLE)
			user.set_card_waiting(0)
	

	def add_user(self,user_id, username, bot):
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
			logger = logging.getLogger(str(user_id))
			path = '../logs/{}.log'.format(str(user_id))
			if self.debug_mode:
				path = '../logs_debug/{}.log'.format(str(user_id))
			logging_utils.setup_logger_default(logger, path, bot)
			return self.db.add_user(user_id, username)

		return "User already exists."

	def get_user_by_username(self, username):
		user_id = self.db.get_id_by_username(username)	
		if user_id == None:
			return False, None		
		return True, self.get_user(user_id)

	def check_user_existence(self, user_id):
		return (user_id in self.users.keys())


	def copy_topic(self, user_dest, user_source, language, topic, overwrite):
		ret = []
		words = user_source.get_words_on_topic(language, topic)
		user_id = user_dest.get_id()

		cnt_word = user_dest.get_highest_word_id() + 1
		cnt_card = user_dest.get_highest_card_id() + 1
		for word in words:
			language = word.get_language()
			user_dest.add_language(language)
			#RESETAR NEXT DATE
			word.user_id = user_dest.user_id
			word.word_id = cnt_word
			cnt_word += 1
			for content, card in word.cards.items():
				card.user_id = user_dest.get_id()
				card.card_id = cnt_card
				card.word_id = word.word_id

				card.attempts = 1  
				card.ef = 1.5  
				card.interval = 1
				card.next_date = datetime.datetime.now()


				cnt_card += 1
				for i in range(0, len(card.archives)):
					archive = card.archives[i]
					if card.get_type() == 'text':
						break
					prev_path = archive
					next_path = '../data/{}/{}/{}'.format(user_id, word.word_id, card.card_id) + utils.get_file_extension(archive)
					if self.debug_mode:
						next_path = '../data_debug/{}/{}/{}'.format(user_id, word.word_id, card.card_id) + utils.get_file_extension(archive)
						
					card.archives[i] = next_path
					utils.create_dir_card_archive(user_id, word.word_id, self.debug_mode)
					os.system("cp -TRv {} {}".format(prev_path, next_path))
			exist, aux_word_id = user_dest.check_word_existence(word.language, word.topic, word.foreign_word)
			if exist == True and overwrite == True:
				if utils.check_special_word(word.get_word()):
					ret.append(word.cards['text'].get_question())
				else:
					ret.append(word.get_word())
				user_dest.erase_word(aux_word_id)
				user_dest.add_word(word)
			elif exist == False:
				user_dest.add_word(word)

		return ret


	def backup(self, PATH):
		return self.db.backup(PATH)

	
