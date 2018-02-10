import telebot
import fsm
import utils
from flashcard import Word, Card
from bot_utils import get_id, create_key_button


def handle_list_languages(bot, rtd):	

	#=====================LIST LANGUAGES=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE, 
					commands = ['list_languages'])
	def list_languages(msg):
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		known_languages = user.get_languages()
		text = "_Languages:_\n"
		for language in known_languages:
			text += "*." + language + "*\n"
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "No languages registered yet...")
			return

		bot.send_message(user_id, text, parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.IDLE]['list_languages'])


