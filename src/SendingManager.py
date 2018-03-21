#! /usr/bin/python3
import datetime
import time
from threading import Thread
from UserManager import UserManager
from UserSendingCardManager import UserSendingCardManager
from utilities import logging_utils
import logging
import gc


class SendingManager():

	def __init__(self, sleep, bot_controller_factory, debug_mode):
		self.continue_flag = False

		self.sleep = sleep
		self.sleep_divisions = 60
		self.debug_mode = debug_mode
		self.bot_logger = logging.getLogger('Bot_Sender')
		self.logger = logging.getLogger('Sending_Manager')
		self.user_manager = UserManager(bot_controller_factory, self.debug_mode)
		self.users = self.user_manager.users
		self.user_card_manager = {}
		self.init_time = 180


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

	def partial_sleep(self, sleep, divisions):
		cnt = divisions
		mini_sleep = sleep / divisions
		while cnt > 0 and self.continue_flag:
			time.sleep(mini_sleep)
			cnt -= 1

	def run(self):
		self.continue_flag = True

		self.logger.warning("Wait {} seconds to initialize sending manager".format(self.init_time))
		self.partial_sleep(self.init_time, self.sleep_divisions)

		cycles = 0
		while self.continue_flag:
			try:
				if cycles % 2 == 0:
					self.logger.warning("Collect garbage")
					gc.collect()

				self.logger.warning("Sending Manager Woke Up - Cycles: {}".format(cycles))
				cycles += 1
				self.upd_users()
				for user_id, user_card_manager in self.user_card_manager.items():
					if self.users[user_id].get_active() == 0:
						continue
					user_card_manager.run()
				self.logger.info("Sleep {}".format(self.sleep))
				self.partial_sleep(self.sleep, self.sleep_divisions)
			except Exception as e:
				self.bot_logger.error("EXCEPTION on sending manager", exc_info=True)
				self.logger.error("EXCEPTION on sending manager", exc_info=True)
				self.partial_sleep(self.sleep, self.sleep_divisions)

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

if __name__ == '__main__':
	from BotController import BotControllerFactory
	sending_manager = SendingManager(5, BotControllerFactory('495750247:AAFVO7YqWCl2QKov6PselFnAlL_RRBtfWco'), 1)
	sending_manager_thread = SendingManagerThread(sending_manager)
	sending_manager_thread.start()
