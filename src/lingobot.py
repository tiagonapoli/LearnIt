#! /usr/bin/python3
import sys
import os
import subprocess
import telebot
import signal
import time
import fsm
import datetime
import logging

import message_handlers.cancel
import message_handlers.error_handling

import message_handlers.add_word
import message_handlers.copy_words
import message_handlers.list_words
import message_handlers.erase_words

import message_handlers.add_language 
import message_handlers.list_languages 
import message_handlers.erase_languages

import message_handlers.settings
import message_handlers.stop
import message_handlers.help
import message_handlers.setup_user

import message_handlers.topic_review
import message_handlers.card_answering
import message_handlers.message_not_understood

from runtimedata import RuntimeData
from utilities import utils, bot_utils, logging_utils


"""
	Bot message handlers source file
"""

args = sys.argv
args = args[1:]
debug_mode = False
if len(args) > 0 and args[0] == '-debug':
	debug_mode = True

logger = logging.getLogger(__name__)
logging_utils.setup_logger_learnit_bot(logger, debug_mode)
bot = bot_utils.open_bot(debug_mode, logger)
logging_utils.add_bot_handler(logger, bot)

def signal_handler(sign, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	sending_manager.send_signal(signal.SIGINT)
	utils.turn_off(rtd, bot, debug_mode)
	logger.warning("Bot turned off")
	print("Exiting bot...")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if debug_mode:
	sending_manager = subprocess.Popen("gnome-terminal -x ./sending_manager.py -debug", stdout=subprocess.PIPE, shell=True) 		
else:
	sending_manager = subprocess.Popen("gnome-terminal -x ./sending_manager.py", stdout=subprocess.PIPE, shell=True)


print(debug_mode) 
rtd = RuntimeData(debug_mode)
rtd.reset_all_states()

while True:
	try:

		for user_id in rtd.users.keys():
			logger = logging.getLogger(str(user_id))
			path = '../logs/{}.log'.format(str(user_id))
			if debug_mode:
				path = '../logs_debug/{}.log'.format(str(user_id))
			logging_utils.setup_logger_default(logger, path, bot)


		#=====================SETUP USER=====================
		message_handlers.setup_user.handle_setup_user(bot, rtd, debug_mode)


		#=====================USER DOESN'T EXIST=====================
		message_handlers.error_handling.handle_user_dont_exist(bot, rtd, debug_mode)	


		#=====================CANCEL=====================
		message_handlers.cancel.handle_cancel(bot, rtd, debug_mode)


		#=====================ANSWER AND RATE CARD DIFFICULTY=====================
		message_handlers.card_answering.handle_card_answer(bot, rtd, debug_mode)


		#=====================ADD LANGUAGE=====================
		message_handlers.add_language.handle_add_language(bot, rtd, debug_mode)


		#=====================LIST LANGUAGES=====================
		message_handlers.list_languages.handle_list_languages(bot, rtd, debug_mode)


		#=====================ERASE LANGUAGES=====================
		message_handlers.erase_languages.handle_erase_languages(bot, rtd, debug_mode)


		#=====================ADD WORD=====================
		message_handlers.add_word.handle_add_word(bot, rtd, debug_mode)


		#=====================COPY WORDS=====================
		message_handlers.copy_words.handle_copy_words(bot, rtd, debug_mode)


		#=====================LIST WORDS=====================
		message_handlers.list_words.handle_list_words(bot, rtd, debug_mode)


		#=====================ERASE WORD=====================
		message_handlers.erase_words.handle_erase_words(bot, rtd, debug_mode)


		#=====================TOPIC REVIEW=====================
		message_handlers.topic_review.handle_topic_review(bot, rtd, debug_mode)


		#=====================SETTINGS=====================
		message_handlers.settings.handle_settings(bot, rtd, debug_mode)


		#=====================HELP=====================
		message_handlers.help.handle_help(bot, rtd, debug_mode)


		#=====================STOP=====================
		message_handlers.stop.handle_stop(bot, rtd, debug_mode)


		#=====================MESSAGE NOT UNDERSTOOD=====================
		message_handlers.message_not_understood.handle_message_not_understood(bot, rtd, debug_mode)
		
		print("Press Ctrl+C to exit gently")
		bot.polling()	

	except Exception as e:

		rtd.reset_all_states_exception(bot)

		logger.error("Bot Crashed {}".format(e.__class__.__name__), exc_info=True)
		if str(e.__class__.__name__) == 'ConnectionError':
			time.sleep(30)
		elif str(e.__class__.__name__) == 'ReadTimeout':
			time.sleep(15)
		elif str(e).find("502") != -1:
			logger.error("Connection Lost -> HTTP 502")
			time.sleep(120)
		else:	
			time.sleep(5)	
