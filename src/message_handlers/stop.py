import fsm
from utilities.bot_utils import get_id
import logging
import bot_language


def handle_stop(bot, rtd, debug_mode):

	#=====================STOP=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE, 
					commands = ['stop'])
	def stop(msg):
		"""
			Stop: stop receiving cards
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))

		user.set_active(0)
		bot.send_message(user_id, bot_language.translate("You will *not* receive any card until you use the command /start again", user), 
			parse_mode="Markdown")

		user.set_state(fsm.IDLE)