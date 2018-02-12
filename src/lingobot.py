#! /usr/bin/python3
import sys
import telebot
import utils
import signal
import systemtools
import time
import bot_utils
import fsm

import message_handlers.cancel
import message_handlers.error_handling

import message_handlers.add_word
import message_handlers.list_words
import message_handlers.erase_words

import message_handlers.add_language 
import message_handlers.list_languages 
import message_handlers.erase_languages

import message_handlers.settings
import message_handlers.help
import message_handlers.setup_user

import message_handlers.topic_review
import message_handlers.card_answering
import message_handlers.message_not_understood

from runtimedata import RuntimeData


"""
	Bot message handlers source file
"""

def signal_handler(signal, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	bot.send_message(359999978,"Bot turned off")
	#bot.send_message(113538563,"Bot turned off")
	utils.turn_off(rtd)
	print("Exiting bot...")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
	arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)
	sys.exit(0)	
	
rtd = RuntimeData()
rtd.reset_all_states()
systemtools.schedule_daily_setup()

'''
@bot.message_handler(func = lambda msg: True)
def debug(msg):
	str = ("Bot is under development. Some bugs ocurred. You can contact one of the developers to ask about the situation: " +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")
	bot.send_message(msg.chat.id, str, disable_web_page_preview=True, parse_mode="Markdown")
'''


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


#=====================MESSAGE NOT UNDERSTOOD=====================
message_handlers.message_not_understood.handle_message_not_understood(bot,rtd)


while True:
	try:
		print("Press Ctrl+C to exit gently")
		print("Bot Polling!!!")
		bot.polling(none_stop=True)	
	except Exception as e:
		bot.send_message(113538563,"Bot Crashed!!")
		bot.send_message(359999978,"Bot Crashed!!")
		print("=====================An error ocurred with bot.polling======================")
		print(e)
		time.sleep(5)	

