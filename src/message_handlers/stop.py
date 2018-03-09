import fsm
from utilities.bot_utils import get_id
import logging



def handle_stop(bot, user_manager, debug_mode):

	#=====================STOP=====================
	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE, 
					commands = ['stop'])
	def stop(msg):
		"""
			Stop: stop receiving cards
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		user.set_active(0)
		user.send_message("#stop_msg")
		user.set_state(fsm.IDLE)