import telebot
from bot_utils import get_id

def handle_message_not_understood(bot, rtd):

	#=====================MESSAGE NOT UNDERSTOOD=====================
	@bot.message_handler(func = lambda msg: True)
	def msg_not_undestood(msg):
		"""
			Change setting sequence
		"""
		user_id = get_id(msg)
		bot.send_message(user_id, "Oops, didn't understand your message")

	@bot.callback_query_handler(func=lambda call: True)
	def callback_not_understood(call):
		user_id = get_id(call.message)
		print("Callback from user {} not understood or thrown away: {}".format(user_id, call.message.text))
		#bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
