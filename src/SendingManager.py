#! /usr/bin/python3
import datetime
import time
from threading import Thread
from UserManager import UserManager
from UserSendingCardManager import UserSendingCardManager
from utilities import logging_utils
import logging


class SendingManager():

	def __init__(self, sleep, bot_controller_factory, debug_mode):
		self.continue_flag = False
		self.sleep = sleep
		self.debug_mode = debug_mode	
		self.bot_logger = logging.getLogger('Bot_Sender')
		self.logger = logging.getLogger('Sending_Manager')
		self.user_manager = UserManager(bot_controller_factory, self.debug_mode)
		self.users = self.user_manager.users
		self.user_card_manager = {}
		self.cycles = 0


	def upd_users(self):
		self.user_manager.update_users()
		self.users = self.user_manager.users
		for user_id, user in self.users.items():
			if user.get_active() == 0:
				continue
			if not (user_id in self.user_card_manager.keys()):
				self.user_card_manager[user_id] = UserSendingCardManager(user)

	def stop(self):
		self.continue_flag = False

	def run(self):
		self.continue_flag = True
		while self.continue_flag:
			try:
				self.logger.warning("Sending Manager Woke Up - Cycles: {}".format(self.cycles))
				self.cycles += 1
				self.upd_users()
				for user_id, user_card_manager in self.user_card_manager.items():
					if self.users[user_id].get_active() == 0:
						continue
					user_card_manager.run()
				self.logger.info("Sleep {}".format(self.sleep))
				time.sleep(self.sleep)
			except Exception as e:
				self.bot_logger.error("EXCEPTION on sending manager", exc_info=True)
				self.logger.error("EXCEPTION on sending manager", exc_info=True)
				time.sleep(self.sleep)

		self.logger.warning("Sending manager turned off")
		self.bot_logger.warning("Sending manager turned off")


class SendingManagerThread(Thread):

	def __init__(self, sending_manager):
		Thread.__init__(self)
		self.sending_manager = sending_manager

	def stop(self):
		self.sending_manager.stop()

	def run(self):
		self.sending_manager.run()

