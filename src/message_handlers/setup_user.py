import telebot
import fsm
from bot_utils import get_id

def handle_setup_user(bot, rtd):

	#=====================SETUP USER=====================
	@bot.message_handler(commands = ['start'])
	def setup_user(msg):
		"""
			Register user into database.
		"""
		user_id = get_id(msg)
		if user_id in rtd.known_users:
			return
		rtd.set_state(user_id, fsm.LOCKED)
		m = rtd.add_user(user_id)
		bot.send_message(user_id, m)
		rtd.set_state(user_id, fsm.IDLE)	
