#! /usr/bin/python3
import sys
import os
from LearnIt import LearnIt
from MessageHandler import MessageHandler
from SendingManager import SendingManager
from BotController import BotControllerFactory

class Console():


	def __init__(self, debug_mode, gui):
		self.debug_mode = debug_mode
		self.gui = gui
		self.message_handler = None
		self.sending_manager = None
		self.learnit = None
		self.MESSAGE_HANDLER_MAX_IDLE_TIME = 180
		self.SENDING_MANAGER_SLEEP_TIME = 120
		self.INSTALLED = False
		self.read_data()

		print("Installed: {}\nMax time idle: {}\nSleep time: {}\n".format(self.INSTALLED, self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.SENDING_MANAGER_SLEEP_TIME))

		if self.INSTALLED == False:
			self.install()
			
		arq = None
		if debug_mode:
			arq = open("../credentials/bot_debug_token.txt", "r")
		else:
			arq = open("../credentials/bot_token.txt", "r")
		TOKEN = (arq.read().splitlines())[0]
		arq.close()
		self.bot_controller_factory = BotControllerFactory(TOKEN)

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
		self.save_data()
		print("Saved data")
		self.learnit.safe_stop()

	def turn_on(self):
		print("System turning on")
		self.message_handler = MessageHandler(self.MESSAGE_HANDLER_MAX_IDLE_TIME, self.bot_controller_factory, self.debug_mode)
		self.sending_manager = SendingManager(self.SENDING_MANAGER_SLEEP_TIME, self.bot_controller_factory, self.debug_mode)
		self.learnit = LearnIt(self.message_handler, self.sending_manager, self.bot_controller_factory)
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
					self.learnit.restart_bot_sending_manager()
					self.learnit.restart_bot_message_handler()
		except KeyboardInterrupt as e:
			pass	

	def run(self):
		if self.gui:
			self.interactive()
		else:
			self.turn_on()
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
