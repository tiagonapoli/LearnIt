import logging
import telebot
import os
import time
from utilities import utils
import datetime

USER_LOGGER = logging.DEBUG
DATABASE = logging.DEBUG
LEARNIT = logging.DEBUG

USER_LOGGER_CONSOLE = logging.WARNING
DATABASE_CONSOLE = logging.WARNING
LEARNIT_CONSOLE = logging.WARNING
BOT_SENDER = logging.WARNING



class BotHandler(logging.Handler): # Inherit from logging.Handler
	def send_message(self, msg, exc_text, exc_class):
		self.user_sender.send_message(msg, translate_flag=False, parse="", markup=None)
		if exc_text != None and len(exc_text) <= 200:
			self.user_sender.send_message(exc_text, translate_flag=False, parse="", markup=None)
		elif exc_class != None:
			self.user_sender.send_message(str(exc_class), translate_flag=False, parse="", markup=None)

	def __init__(self, bot_controller_factory):
		self.user_sender = bot_controller_factory.get_bot_controller(359999978, 1)
		logging.Handler.__init__(self)

	def emit(self, record):
		log_entry = self.format(record)
		self.send_message(log_entry, record.exc_text, record.exc_info)

def setup_learnit():
	logger = logging.getLogger('LearnIt')
	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/LearnIt.log'

	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)

	PATH += filename

	handler_file = logging.FileHandler(PATH, mode='w')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(LEARNIT)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(LEARNIT_CONSOLE)
	formatter = logging.Formatter('%(name)s %(threadName)-25s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)

	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_message_handler():
	logger = logging.getLogger('Message_Handler')
	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/Message_Handler.log'

	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)

	PATH += filename

	handler_file = logging.FileHandler(PATH, mode='w')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(LEARNIT)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(LEARNIT_CONSOLE)
	formatter = logging.Formatter('%(name)s %(threadName)-25s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)

	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_sending_manager():
	logger = logging.getLogger('Sending_Manager')
	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/Sending_Manager.log'

	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)

	PATH += filename

	handler_file = logging.FileHandler(PATH, mode='w')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(LEARNIT)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(LEARNIT_CONSOLE)
	formatter = logging.Formatter('%(name)s %(threadName)-25s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)

	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_database():
	logger = logging.getLogger('Database')

	if len(logger.handlers) > 0:
		return

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/Database.log'

	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)

	PATH += filename

	handler_file = logging.FileHandler(PATH, mode='w')
	formatter = logging.Formatter('%(asctime)s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n',
									datefmt= '%d/%m %H:%M:%S')
	handler_file.setFormatter(formatter)
	handler_file.setLevel(DATABASE)

	handler_stream = logging.StreamHandler()
	handler_stream.setLevel(DATABASE_CONSOLE)
	formatter = logging.Formatter('%(name)-30s %(threadName)s %(funcName)s %(levelname)-8s %(message)s\n')
	handler_stream.setFormatter(formatter)

	logger.addHandler(handler_file)
	logger.addHandler(handler_stream)
	logger.setLevel(logging.DEBUG)

def setup_bot_sender(bot_controller_factory):

	logger = logging.getLogger('Bot_Sender')

	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	PATH = '../logs/Bot_Sender.log'

	pos = PATH.rfind('/')
	filename = PATH[pos+1:]
	PATH = PATH[:pos+1]

	if not os.path.exists(PATH):
		os.makedirs(PATH)

	PATH += filename

	handler_file = logging.FileHandler(PATH, mode='w')
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
	handler_bot = BotHandler(bot_controller_factory)
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

	handler_file = logging.FileHandler(PATH, mode='w')
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
