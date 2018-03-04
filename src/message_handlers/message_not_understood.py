from utilities.bot_utils import get_id
import bot_language


def handle_message_not_understood(bot, rtd, debug_mode):

	#=====================MESSAGE NOT UNDERSTOOD=====================
	@bot.message_handler(func = lambda msg: (True and
											 rtd.get_user(get_id(msg)).get_active() == 1))
	def msg_not_undestood(msg):
		"""
			Change setting sequence
		"""
		user_id = get_id(msg)
		user = rtd.get_user(get_id(msg))
		bot.send_message(user_id, 
			bot_language.translate("Oops, didn't understand your message", user))

	@bot.callback_query_handler(func=lambda call: (True and
												   rtd.get_user(get_id(call.message)).get_active() == 1))
	def callback_not_understood(call):
		user_id = get_id(call.message)
		#print("Callback from user {} not understood or thrown away: {}".format(user_id, call.message.text))
		#bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
