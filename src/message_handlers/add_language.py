import telebot
import fsm
import utils
from bot_utils import get_id, create_key_button

def handle_add_language(bot, rtd):

	#=====================ADD LANGUAGE=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE, 
					commands = ['add_language'])
	def add_language(msg):
		""" 
			Add language sequence
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		bot.send_message(user_id, "Text me the language you want to add")
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['add_language'])




	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.ADD_LANGUAGE, 
					content_types = ['text'])
	def add_language_0(msg):
		"""
			Get language text - Add language
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		language = utils.treat_special_chars(msg.text)
		print(language)
		bot.send_message(user_id, rtd.add_language(user_id, language))
		rtd.set_state(user_id, fsm.next_state[fsm.ADD_LANGUAGE])
