import logging 
import telebot
import os
import time
from utilities import utils
import datetime

USER_LOGGER = logging.INFO
DB_API = logging.INFO
LEARNIT_THREAD = logging.INFO
USER_LOGGER_CONSOLE = logging.WARNING
DB_API_CONSOLE = logging.WARNING
LEARNIT_THREAD_CONSOLE = logging.WARNING
BOT_SENDER = logging.WARNING


class BotHandler(logging.Handler): # Inherit from logging.Handler
    
	def send_message(self, msg, exc_text, exc_class):
		log = open("log.txt", "a")
		log.write("{} {}\n\n".format(datetime.datetime.now(), exc_class))
		
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
				log.write("{} {}\n\n".format(datetime.datetime.now(), str(e)))
				time.sleep(1)
		log.close()

	def __init__(self, bot):
		self.bot = bot
		logging.Handler.__init__(self)

	def emit(self, record):
		log_entry = self.format(record)
		log = open("log.txt", "a")
		log.write("{}\n".format(record.exc_info))
		log.close()
		self.send_message(log_entry, record.exc_text, record.exc_info)

def setup_learnit_thread():

	logger = logging.getLogger('learnit_thread')

	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/LearnIt_thread.log'
	
	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)
	
	PATH += filename
		
	handler_file = logging.FileHandler(PATH, mode='a')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(LEARNIT_THREAD)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(LEARNIT_THREAD_CONSOLE)
	formatter = logging.Formatter('%(name)-30s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)
		

def setup_db_api():

	logger = logging.getLogger('db_api')

	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/DB_API.log'
	
	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)
	
	PATH += filename
		
	handler_file = logging.FileHandler(PATH, mode='a')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(DB_API)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(DB_API_CONSOLE)
	formatter = logging.Formatter('%(name)-30s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_bot_sender(bot):

	logger = logging.getLogger('bot_sender')

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/bot_sender.log'
	
	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)
	
	PATH += filename
		
	handler_file = logging.FileHandler(PATH, mode='a')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(BOT_SENDER)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(BOT_SENDER)
	formatter = logging.Formatter('%(name)-30s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_bot = BotHandler(bot)
	handler_bot.setFormatter(formatter)
	handler_bot.setLevel(BOT_SENDER)

	logger.addHandler(handler_bot)
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.WARNING)

def setup_user_logger(user_id):

	logger = logging.getLogger('{}'.format(user_id))

	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/{}.log'.format(user_id)
	
	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)
	
	PATH += filename
		
	handler_file = logging.FileHandler(PATH, mode='a')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(USER_LOGGER)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(USER_LOGGER_CONSOLE)
	formatter = logging.Formatter('%(name)-30s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)
	
	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)
	

