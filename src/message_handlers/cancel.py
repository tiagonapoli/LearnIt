import telebot
import fsm
import bot_utils
from bot_utils import get_id

def handle_cancel(bot, rtd):

	#=====================CANCEL=====================
	@bot.message_handler(func = lambda msg: rtd.get_user(get_id(msg)).not_locked() , commands = ['cancel'])
	def cancel(msg):
		"""
			Cancels any ongoing events for the user.
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "canceled...", reply_markup=markup)
		user.set_state(fsm.IDLE)
	
