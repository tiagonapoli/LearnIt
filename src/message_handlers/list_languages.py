import telebot
import fsm
from flashcard import Word, Card
from utilities import utils
from utilities.bot_utils import get_id, create_key_button


def handle_list_languages(bot, rtd):	

	#=====================LIST LANGUAGES=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['list_languages'])
	def list_languages(msg):
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		known_languages = user.get_languages()
		text = "_Languages:_\n"
		for language in known_languages:
			text += "*." + utils.treat_msg_to_send(language, "*") + "*\n"
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "_No languages registered yet..._", parse_mode="Markdown")
			return

		bot.send_message(user_id, text, parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.IDLE]['list_languages'])


