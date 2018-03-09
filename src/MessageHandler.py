import time
import logging

import message_handlers.cancel
import message_handlers.error_handling
import message_handlers.add_item
'''
import message_handlers.copy_words
import message_handlers.list_words
import message_handlers.erase_words

import message_handlers.add_language 
import message_handlers.list_languages 
import message_handlers.erase_languages
'''

import message_handlers.settings
import message_handlers.stop
import message_handlers.help
import message_handlers.setup_user
'''
import message_handlers.topic_review
import message_handlers.card_answering
'''
import message_handlers.message_not_understood

from utilities import logging_utils, bot_utils, utils
from UserManager import UserManager
from BotController import BotControllerFactory
from threading import Thread


class MessageHandler():

	def __init__(self, max_idle_time, bot_controller_factory, debug_mode):
		self.max_idle_time = max_idle_time
		self.debug_mode = debug_mode
		self.bot_controller_factory = bot_controller_factory
		self.logger = logging.getLogger('learnit_thread')
		#self.bot_logger = logging.getLogger('bot_sender')
		self.bot = bot_utils.open_bot(self.debug_mode, self.logger)
		self.user_manager = UserManager(self.bot_controller_factory, self.debug_mode)
		self.user_manager.reset_all_states()
		self.continue_flag = False

	def idle_time_exceed(self):
		now = time.time()
		ret = 99999999
		for user_id, user in self.user_manager.users.items():
			if ret > now - user.get_last_op_time():
				ret = now - user.get_last_op_time()
		if ret == 99999999:
			ret = 0
		return self.max_idle_time - ret

	def restart_bot(self):
		if self.bot != None:
			self.bot.stop_polling()


	def stop(self):
		self.continue_flag = False
		if self.bot != None:
			self.bot.stop_polling()


	def reset_exception(self):
		self.setup_bot()
		self.user_manager.reset_all_states_exception()


	def backup(self):
		self.user_manager.reset_all_states_turn_off()
		utils.backup(self.bot, self.user_manager,self.debug_mode)
	

	def setup_bot(self):
		self.logger.warning("Setup message handler")
		del self.bot
		self.bot = None

		for user_id, user in self.user_manager.users.items():
			user.set_last_op_time()

		self.bot = bot_utils.open_bot(self.debug_mode, self.logger)
		#logging_utils.setup_bot_sender()

		message_handlers.setup_user.handle_setup_user(self.bot, self.user_manager,self.debug_mode)
		message_handlers.error_handling.handle_user_dont_exist(self.bot, self.user_manager,self.debug_mode)	
		message_handlers.cancel.handle_cancel(self.bot, self.user_manager,self.debug_mode)
		message_handlers.add_item.handle_add_item(self.bot, self.user_manager,self.debug_mode)
		'''
		message_handlers.card_answering.handle_card_answer(self.bot, self.user_manager,self.debug_mode)
		message_handlers.list_languages.handle_list_languages(self.bot, self.user_manager,self.debug_mode)
		message_handlers.erase_languages.handle_erase_languages(self.bot, self.user_manager,self.debug_mode)
		message_handlers.copy_words.handle_copy_words(self.bot, self.user_manager,self.debug_mode)
		message_handlers.list_words.handle_list_words(self.bot, self.user_manager,self.debug_mode)
		message_handlers.erase_words.handle_erase_words(self.bot, self.user_manager,self.debug_mode)
		message_handlers.topic_review.handle_topic_review(self.bot, self.user_manager,self.debug_mode)
		'''
		message_handlers.settings.handle_settings(self.bot, self.user_manager,self.debug_mode)
		message_handlers.help.handle_help(self.bot, self.user_manager,self.debug_mode)
		message_handlers.stop.handle_stop(self.bot, self.user_manager,self.debug_mode)
		message_handlers.message_not_understood.handle_message_not_understood(self.bot, self.user_manager,self.debug_mode)

	def run(self):
		self.continue_flag = True
		while self.continue_flag:
			try:
				self.setup_bot()					
				self.bot.polling()	
			except Exception as e:
				if self.bot != None:
					self.bot.stop_polling()
					time.sleep(5)
				self.reset_exception()
				#self.bot_logger.error("Bot Crashed {}".format(e.__class__.__name__), exc_info=True)
				self.logger.error("Bot Crashed {}".format(e.__class__.__name__), exc_info=True)	
				time.sleep(5)


class MessageHandlerThread(Thread):

	def __init__(self, message_handler):
		Thread.__init__(self)
		self.message_handler = message_handler

	def safe_stop(self):
		self.message_handler.stop()
	
	def run(self):
		self.message_handler.run()

	def restart_bot(self):
		self.message_handler.restart_bot()

	def backup(self):
		self.message_handler.backup()

	def idle_time_exceed(self):
		return self.message_handler.idle_time_exceed()

	def get_max_idle_time(self):
		return self.message_handler.max_idle_time

if __name__ == '__main__':
	import BotController
	message_handler = MessageHandler(60, BotControllerFactory('540185672:AAHDW57BvDSqRtXKXWfbRL44Ik1JIuXzYeg'), 1)
	message_handler.run()