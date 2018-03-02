#! /usr/bin/python3
import datetime
import time
from threading import Thread
from runtimedata import RuntimeData
from UserCardQueue import UserCardQueue
from utilities import logging_utils, bot_utils
import logging


class SendingManager():

	def __init__(self, debug_mode):
		self.debug_mode = debug_mode
		self.continua = 1
		self.restart_bot_flag = 0
		self.logger = None
		self.bot = None
		self.start_bot() 

		self.rtd = RuntimeData(self.debug_mode)
		self.rtd.get_known_users()
		self.users = self.rtd.users
		self.user_queues = {}

		self.now = datetime.datetime.now()
		self.last_hour = (self.now.hour - 1 + 24) % 24
		self.cycles = 0

	def start_bot(self):
		del self.bot
		self.restart_bot_flag = 0
		self.logger = logging.getLogger(__name__)
		logger_aux = logging.getLogger('__main__')
		logger_aux.warning("Restarted bot sending manager")
		logging_utils.setup_logger_sending_manager(self.logger, self.debug_mode)
		self.bot = bot_utils.open_bot(self.debug_mode, self.logger) 
		logging_utils.add_bot_handler(self.logger, self.bot)

	def upd_users(self):
		self.now = datetime.datetime.now()
		hour = self.now.hour

		self.rtd.get_known_users()
		self.users = self.rtd.users

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
			self.rtd.reset_state_exception(user_id, self.bot)
			self.logger.error("Had to restart {}".format(user_id))


	def stop(self):
		self.continua = 0

	def restart_bot(self):
		self.restart_bot_flag = 1

	def run(self):
		self.logger.info("Starting sending manager")

		while self.continua == 1:
			try:
				self.logger.info("Woke Up - Cycles: {}".format(self.cycles))

				if self.restart_bot_flag == 1:
					self.start_bot()

				self.cycles += 1

				self.upd_users()
				self.new_hour_check()
				for user_id, user in self.users.items():
					if user.get_active() == 0:
						continue
					self.prepare_users_queues(user_id)
					self.process_users_queues(user_id)
					
				sleep = 60
				if self.debug_mode:
					sleep = 20
				self.logger.info("Sleep {}".format(sleep))
				time.sleep(sleep)

			except Exception as e:
				self.logger.error("EXCEPTION on sending manager", exc_info=True)
				self.restart_bot()
				sleep = 20
				if self.debug_mode:
					sleep = 20
				time.sleep(sleep)


		self.logger.warning("Sending manager turned off")
		for user_id, user in self.users.items():
			if user.get_active() == 0:
				continue
			self.user_queues[user_id].logger.info("Exiting sending manager")


class SendingManagerThread(Thread):

	def __init__(self, debug_mode):
		Thread.__init__(self)
		self.sending_manager = SendingManager(debug_mode)

	def safe_stop(self):
		self.sending_manager.stop()

	def run(self):
		self.sending_manager.run()

	def restart_bot(self):
		self.sending_manager.restart_bot()




	