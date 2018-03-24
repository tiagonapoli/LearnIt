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
import threading
import gc

class LearnItThread(threading.Thread):

	def __init__(self, learnit_sleep, message_handler, sending_manager, bot_controller_factory):
		threading.Thread.__init__(self, name="LearnItThread")
		self.lock = threading.Lock()
		self.__stop = threading.Event()

		self.learnit_sleep = learnit_sleep
		logging_utils.setup_learnit()
		logging_utils.setup_message_handler()
		logging_utils.setup_sending_manager()
		logging_utils.setup_database()
		logging_utils.setup_bot_sender(bot_controller_factory)
		self.bot_logger = logging.getLogger('Bot_Sender')
		self.logger = logging.getLogger('LearnIt')
		self.message_handler_thread = MessageHandlerThread(message_handler)
		self.sending_manager_thread = SendingManagerThread(sending_manager)

	def start_message_handler(self):
		self.message_handler_thread.start()

	def restart_bot_message_handler(self):
		self.logger.warning("Set to restart MH bot")
		self.message_handler_thread.restart_bot()

	def stop_message_handler(self):
		self.message_handler_thread.stop()
		self.logger.warning("Requested MH to stop")

	def start_sending_manager(self):
		self.sending_manager_thread.start()

	def stop_sending_manager(self):
		self.sending_manager_thread.stop()
		self.logger.warning("Requested SM to stop")

	def default(self):
		self.start_message_handler()
		self.start_sending_manager()

	def backup(self):
		self.logger.warning("Start backup")
		self.message_handler_thread.backup()
		self.logger.warning("Ended backup")

	def safe_stop(self):
		self.__stop.set()
		self.lock.acquire()

		self.logger.warning("LearnIt Safe Stop!")

		self.stop_sending_manager()
		self.stop_message_handler()

		self.backup()

		self.logger.warning("Waiting MH to stop")
		while self.message_handler_thread.is_alive():
			try:
				self.message_handler_thread.join(2)
			except:
				pass
			self.stop_message_handler()
		self.logger.warning("MH stopped!")
		self.logger.warning("Waiting SM to stop")
		while self.sending_manager_thread.is_alive():
			try:
				self.sending_manager_thread.join(2)
			except:
				pass
			self.stop_sending_manager()

		self.logger.warning("SM stopped!")

		self.lock.release()

	def run(self):
		self.logger.warning("Running LearniIt")
		self.default()
		cycles = 0
		while not self.__stop.wait(self.learnit_sleep):
			msg = ''
			for x in threading.enumerate():
				msg += str(x.name) + "\n"

			self.logger.warning("LearnIt_Cycles:{}  Threads: ".format(cycles) + str(threading.active_count()) + "\n" + msg)
			self.bot_logger.warning("LearnIt_Cycles:{}  Threads: ".format(cycles) + str(threading.active_count()) + "\n" + msg)

			self.lock.acquire()
			if self.__stop.wait(0):
				self.lock.release()
				break

			if cycles % 4 == 3:
				self.restart_bot_message_handler()
				self.backup()

			self.lock.release()
			self.logger.info("LearnIt Sleep {}".format(self.learnit_sleep))
			cycles += 1



class Container():

		def end_func(self, signal, frame):
			print("---------End LearnIt---------")
			self.__stop.set()

		def __init__(self, debug_mode):
			signal.signal(signal.SIGINT, self.end_func)
			signal.signal(signal.SIGTERM, self.end_func)

			self.__stop = threading.Event()

			self.debug_mode = debug_mode
			self.message_handler = None
			self.sending_manager = None
			self.learnit = None
			self.SENDING_MANAGER_SLEEP_TIME = 120
			self.LEARNIT_SLEEP = 3600
			self.INSTALLED = False
			self.read_data()
			self.save_data()

			print("Installed: {}\nLearnIt Sleep: {}\nSM Sleep time: {}\n".format(self.INSTALLED, self.LEARNIT_SLEEP,self.SENDING_MANAGER_SLEEP_TIME))

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
			f.write("{} {} {}".format(self.INSTALLED,self.LEARNIT_SLEEP, self.SENDING_MANAGER_SLEEP_TIME))
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
				self.LEARNIT_SLEEP = int(data[1])
				self.SENDING_MANAGER_SLEEP_TIME = int(data[2])
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
			self.message_handler = MessageHandler(self.bot_controller_factory, self.debug_mode)
			self.sending_manager = SendingManager(self.SENDING_MANAGER_SLEEP_TIME, self.bot_controller_factory, self.debug_mode)
			self.learnit = LearnItThread(self.LEARNIT_SLEEP, self.message_handler, self.sending_manager, self.bot_controller_factory)
			self.learnit.start()
			print("System turned on")

		def run(self):
			self.turn_on()
			self.__stop.wait()
			print("Stop ask stop bot")
			self.turn_off()

if __name__ == '__main__':

	args = sys.argv
	args = args[1:]
	debug_mode = False

	if '--debug' in args:
		debug_mode = True

	container = Container(debug_mode)
	container.run()
