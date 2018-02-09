import telebot
import fsm
from flashcard import Word, Card
from bot_utils import get_id, create_key_button

help_msg = ("NOT YET IMPLEMENTED.\n" +
		   "If you have questions or want to support the project, please contact one of the developers:" +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")


def handle_user_dont_exist(bot, rtd):

	#=====================HELP=====================
	@bot.message_handler(func = lambda msg:	rtd.check_user_existence(get_id(msg)) == False)
	def user_existence(msg):
		user_id = get_id(msg)
		str = ("LingoBot is under development, so sometimes we have to do some experiments and reset some things" +
			   ", maybe because of this your user isn't in our database. To fix this, please send a /start.")
		bot.send_message(user_id, str)

		