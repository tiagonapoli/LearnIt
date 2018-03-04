import fsm
from utilities.bot_utils import get_id
import bot_language


def handle_help(bot, rtd, debug_mode):

	#=====================HELP=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE,
					commands = ['help'])
	def help(msg):
		user = rtd.get_user(get_id(msg))
		user_id = get_id(msg)
		help_msg = bot_language.translate("help_msg", user)
		bot.send_message(user_id, help_msg, disable_web_page_preview=True, parse_mode="Markdown")

		