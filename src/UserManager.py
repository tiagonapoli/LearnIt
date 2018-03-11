from Database import Database
from User import User
from utilities import utils
import datetime
import fsm
import os

class UserManager: 

	def __init__(self, bot_controller_factory, debug_mode):
		self.debug_mode = debug_mode
		self.db = Database(debug_mode)
		self.bot_controller_factory = bot_controller_factory
		self.users = {}
		self.update_users()

	def get_user(self,user_id):
		return self.users[user_id]

	def update_users(self):
		known_users = self.db.get_known_users()
		for user_id in known_users:
			if not (user_id in self.users.keys()):
				self.users[user_id] = User(user_id, self.db, self.bot_controller_factory)
		return self.users

	def reset_all_states(self):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			user.set_state(fsm.IDLE)
			user.set_card_waiting(0)

	def reset_all_states_exception(self):
		for user_id, user in self.users.items():
			if user.get_state() == fsm.LOCKED:
				user.send_message("#reset_all_states_exception")
				user.set_state(fsm.IDLE)
				user.set_card_waiting(0)

	def reset_all_states_turn_off(self):
		"""Sets the states of all users to the initial state"""
		for user_id, user in self.users.items():
			if user.get_state() != fsm.IDLE:
				user.send_message("The bot is turning off, the operation is being canceled. Sorry for the inconvenience.")
			user.set_state(fsm.IDLE)
			user.set_card_waiting(0)

	def add_user(self, user_id, username):
		if not user_id in self.users.keys():
			self.users[user_id] = User(user_id, self.db, self.bot_controller_factory)
			return self.db.add_user(user_id, username)

	def get_user_by_username(self, username):
		user_id = self.db.get_id_by_username(username)	
		if user_id == None:
			return False, None		
		return True, self.get_user(user_id)

	def check_user_existence(self, user_id):
		return (user_id in self.users.keys())

	def copy_topic(self, user_dest, user_source, subject, topic, overwrite):
		overwritten = []
		copied = []
		study_items = user_source.get_study_items_on_topic(subject, topic)
		user_id = user_dest.get_id()

		cnt_study_item = user_dest.get_highest_study_item_id() + 1
		cnt_card = user_dest.get_highest_card_id() + 1
		for deck in study_items:

			deck.user_id = user_dest.user_id
			deck.study_item_id = cnt_study_item
			cnt_study_item += 1
			deck.active = 1

			exist, aux_study_item_id = user_dest.check_study_item_existence(deck.subject, deck.topic, deck.study_item)

			if exist == True and overwrite == False:
				continue

			if exist == True and overwrite == True:
				overwritten.append(deck.get_sendable_study_item())
				user_dest.erase_study_item(aux_study_item_id)

			if deck.study_item_type == 1:
				prev_path = deck.study_item
				next_path = '../data/{}/{}/study_item'.format(user_id, deck.study_item_id) + utils.get_file_extension(deck.study_item)
				if self.debug_mode:
					next_path = '../data_debug/{}/{}/study_item'.format(user_id, deck.study_item_id) + utils.get_file_extension(deck.study_item)		
				deck.study_item = next_path
				utils.create_dir_card_archive(user_id, deck.study_item_id, self.debug_mode)
				os.system("cp -TRv {} {}".format(prev_path, next_path))

			for content, card in deck.cards.items():

				card.user_id = user_dest.get_id()
				card.card_id = cnt_card
				cnt_card += 1
				card.active = 1
				card.study_item_id = deck.study_item_id

				card.attempts = 1  
				card.ef = 1.5  
				card.interval = 1
				card.next_date = datetime.datetime.now()

				question_type, question = card.get_question()
				if question_type == 'text':
					continue

				prev_path = question
				next_path = '../data/{}/{}/{}'.format(user_id, deck.study_item_id, card.card_id) + utils.get_file_extension(question)
				if self.debug_mode:
					next_path = '../data_debug/{}/{}/{}'.format(user_id, deck.study_item_id, card.card_id) + utils.get_file_extension(question)
					
				card.question = next_path
				utils.create_dir_card_archive(user_id, deck.study_item_id, self.debug_mode)
				os.system("cp -TRv {} {}".format(prev_path, next_path))
			
			user_dest.add_study_item_deck(deck)
			if exist == False:
				copied.append(deck.get_sendable_study_item())

		return copied, overwritten


	def backup(self, PATH):
		return self.db.backup(PATH)