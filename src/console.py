#! /usr/bin/python3
import sys
import os
import signal
import time
import logging
from MessageHandler import MessageHandler, MessageHandlerThread
from SendingManager import SendingManager, SendingManagerThread
from utilities import logging_utils
from threading import Thread


class LearnIt(Thread):

	def __init__(self, message_handler, sending_manager):
		Thread.__init__(self)
		self.locked = True
		self.continue_flag = True
		logging_utils.setup_learnit_thread()
		self.logger = logging.getLogger('learnit_thread')
		self.message_handler_thread = MessageHandlerThread(message_handler)
		self.sending_manager_thread = SendingManagerThread(sending_manager)

	def start_message_handler(self):
		self.logger.info("Starting message handler")
		self.message_handler_thread.start()

	def restart_bot_message_handler(self):
		self.logger.warning("Set to restart message handler bot")
		self.message_handler_thread.restart_bot()

	def stop_message_handler(self):
		self.logger.info("Stopping message handler")
		self.message_handler_thread.safe_stop()
		self.logger.info("Message Handler stopped!!")

	def start_sending_manager(self):
		self.logger.info("Starting sending manager")
		self.sending_manager_thread.start()

	def restart_bot_sending_manager(self):
		self.logger.warning("Set to restart sending manager bot")
		self.message_handler_thread.restart_bot()

	def stop_sending_manager(self):
		self.logger.info("Stopping sending manager")
		self.message_handler_thread.safe_stop()
		self.logger.info("Sending Manager stopped!!")

	def default(self):
		self.start_message_handler()
		self.start_sending_manager()

	def safe_stop(self):
		self.continue_flag = False
		while self.locked == True:
			time.sleep(0.5)
		self.stop_sending_manager()
		self.stop_message_handler()

	def run(self):
		self.logger.info("Running LearniIt")
		self.default()
		while self.continue_flag:
			self.locked = True
			self.logger.info("Check if idle time exceeded")
			sleep = self.message_handler_thread.idle_time_exceed()
			self.logger.info("Sleep {}".format(sleep))
			if sleep < 1:
				self.restart_bot_message_handler()
				self.restart_bot_sending_manager()
				sleep = self.message_handler_thread.get_max_idle_time()
				self.logger.info("Sleep {}".format(sleep))
				time.sleep(sleep)
			else:
				time.sleep(sleep)
			self.locked = False

class Console():


	def __init__(self, debug_mode, gui):
		self.debug_mode = debug_mode
		self.gui = gui
		self.message_handler = None
		self.sending_manager = None
		self.learnit = None
		self.MESSAGE_HANDLER_MAX_IDLE_TIME = 300
		self.SENDING_MANAGER_SLEEP_TIME = 240
		self.INSTALLED = False
		self.read_data()

		print("Installed: {}\nMax time idle: {}\nSleep time: {}\n".format(self.INSTALLED, self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.SENDING_MANAGER_SLEEP_TIME))

		if self.INSTALLED == False:
			self.install()

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
		print("System turning off...")
		self.learnit.safe_stop()
		self.message_handler.turn_off()
		self.sending_manager.stop()
		self.save_data()

	def turn_on(self):
		print("System turning on")
		self.message_handler = MessageHandler(self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.debug_mode)
		self.sending_manager = SendingManager(self.SENDING_MANAGER_SLEEP_TIME, self.debug_mode)
		self.learnit = LearnIt(self.message_handler, self.sending_manager)
		self.learnit.start()
		print("System turned on")


	def interactive(self):
		try:
			self.turn_on()
			while True:
				print(">>", end=' ')
				inp = input().split()

				if len(inp) == 0:
					continue

				if inp[0] == 'stop':
					break
				elif inp[0] == 'set' and len(inp) >= 3:
					if inp[1] == 'max_idle_time':
						MESSAGE_HANDLER_MAX_IDLE_TIME = int(inp[2])
					elif inp[1] == 'sleep_time':
						SENDING_MANAGER_SLEEP_TIME = int(inp[2])
				elif inp[0] == 'restart':
					turn_off()
					time.sleep(1)
					turn_on()
		except KeyboardInterrupt as e:
			pass	

	def run(self):
		if self.gui:
			self.interactive()
		else:
			try:
				while True:
					pass
			except KeyboardInterrupt:
				pass
		self.turn_off()	



if __name__ == '__main__':

	args = sys.argv
	args = args[1:]
	debug_mode = False
	gui = True

	if '--debug' in args:
		debug_mode = True

	if '--no-gui' in args:
		gui = False

	console = Console(debug_mode, gui)
	console.run()


	





	
