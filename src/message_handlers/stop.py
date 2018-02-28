import telebot
import fsm
from utilities.bot_utils import get_id
import logging

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
		logger = logging.getLogger(str(user_id))

		user.set_active(0)
		bot.send_message(user_id, "You will *not* receive any card until you use the command /start again", parse_mode="Markdown")

		user.set_state(fsm.IDLE)