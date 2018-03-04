import fsm
from utilities.bot_utils import get_id, get_username
import logging
import bot_language
from utilities import bot_utils


def handle_setup_user(bot, rtd, debug_mode):

	

	
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
				bot.send_message(user_id, 
					bot_language.translate("Welcome back to LearnIt!", user) + "\n" + bot_language.translate("welcome_msg", user),
					parse_mode="Markdown")
			return
		
		m = rtd.add_user(user_id, username, bot)
		user = rtd.get_user(user_id)
		user.set_state(fsm.LOCKED)

		logger = logging.getLogger('{}'.format(user_id))
		logger.warning("New username {} {} ".format(user_id, username))
		logger = logging.getLogger('bot_sender')
		logger.warning("New username {} {} ".format(user_id, username))


		options = ['English', 'Português']
		text = "*Please select your mother language:*\n*Por favor, selecione sua língua nativa:*" + "\n" + bot_utils.create_string_keyboard(options)
		markup = bot_utils.create_keyboard(options, 3)

		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		user.keyboard_options = options
		user.set_state(fsm.next_state[fsm.IDLE]['setup user'])


	@bot.message_handler(func = lambda msg:
					(rtd.check_user_existence(get_id(msg)) == True and
					 rtd.get_user(get_id(msg)).get_state() == (fsm.SETUP_USER, fsm.GET_LANGUAGE)),
					content_types=['text'])
	def add_word1(msg):
		"""
			Add word: Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, 
				bot_language.translate("Please choose from keyboard", user))
			user.set_state(fsm.next_state[(fsm.SETUP_USER, fsm.GET_LANGUAGE)]['error'])
			return

		user.set_native_language(bot_language.native_languages[language])

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, 
			bot_language.translate("Welcome to LearnIt!", user) + "\n" + bot_language.translate("welcome_msg", user),
			reply_markup=markup, 
			parse_mode="Markdown")
		user.set_state(fsm.next_state[(fsm.SETUP_USER, fsm.GET_LANGUAGE)]['done'])
