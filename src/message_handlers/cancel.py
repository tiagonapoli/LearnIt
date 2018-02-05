import telebot
import fsm
from bot_utils import get_id

def handler_cancel(bot, rtd):

	#=====================CANCEL=====================
	@bot.message_handler(func = lambda msg: rtd.not_locked(get_id(msg)) , commands = ['cancel'])
	def cancel(msg):
		"""
			Cancels any ongoing events for the user.
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id, "canceled...", reply_markup=markup)
		rtd.set_state(user_id, fsm.IDLE)
	
