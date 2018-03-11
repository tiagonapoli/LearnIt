import fsm
from utilities import bot_utils
from utilities.bot_utils import get_id
import logging


def handle_cancel(bot, user_manager, debug_mode):

	#=====================CANCEL=====================
	@bot.message_handler(func = lambda msg: (user_manager.get_user(get_id(msg)).not_locked() and
											 user_manager.get_user(get_id(msg)).get_active() == 1),
						commands = ['cancel'])
	def cancel(msg):
		"""
			Cancels any ongoing events for the user.
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		
		prev_state = user.get_state()
		user.set_state(fsm.LOCKED)
		logger = user.logger
		
		if (prev_state == fsm.WAITING_ANS or prev_state == fsm.WAITING_POLL_ANS):
			user.set_card_waiting(0)
			
		user.send_message("#cancel")
		user.set_state(fsm.IDLE)
	
