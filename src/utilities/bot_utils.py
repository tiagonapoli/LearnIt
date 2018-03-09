import telebot
from utilities import utils
import sys


def open_bot(debug_mode, logger = None):
	arq = None
	if debug_mode:
		arq = open("../credentials/bot_debug_token.txt", "r")
	else:
		arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot_aux = telebot.TeleBot(TOKEN)
	if logger:
		logger.info("Bot initialized successfully")
	return bot_aux

def get_id(msg):
	"""
		Gets message user ID
		Return:
			User ID: integer
	"""
	return msg.chat.id

def get_username(msg):
	return msg.from_user.username













