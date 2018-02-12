import telebot
import fsm
from utilities import utils
from utilities.bot_utils import get_id, create_key_button

def handle_add_language(bot, rtd):

	#=====================ADD LANGUAGE=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE, 
					commands = ['add_language'])
	def add_language(msg):
		""" 
			Add language sequence
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		bot.send_message(user_id, "Text me the language you want to add")
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

		language = utils.treat_special_chars(msg.text)
		print(language)
		bot.send_message(user_id, user.add_language(language))
		user.set_state(fsm.next_state[fsm.ADD_LANGUAGE])
