import fsm
from utilities import utils
from utilities import bot_utils
from utilities.bot_utils import get_id
import logging



def handle_settings(bot, user_manager, debug_mode):

	#=====================SETTINGS=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['settings'])
	def settings(msg):
		"""
			Settings: settings menu
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		btns = ['Cards per hour', 
				'Set profile public', 
				'Set profile private',
				'Change bot language']
		
		user.send_string_keyboard("#settings_msg", btns, translate_options=True, width=2)
		user.set_state(fsm.next_state[fsm.IDLE]['settings'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.SETTINGS, fsm.GET_OPTION),
					content_types=['text'])
	def settings1(msg):
		"""
			Settings: get option
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, option, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_OPTION)]['error'])
			return

		if keyboard_option == 0:
			btns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
			user.send_string_keyboard("#settings_cards_per_hour", btns)
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_OPTION)]['cards per hour'])
		elif keyboard_option == 1:
			user.set_public(1)
			user.send_message('#settings_set_public')
			user.set_state(fsm.IDLE)
		elif keyboard_option == 2:
			user.set_public(0)
			user.send_message('#settings_set_private')
			user.set_state(fsm.IDLE)
		elif keyboard_option == 3:
			options = ['English', 'Português']
			user.send_string_keyboard("#settings_change_language", options)
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_OPTION)]['change language'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.SETTINGS, fsm.CARDS_PER_HOUR), 
					content_types=['text'])
	def settings2(msg):
		"""
			Settings: get the frequency of cards received per hour
		"""
		
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger
		
		valid, cards_per_hour, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.CARDS_PER_HOUR)]['error'])
			return

		user.set_cards_per_hour(int(cards_per_hour))
		user.send_message("#settings_cards_per_hour_setted")
		user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.CARDS_PER_HOUR)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.SETTINGS, fsm.GET_LANGUAGE),
					content_types=['text'])
	def add_word1(msg):
		"""
			Add word: Get word's language
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, language, keyboard_options, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_LANGUAGE)]['error'])
			return

		user.set_native_language(language)
		user.send_message("#settings_language_setted")
		user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_LANGUAGE)]['done'])
