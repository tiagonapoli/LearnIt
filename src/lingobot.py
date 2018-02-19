#! /usr/bin/python3
import sys
import os
import subprocess
import telebot
import signal
import time
import fsm
import datetime

import message_handlers.cancel
import message_handlers.error_handling

import message_handlers.add_word
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
from utilities import utils
from utilities import bot_utils


"""
	Bot message handlers source file
"""

def signal_handler(sign, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	bot.send_message(359999978,"Bot turned off")
	sending_manager.send_signal(signal.SIGINT)
	utils.turn_off(rtd)
	print("Exiting bot...")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

sending_manager = subprocess.Popen("gnome-terminal -x ./sending_manager.py", stdout=subprocess.PIPE, shell=True) 

rtd = RuntimeData()
rtd.reset_all_states()

while True:
	try:

		arq = open("../credentials/bot_token.txt", "r")
		TOKEN = (arq.read().splitlines())[0]
		arq.close()
		bot = telebot.TeleBot(TOKEN)
		print("Bot initialized successfully!")

		

		#=====================SETUP USER=====================
		message_handlers.setup_user.handle_setup_user(bot, rtd)


		#=====================USER DOESN'T EXIST=====================
		message_handlers.error_handling.handle_user_dont_exist(bot, rtd)	


		#=====================CANCEL=====================
		message_handlers.cancel.handle_cancel(bot, rtd)


		#=====================ANSWER AND RATE CARD DIFFICULTY=====================
		message_handlers.card_answering.handle_card_answer(bot, rtd)


		#=====================ADD LANGUAGE=====================
		message_handlers.add_language.handle_add_language(bot,rtd)


		#=====================LIST LANGUAGES=====================
		message_handlers.list_languages.handle_list_languages(bot,rtd)


		#=====================ERASE LANGUAGES=====================
		message_handlers.erase_languages.handle_erase_languages(bot,rtd)


		#=====================ADD WORD=====================
		message_handlers.add_word.handle_add_word(bot,rtd)


		#=====================LIST WORDS=====================
		message_handlers.list_words.handle_list_words(bot,rtd)


		#=====================ERASE WORD=====================
		message_handlers.erase_words.handle_erase_words(bot,rtd)


		#=====================TOPIC REVIEW=====================
		message_handlers.topic_review.handle_topic_review(bot,rtd)


		#=====================SETTINGS=====================
		message_handlers.settings.handle_settings(bot,rtd)


		#=====================HELP=====================
		message_handlers.help.handle_help(bot,rtd)

		#=====================STOP=====================
		message_handlers.stop.handle_stop(bot,rtd)


		#=====================MESSAGE NOT UNDERSTOOD=====================
		message_handlers.message_not_understood.handle_message_not_understood(bot,rtd)


		print("Press Ctrl+C to exit gently")
		print("Bot Polling!!!")
		bot.polling()	
	except Exception as e:

		rtd.reset_all_states_exception(bot)

		try:
			#bot.send_message(113538563,"Bot Crashed!!")
			bot.send_message(359999978,"Bot Crashed!!")
			bot.send_message(359999978,"{}".format(str(e.__class__.__name__)))
		except Exception as ee:
			print(ee)

		print("=====================An error ocurred with bot.polling======================")
		with open("exceptions_lingbot.txt", "a") as myfile:
   			myfile.write(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + "   " + str(e.__class__.__name__) + "\n")
		print(e.__class__.__name__)
		print("============================================================================\n\n\n\n")
		if str(e.__class__.__name__) == 'ConnectionError':
			time.sleep(30)
		elif str(e.__class__.__name__) == 'ReadTimeout':
			time.sleep(15)
		elif str(e).find("502") != -1:
		#	print(e)
			print("CONECTION LOST -> HTTP 502")
			time.sleep(120)
		else:	
		#	print(e)
			time.sleep(5)	
