import fsm
from utilities import bot_utils
from utilities.bot_utils import get_id
import logging

def handle_cancel(bot, rtd, debug_mode):

	#=====================CANCEL=====================
	@bot.message_handler(func = lambda msg: (rtd.get_user(get_id(msg)).not_locked() and
											 rtd.get_user(get_id(msg)).get_active() == 1),
						commands = ['cancel'])
	def cancel(msg):
		"""
			Cancels any ongoing events for the user.
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		
		prev_state = user.get_state()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))
		
		if (prev_state == fsm.WAITING_ANS or
			prev_state == fsm.WAITING_POLL_ANS):
			user.set_card_waiting(0)
			
		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "canceled...", reply_markup=markup)
		user.set_state(fsm.IDLE)
	
