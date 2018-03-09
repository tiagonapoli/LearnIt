import fsm
from utilities.bot_utils import get_id


def handle_user_dont_exist(bot, user_manager, debug_mode):

	#=====================USER DOESN'T EXIST - MSG=====================
	@bot.message_handler(func = lambda msg:	user_manager.check_user_existence(get_id(msg)) == False, content_types=['text','photo','audio','voice'])
	def user_existence(msg):
		user_id = get_id(msg)
		bot = user_manager.bot_controller_factory.get_bot_controller(user_id, 0)
		bot.send_message("#user_dont_exist_error_handling")

	#=====================USER DOESN'T EXIST - CALLBACK=====================
	@bot.callback_query_handler(func = lambda call:	user_manager.check_user_existence(get_id(call.message)) == False)
	def callback_user_existence(call):
		user_id = get_id(call.message)
		bot = user_manager.bot_controller_factory.get_bot_controller(user_id, 0)
		bot.send_message("#user_dont_exist_error_handling")



		