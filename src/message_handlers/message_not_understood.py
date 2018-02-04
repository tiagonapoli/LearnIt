import telebot
from bot_utils import get_id

def handle_message_not_understood(bot, rtd):

	#=====================MESSAGE NOT UNDERSTOOD=====================
	@bot.message_handler(func = lambda msg: True)
	def set_settings(msg):
		"""
			Change setting sequence
		"""
		user_id = get_id(msg)
		bot.send_message(user_id, "Oops, didn't understand your message")
