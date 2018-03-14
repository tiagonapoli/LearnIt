from utilities.bot_utils import get_id



def handle_message_not_understood(bot, user_manager, debug_mode):

	#=====================MESSAGE NOT UNDERSTOOD=====================
	@bot.message_handler(func = lambda msg: (True and
											 user_manager.get_user(get_id(msg)).get_active() == 1))
	def msg_not_undestood(msg):
		"""
			Change setting sequence
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(get_id(msg))
		user.send_message("#message_not_understood", txt_args=(msg.text, ))

	@bot.callback_query_handler(func=lambda call: (True and
												   user_manager.get_user(get_id(call.message)).get_active() == 1))
	def callback_not_understood(call):
		user_id = get_id(call.message)
		#print("Callback from user {} not understood or thrown away: {}".format(user_id, call.message.text))
		#bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
