import logging 
import telebot
import os
import time
from utilities import utils
import datetime

SENDING_MANAGER = logging.WARNING
SENDING_MANAGER_FILE = logging.DEBUG
USER_CARD_QUEUE = logging.WARNING
USER_CARD_QUEUE_FILE = logging.DEBUG
MESSAGES_BOT = logging.WARNING
DEFAULT_FILE = logging.DEBUG
DEFAULT_CONSOLE = logging.INFO

class BotHandler(logging.Handler): # Inherit from logging.Handler
    
	def send_message(self, msg, exc_text, exc_class):
		log = open("log.txt", "a")
		log.write("{} {}\n".format(datetime.datetime.now(), exc_class))
		
		tries = 10
		while tries > 0:
			tries -= 1
			try:
				self.bot.send_message(359999978, msg)
				#self.bot.send_message(113538563, msg)
				if exc_text != None and len(exc_text) <= 200:
					self.bot.send_message(359999978, exc_text)
				#	self.bot.send_message(113538563, exc_text)
				else:
					self.bot.send_message(359999978, str(exc_class))
				#	self.bot.send_message(113538563, str(exc_class))
				return
			except Exception as e:
				log.write("{} {}\n".format(datetime.datetime.now(), str(e)))
				time.sleep(1)
		log.close()

	def __init__(self, bot):
		self.bot = bot
		logging.Handler.__init__(self)

	def emit(self, record):
		log_entry = self.format(record)
		log = open("log.txt", "a")
		log.write("BBBBBBBBB {}\n".format(record.exc_info))
		log.close()
		self.send_message(log_entry, record.exc_text, record.exc_info)


def setup_logger_default(logger, path, bot=None):

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = path
	
	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	
	if not os.path.exists(PATH):
		os.makedirs(PATH)
	
	PATH += filename
		
	handler_file = logging.FileHandler(PATH, mode='a')
	formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(DEFAULT_FILE)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(DEFAULT_CONSOLE)
	formatter = logging.Formatter('%(name)-30s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)
	if bot != None:
		add_bot_handler(logger,bot)
		
	return logger


def setup_logger_sending_manager(logger, debug_mode):

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/sending_manager/'
	if debug_mode:
		PATH = '../logs_debug/sending_manager/'
	
	if not os.path.exists(PATH):
		os.makedirs(PATH)
		
	PATH += 'sending_manager.log'
	
	handler_file = logging.FileHandler(PATH, mode='w')
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

def setup_logger_learnit_bot(logger, debug_mode):

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/'
	if debug_mode:
		PATH = '../logs_debug/'
	
	if not os.path.exists(PATH):
		os.makedirs(PATH)
		
	PATH += 'learnit.log'
	
	handler_file = logging.FileHandler(PATH, mode='w')
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


def setup_logger_UserCardQueue(logger, user_id, debug_mode):
	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/sending_manager/'
	if debug_mode:
		PATH = '../logs_debug/sending_manager/'.format(user_id)
	
	if not os.path.exists(PATH):
		os.makedirs(PATH)
		
	PATH += 'UserCardQueue_{}.log'.format(user_id)
		
	handler_file = logging.FileHandler(PATH, mode='w')
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

