import fsm
from utilities.bot_utils import get_id



def handle_help(bot, user_manager, debug_mode):

	#=====================HELP=====================
	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE,
					commands = ['help'])
	def help(msg):
		user = user_manager.get_user(get_id(msg))
		user.send_message("#help_msg")

		