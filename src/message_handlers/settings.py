import telebot
import fsm
from bot_utils import get_id

def handle_settings(bot, rtd):

	#=====================SETTINGS=====================
	@bot.message_handler(func = lambda msg: 
				rtd.get_state(get_id(msg)) == fsm.IDLE, 
				commands = ['settings'])
	def set_settings(msg):
		"""
			Change setting sequence
		"""
		pass
