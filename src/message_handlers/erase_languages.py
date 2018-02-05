import telebot
import fsm
from flashcard import Word, Card
from bot_utils import get_id, create_key_button

help_msg = ("NOT YET IMPLEMENTED.\n" +
		   "If you have questions or want to support the project, pleases contact one of the developers:" +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")


def handle_help(bot, rtd):

	#=====================HELP=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE,
					commands = ['help'])
	def help(msg):
		user_id = get_id(msg)
		bot.send_message(user_id, help_msg, disable_web_page_preview=True, parse_mode="Markdown")

		