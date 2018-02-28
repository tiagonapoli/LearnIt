#! /usr/bin/python3
import sys
import datetime
import telebot
import time
import signal
import os

from runtimedata import RuntimeData
from UserCardQueue import UserCardQueue
from utilities import utils, logging_utils, bot_utils
import logging

args = sys.argv
args = args[1:]
debug_mode = False
if len(args) > 0 and args[0] == '-debug':
	debug_mode = True

logger = logging.getLogger(__name__)
logging_utils.setup_logger_sending_manager(logger, debug_mode)


def signal_handler(sign, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	logger.warning("Sending manager turned off")
	for user_id, user in users.items():
		if user.get_active() == 0:
			continue
		user_queues[user_id].logger.info("Exiting sending manager")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

bot = bot_utils.open_bot(debug_mode, logger)
logging_utils.add_bot_handler(logger, bot)

rtd = RuntimeData(debug_mode)
rtd.get_known_users()
users = rtd.users

user_queues = {}

now = datetime.datetime.now()
last_hour = (now.hour - 1 + 24) % 24
cycles = 0
#rtd.reset_all_states()


logger.info("Starting sending manager")

while True:
	try:
		logger.info("Woke Up - Cycles: {}".format(cycles))
		cycles += 1

		now = datetime.datetime.now()
		hour = now.hour 
		rtd.get_known_users()

		users = rtd.users

		for user_id, user in users.items():
			if user.get_active() == 0:
				continue

			if ((user_id in user_queues.keys()) and 
					hour == 0 and 
					user_queues[user_id].get_initialized() == False):
				user_queues[user_id].process_end_day()
				user_queues[user_id].init_day()

			if not (user_id in user_queues.keys()):
				user_queues[user_id] = UserCardQueue(user, bot, debug_mode)

			if  cycles % 2 == 0:
				user_queues[user_id].upd_cards_expired() 				

			user_queues[user_id].add_learning_cards()

			if hour != 0:
				user_queues[user_id].reset_initialized()
				

		if last_hour != hour:
			last_hour = hour
			for user_id, user in users.items():
				if user.get_active() == 0:
					continue
				user_queues[user_id].hourly_init()
				

		for user_id, user in users.items():
			if user.get_active() == 0:
				continue
			user_queues[user_id].prepare_queue()


		restart = False
		for user_id, user in users.items():
			if user.get_active() == 0:
				continue
			sucess = user_queues[user_id].process_queue(bot)
			if sucess == False:
				restart = True


		if restart == True:
			rtd.reset_all_states_exception(bot)
			logger.error("Had to restart bot")
			bot = bot_utils.open_bot(debug_mode, logger)
			
		sleep = 220
		if debug_mode:
			sleep = 4
		logger.info("Sleep {}".format(sleep))
		time.sleep(sleep)


	except Exception as e:
		logger.error("EXCEPTION on sending manager", exc_info=True)
		sleep = 220
		if debug_mode:
			sleep = 10
		time.sleep(sleep)
