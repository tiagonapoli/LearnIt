import logging 
import telebot
import os
from utilities import utils

SENDING_MANAGER = logging.INFO
SENDING_MANAGER_FILE = logging.DEBUG
USER_CARD_QUEUE = logging.DEBUG
USER_CARD_QUEUE_FILE = logging.DEBUG
MESSAGES_BOT = logging.ERROR

class BotHandler(logging.Handler): # Inherit from logging.Handler
    
	def send_message(self, msg, exc):
		try:
			self.bot.send_message(359999978, msg)
			if exc != None and len(exc) <= 2000:
				self.bot.send_message(359999978, exc)
		except:
			arq = open("../credentials/bot_token.txt", "rs")
			TOKEN = (arq.read().splitlines())[0]
			arq.close()
			self.bot = telebot.TeleBot(TOKEN)

	def __init__(self, bot):
		self.bot = bot
		logging.Handler.__init__(self)

	def emit(self, record):
		self.send_message(record.message, record.exc_text)


def setup_logger_sending_manager(logger):
	utils.create_log_dir()
	if not os.path.exists('../logs/sending_manager/'):
		os.mkdir('../logs/sending_manager/')
	handler_file = logging.FileHandler('../logs/sending_manager/sending_manager.log', mode='w')
	formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(SENDING_MANAGER_FILE)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(SENDING_MANAGER)
	formatter = logging.Formatter('%(name)-30s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_logger_learnit_bot(logger):
	utils.create_log_dir()

	handler_file = logging.FileHandler('../logs/learnit.log', mode='w')
	formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(SENDING_MANAGER_FILE)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(SENDING_MANAGER)
	formatter = logging.Formatter('%(name)-30s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)


def add_bot_handler(logger, bot):
	formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_bot = BotHandler(bot)
	handler_bot.setFormatter(formatter)
	handler_bot.setLevel(MESSAGES_BOT)
	logger.addHandler(handler_bot)


def setup_logger_UserCardQueue(logger, user_id):
	utils.create_log_dir()
	if not os.path.exists('../logs/sending_manager/'):
		os.mkdir('../logs/sending_manager/')
		
	handler_file = logging.FileHandler('../logs/sending_manager/UserCardQueue_{}.log'.format(user_id), mode='w')
	formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(USER_CARD_QUEUE_FILE)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(USER_CARD_QUEUE)
	formatter = logging.Formatter('%(name)-30s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

