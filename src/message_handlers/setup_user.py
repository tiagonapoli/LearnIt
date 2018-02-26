import telebot
import fsm
import logging
from utilities.bot_utils import get_id, get_username
from utilities import logging_utils

logger = None

def handle_setup_user(bot, rtd):

	logger = logging.getLogger(__name__)
	logging_utils.setup_logger_default(logger, '../logs/setup_user.log', bot)

	welcome = ("Use the command /add_language to add the languages you are interested in learning and then use the command /add_word to add words you are interested in memorizing, " +
			"or just use the command /copy_words to copy words from other users. During any process you can use /cancel to cancel the ongoing events, if you made a mistake, for example.")
	#=====================SETUP USER=====================
	@bot.message_handler(commands = ['start'])
	def setup_user(msg):
		"""
			Register user into database.
		"""
		user_id = get_id(msg)
		username = get_username(msg)

		if username == None:
			bot.send_message(user_id, "Please, create your Telegram Username first. You just have to go to Settings->Info->Username to create it. After you create one, type /start again.")
			return

		if rtd.check_user_existence(user_id):
			user = rtd.get_user(get_id(msg))
			if user.get_active() == 0:
				user.set_active(1)
				bot.send_message(user_id, "Welcome back to LearnIt!\n" + welcome)
			return
		
		logger.warning("New username {} {} ".format(user_id, username))
		m = rtd.add_user(user_id, username)
		bot.send_message(user_id, "Welcome to LearnIt!\n" + welcome)
		user = rtd.get_user(user_id)
		user.set_state(fsm.IDLE)
