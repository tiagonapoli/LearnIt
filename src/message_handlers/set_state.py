import telebot
import fsm
from bot_utils import get_id

def handle_set_state(bot, rtd):

	#=====================SET STATE=====================
	@bot.message_handler(commands = ['set_state'])
	def set_state(msg):
		"""
			Used for debug only. Set user state
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.IDLE)
		'''
		rtd.set_state(user_id, fsm.LOCKED)
		number = msg.text[11:]
		if len(number) == 0:
			bot.sent_message(user_id, "don't forget the new state")
			return 0
		print("new state:{}".format(int(number)))
		print("id:{} state:{}".format(user_id, rtd.get_state(user_id)))
		rtd.set_state(user_id, str(int(number)))
		'''
