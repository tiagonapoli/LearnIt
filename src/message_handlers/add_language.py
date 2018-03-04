import fsm
from utilities import utils
from utilities.bot_utils import get_id
import logging
import bot_language

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
		logger = logging.getLogger('{}'.format(user_id))

		bot.send_message(user_id, 
			bot_language.translate("*Text me the language you want to add*", user), 
			parse_mode="Markdown")
		
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
		logger = logging.getLogger('{}'.format(user_id))


		language = utils.treat_special_chars(msg.text)

		if len(language) >= 45:
			bot.send_message(user_id, 
				bot_language.translate("Please, don't exceed 45 characters. You digited {} characters. Send the language again:", user).format(len(language)))
			user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['error'])
			return

		if len(language) == 0:
			bot.send_message(user_id, 
				bot_language.translate("Please, don't user / or \ or _ or *. Send the language again:", user))
			user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['error'])
			return

		logger.info(language)

		if user.add_language(language) == True:
			bot.send_message(user_id, 
				utils.treat_msg_to_send(bot_language.translate("{} added successfully to your languages",user).format(language)), 
				parse_mode="Markdown")
		else:
			bot.send_message(user_id, 
				utils.treat_msg_to_send(bot_language.translate("{} already exists", user).format(language)), 
				parse_mode="Markdown")			
		
		user.set_state(fsm.next_state[fsm.ADD_LANGUAGE]['done'])
