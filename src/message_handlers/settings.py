import telebot
import fsm
from utilities.bot_utils import get_id

def handle_settings(bot, rtd):

	#=====================SETTINGS=====================
	@bot.message_handler(func = lambda msg: 
				rtd.get_user(get_id(msg)).get_state() == fsm.IDLE, 
				commands = ['settings'])
	def set_settings(msg):
		"""
			Change setting sequence
		"""
		pass
