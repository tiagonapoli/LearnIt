import telebot
import fsm
from utilities.bot_utils import get_id, get_username

def handle_setup_user(bot, rtd):

	#=====================SETUP USER=====================
	@bot.message_handler(commands = ['start'])
	def setup_user(msg):
		"""
			Register user into database.
		"""
		user_id = get_id(msg)
		username = get_username(msg)

		if username == None:
			bot.send_message(user_id, "Please, create your Telegram Username first. You just have to go to Settings->Info->Username to create it")
			return

		if rtd.check_user_existence(user_id):
			user = rtd.get_user(get_id(msg))
			if user.get_active() == 0:
				user.set_active(1)
				bot.send_message(user_id, "Welcome back!")
			return
		
		print(username)	
		m = rtd.add_user(user_id, username)
		bot.send_message(user_id, m)
		user = rtd.get_user(user_id)
		user.set_state(fsm.IDLE)
