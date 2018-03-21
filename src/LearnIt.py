#! /usr/bin/python3
import sys
import os
import signal
import time
import logging
from MessageHandler import MessageHandlerThread, MessageHandler
from SendingManager import SendingManagerThread, SendingManager
from BotController import BotControllerFactory
from utilities import logging_utils
from threading import Thread
import gc

class LearnItThread(Thread):

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

	def partial_sleep(self, sleep, divisions):
		cnt = divisions
		mini_sleep = sleep / divisions
		while cnt > 0 and self.continue_flag:
			time.sleep(mini_sleep)
			cnt -= 1

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
				self.partial_sleep(sleep, 10)
			else:
				self.locked = False
				self.partial_sleep(sleep, 10)

			time_fim = time.time()
			self.logger.info("Time last backup: {}".format(time_fim - time_ini))
			if time_fim - time_ini > self.backup_time:
				time_ini = time.time()
				self.backup()


class Container():

		def end_func(self, signal, frame):
			print("---------End LearnIt---------")
			self.continue_flag = False

		def __init__(self, debug_mode):
			signal.signal(signal.SIGINT, self.end_func)
			signal.signal(signal.SIGTERM, self.end_func)

			self.continue_flag = True

			self.debug_mode = debug_mode
			self.message_handler = None
			self.sending_manager = None
			self.learnit = None
			self.MESSAGE_HANDLER_MAX_IDLE_TIME = 180
			self.SENDING_MANAGER_SLEEP_TIME = 120
			self.INSTALLED = False
			self.read_data()
			self.save_data()

			print("Installed: {}\nMax time idle: {}\nSleep time: {}\n".format(self.INSTALLED, self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.SENDING_MANAGER_SLEEP_TIME))

			if self.INSTALLED == False:
				self.install()

			arq = None
			if debug_mode:
				arq = open("../credentials/bot_debug_token.txt", "r")
			else:
				arq = open("../credentials/bot_token.txt", "r")
			self.TOKEN = (arq.read().splitlines())[0]
			arq.close()
			self.bot_controller_factory = BotControllerFactory(self.TOKEN)

		def install(self):
			os.system("./install.py")
			self.INSTALLED = True

		def save_data(self):
			f = open('../config.ini', 'w')
			f.write("{} {} {}".format(self.INSTALLED, self.SENDING_MANAGER_SLEEP_TIME, self.MESSAGE_HANDLER_MAX_IDLE_TIME))
			f.close()

		def read_data(self):
			try:
				f = open('../config.ini', 'r')
				data = f.read().split()
				f.close()
				if len(data) < 3:
					return

				if data[0] == 'True':
					self.INSTALLED = True
				else:
					self.INSTALLED = False
				self.SENDING_MANAGER_SLEEP_TIME = int(data[1])
				self.MESSAGE_HANDLER_MAX_IDLE_TIME = int(data[2])
			except FileNotFoundError:
				print("config.ini doesn't exist...")

		def turn_off(self):
			if self.learnit == None:
				return
			print("System turning off...")
			self.save_data()
			print("Saved data")
			self.learnit.safe_stop()
			if self.learnit.is_alive():
				print("Waiting for learnit to stop")
				self.learnit.join()

			del self.learnit
			del self.message_handler
			del self.sending_manager
			del self.bot_controller_factory
			gc.collect()

		def turn_on(self):
			print("System turning on")
			self.bot_controller_factory = BotControllerFactory(self.TOKEN)
			self.message_handler = MessageHandler(self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.bot_controller_factory, self.debug_mode)
			self.sending_manager = SendingManager(self.SENDING_MANAGER_SLEEP_TIME, self.bot_controller_factory, self.debug_mode)
			self.learnit = LearnItThread(self.message_handler, self.sending_manager, self.bot_controller_factory)
			self.learnit.start()
			print("System turned on")

		def run(self):
			self.turn_on()
			while self.continue_flag:
				time.sleep(0.5)
			self.turn_off()

if __name__ == '__main__':

	args = sys.argv
	args = args[1:]
	debug_mode = False

	if '--debug' in args:
		debug_mode = True

	container = Container(debug_mode)
	container.run()
