import telebot
import fsm
from utilities import utils
from utilities.bot_utils import get_id, create_key_button
import logging

def handle_add_language(bot, rtd, debug_mode):

	#=====================ADD LANGUAGE=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['add_language'])
	def add_language(msg):
		""" 
			Add language sequence
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		bot.send_message(user_id, "*Text me the language you want to add*", parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.IDLE]['add_language'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.ADD_LANGUAGE, 
					content_types = ['text'])
	def add_language_0(msg):
		"""
			Get language text - Add language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))


		language = utils.treat_special_chars(msg.text)

		if len(language) >= 45:
			bot.send_message(user_id, "Please, don't exceed 45 characters. You digited {} characters. Send the language again:".format(len(language)))
			user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['error'])
			return

		if len(language) == 0:
			bot.send_message(user_id, "Please, don't user / or \ or _ or *. Send the language again:")
			user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['error'])
			return

		print(language)
		bot.send_message(user_id, utils.treat_msg_to_send(user.add_language(language)), parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['done'])
