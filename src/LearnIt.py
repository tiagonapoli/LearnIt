#! /usr/bin/python3
import sys
import os
import signal
import time
import logging
from MessageHandler import MessageHandlerThread
from SendingManager import SendingManagerThread
from utilities import logging_utils
from threading import Thread
import gc

class LearnIt(Thread):

	def __init__(self, message_handler, sending_manager, bot_controller_factory):
		Thread.__init__(self)
		self.locked = True
		self.continue_flag = True
		logging_utils.setup_learnit()
		logging_utils.setup_message_handler()
		logging_utils.setup_sending_manager()
		logging_utils.setup_database()
		logging_utils.setup_bot_sender(bot_controller_factory)
		self.logger = logging.getLogger('LearnIt')
		self.message_handler_thread = MessageHandlerThread(message_handler)
		self.sending_manager_thread = SendingManagerThread(sending_manager)
		self.backup_time = 3600 * 8
		self.gc_time = 3600

	def start_message_handler(self):
		self.message_handler_thread.start()

	def restart_bot_message_handler(self):
		self.logger.warning("Set to restart message handler bot")
		self.message_handler_thread.restart_bot()

	def stop_message_handler(self):
		self.message_handler_thread.stop()
		self.logger.warning("Requested message handler to stop")

	def start_sending_manager(self):
		self.sending_manager_thread.start()

	def stop_sending_manager(self):
		self.sending_manager_thread.stop()
		self.logger.warning("Requested sending manager to stop")

	def default(self):
		self.start_message_handler()
		self.start_sending_manager()

	def backup(self):
		self.logger.warning("Start backup")
		self.message_handler_thread.backup()
		self.logger.warning("Ended backup")

	def safe_stop(self):

		self.continue_flag = False
		while self.locked == True:
			time.sleep(0.5)
		self.logger.warning("LearnIt Safe Stop!")

		self.stop_sending_manager()
		self.stop_message_handler()

		self.backup()

		self.logger.warning("Waiting message handler to stop")
		if self.message_handler_thread.is_alive():
			self.message_handler_thread.join()
		self.logger.warning("Message handler stopped!")
		self.logger.warning("Waiting send manager to stop")
		if self.sending_manager_thread.is_alive():
			self.sending_manager_thread.join()
		self.logger.warning("Sending manager stopped!")


	def run(self):
		self.logger.warning("Running LearniIt")
		self.default()
		time_ini = time.time()
		gc_ini = time.time()
		while self.continue_flag:
			self.locked = True
			self.logger.info("Check if idle time exceeded")
			sleep = self.message_handler_thread.idle_time_exceed()
			self.logger.info("LearnIt Sleep {}".format(sleep))
			if sleep < 1:
				self.restart_bot_message_handler()
				sleep = self.message_handler_thread.get_max_idle_time()
				self.logger.info("LearnIt Sleep {}".format(sleep))
				self.locked = False
				time.sleep(sleep)
			else:
				self.locked = False
				time.sleep(sleep)

			time_fim = time.time()
			self.logger.info("Time last backup: {}".format(time_fim - time_ini))
			if time_fim - time_ini > self.backup_time:
				time_ini = time.time()
				self.backup()

			gc_fim = time.time()
			self.logger.info("Time last garbage collection: {}".format(gc_fim - gc_ini))
			if gc_fim - gc_ini > self.gc_time:
				self.logger.warning("Garbage collection")
				gc.collect()
				gc_ini = time.time()
