#! /usr/bin/python3
import datetime
import time
from threading import Thread
from runtimedata import RuntimeData
from UserCardQueue import UserCardQueue
from utilities import logging_utils, bot_utils
import logging


class SendingManager():

	def __init__(self, sleep, debug_mode):
		self.sleep = sleep
		self.debug_mode = debug_mode
		
		self.continue_flag = False
		self.restart_bot_flag = False

		self.bot_logger = logging.getLogger('bot_sender')
		self.logger = logging.getLogger('learnit_thread')
		self.bot = None
		self.start_bot() 

		self.user_manager = RuntimeData(self.debug_mode)
		self.user_manager.get_known_users()
		self.users = self.user_manager.users
		self.user_queues = {}

		self.now = datetime.datetime.now()
		self.last_hour = (self.now.hour - 1 + 24) % 24
		self.cycles = 0


	def start_bot(self):
		self.logger.warning("Restart bot sending manager")
		del self.bot
		self.bot = None
		
		self.restart_bot_flag = False
		self.bot = bot_utils.open_bot(self.debug_mode, self.logger) 
		self.logger.warning("Restarted bot sending manager")

	def upd_users(self):
		self.now = datetime.datetime.now()
		hour = self.now.hour

		self.user_manager.get_known_users()
		self.users = self.user_manager.users

		for user_id, user in self.users.items():
			if user.get_active() == 0:
				continue

			if ((user_id in self.user_queues.keys()) and 
					hour == 0 and 
					self.user_queues[user_id].get_initialized() == False):
				self.user_queues[user_id].process_end_day()
				self.user_queues[user_id].init_day()

			if not (user_id in self.user_queues.keys()):
				self.user_queues[user_id] = UserCardQueue(user, self.bot, self.debug_mode)

			if  self.cycles % 2 == 0:
				self.user_queues[user_id].upd_cards_expired() 				

			self.user_queues[user_id].add_learning_cards()

			if hour != 0:
				self.user_queues[user_id].reset_initialized()


	def new_hour_check(self):
		self.now = datetime.datetime.now()
		hour = self.now.hour 
		if self.last_hour != hour:
			self.last_hour = hour
			for user_id, user in self.users.items():
				if user.get_active() == 0:
					continue
				self.user_queues[user_id].hourly_init()

				
	def prepare_users_queues(self, user_id):
		self.user_queues[user_id].prepare_queue()

	def process_users_queues(self, user_id):
		restart = False
		sucess = self.user_queues[user_id].process_queue(self.bot)
		if sucess == False:
			restart = True

		if restart == True:
			self.users[user_id].reset_state_exception(self.bot)
			self.start_bot()


	def stop(self):
		self.continue_flag = False

	def restart_bot(self):
		self.restart_bot_flag = True

	def run(self):
		self.continue_flag = True
		
		while self.continue_flag:
			try:
				self.logger.warning("Woke Up - Cycles: {}".format(self.cycles))

				self.start_bot()

				self.cycles += 1

				self.upd_users()
				self.new_hour_check()
				for user_id, user in self.users.items():
					if user.get_active() == 0:
						continue
					self.prepare_users_queues(user_id)
					self.process_users_queues(user_id)
					
				self.logger.info("Sleep {}".format(self.sleep))
				time.sleep(self.sleep)

			except Exception as e:
				self.bot_logger.error("EXCEPTION on sending manager", exc_info=True)
				self.logger.error("EXCEPTION on sending manager", exc_info=True)
				self.restart_bot()
				time.sleep(self.sleep)

		self.logger.warning("Sending manager turned off")

class SendingManagerThread(Thread):

	def __init__(self, sending_manager):
		Thread.__init__(self)
		self.sending_manager = sending_manager

	def safe_stop(self):
		self.sending_manager.stop()

	def run(self):
		self.sending_manager.run()

	def restart_bot(self):
		self.sending_manager.restart_bot()

