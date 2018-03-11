import fsm
from utilities.bot_utils import get_id, get_username
import logging
from utilities import bot_utils


def handle_setup_user(bot, user_manager, debug_mode):

	#=====================SETUP USER=====================
	@bot.message_handler(commands = ['start'])
	def setup_user(msg):
		"""
			Register user into database.
		"""
		user_id = get_id(msg)
		username = get_username(msg)

		if username == None:
			bot = user_manager.bot_controller_factory.get_bot_controller(user_id, 0)
			bot.send_message("#setup_user_username_error")
			del bot
			return


		if user_manager.check_user_existence(user_id):
			user = user_manager.get_user(get_id(msg))
			if user.get_active() == 0:
				user.set_active(1)
				user.send_message("#welcome_back")
			return
		
		m = user_manager.add_user(user_id, username)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)

		logger = user.logger
		logger.warning("New username {} {} ".format(user_id, username))
		logger = logging.getLogger('Bot_Sender')
		logger.warning("New username {} {} ".format(user_id, username))

		options = ['English', 'Português']
		user.send_string_keyboard("#setup_user_mother_language", options)
		user.set_state(fsm.next_state[fsm.IDLE]['setup user'])


	@bot.message_handler(func = lambda msg:
					(user_manager.check_user_existence(get_id(msg)) == True and
					 user_manager.get_user(get_id(msg)).get_state() == (fsm.SETUP_USER, fsm.GET_LANGUAGE)),
					content_types=['text'])
	def add_word1(msg):
		"""
			Add word: Get word's language
		"""
		user = user_manager.get_user(get_id(msg))
		user.set_state(fsm.LOCKED)

		valid, language, keyboard_opt, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#setup_user_choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.SETUP_USER, fsm.GET_LANGUAGE)]['error'])
			return

		user.set_native_language(language)
		user.send_message("#welcome")
		user.set_state(fsm.next_state[(fsm.SETUP_USER, fsm.GET_LANGUAGE)]['done'])
