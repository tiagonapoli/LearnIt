import telebot
import fsm
from flashcard import Word, Card
from utilities.bot_utils import get_id, create_key_button

help_msg = ("Use the command /add\_language to add the languages you are interested in learning and then use the command /add\_word to add words you are interested in memorizing, " + 
			"or just use the command /copy\_words to copy words from other users. " +
			"During any process you can use /cancel to cancel the ongoing events, if you made a mistake, for example.\n" +
		   "If you have questions or want to support the project, please contact one of the developers:" +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")


def handle_help(bot, rtd):

	#=====================HELP=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE,
					commands = ['help'])
	def help(msg):
		user_id = get_id(msg)
		bot.send_message(user_id, help_msg, disable_web_page_preview=True, parse_mode="Markdown")

		