import telebot
import fsm
from utilities import utils
from utilities import bot_utils
from utilities.bot_utils import get_id
import logging

def handle_settings(bot, rtd, debug_mode):

	#=====================SETTINGS=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['settings'])
	def settings(msg):
		"""
			Settings: settings menu
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		btns = ['Cards per hour', 'Set profile public', 'Set profile private']
		
		markup = bot_utils.create_keyboard(btns, 2)
		text = "*Which settings do you want to change?*\n" + bot_utils.create_string_keyboard(btns)

		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		user.keyboard_options = btns
		user.set_state(fsm.next_state[fsm.IDLE]['settings'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.SETTINGS, fsm.GET_OPTION),
					content_types=['text'])
	def settings1(msg):
		"""
			Settings: get option
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		valid, option = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_OPTION)]['error'])
			return

		markup = bot_utils.keyboard_remove()

		if option == 'Cards per hour':
			btns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
			markup = bot_utils.create_keyboard(btns, 3)
			text = "*How many cards you want to receive per hour?*\n" + bot_utils.create_string_keyboard(btns)
			bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
			user.keyboard_options = btns
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.GET_OPTION)]['cards per hour'])
		elif option == 'Set profile public':
			user.set_public(1)
			markup = bot_utils.keyboard_remove()
			bot.send_message(user_id, 'Your profile is now public', reply_markup=markup)
			user.set_state(fsm.IDLE)
		elif option == 'Set profile private':
			user.set_public(0)
			markup = bot_utils.keyboard_remove()
			bot.send_message(user_id, 'Your profile is now private', reply_markup=markup)
			user.set_state(fsm.IDLE)


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.SETTINGS, fsm.CARDS_PER_HOUR), 
					content_types=['text'])
	def settings2(msg):
		"""
			Settings: get the frequency of cards received per hour
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))
		
		valid, cards_per_hour = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		markup = bot_utils.keyboard_remove()

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.CARDS_PER_HOUR)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		user.set_cards_per_hour(int(cards_per_hour))
		bot.send_message(user_id, "_Cards per hour set successfuly!_", reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[(fsm.SETTINGS, fsm.CARDS_PER_HOUR)]['done'])