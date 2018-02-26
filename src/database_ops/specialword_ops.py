import psycopg2
import time
from database_ops.db_utils import treat_str_SQL, create_card_with_row
from utilities import logging_utils
import database_ops.archive_ops
import logging
import os



class SpecialWordOps():

	def __init__(self, conn, cursor, debug_mode):
		self.debug_mode = debug_mode
		self.logger = logging.getLogger(__name__)
		path = '../logs/specialwords_ops.log'
		if debug_mode:
			path = '../logs_debug/specialwords_ops.log'
		logging_utils.setup_logger_default(self.logger, path)
		self.conn = conn
		self.cursor = cursor

	def check_existence(self, archive):
		tries = 5
		while tries > 0:
			tries -= 1
			try:
				self.cursor.execute("SELECT * FROM specialwords WHERE archive='{}'".format(treat_str_SQL(archive)))
				rows = self.cursor.fetchall()
				if(len(rows) > 0):
					return True
				return False
			except:
				self.logger.error("Error check_existence {}".format(archive), exc_info=True)
				time.sleep(1)
		return False

	def get_users_using(self, archive):
		tries = 5
		while tries > 0:
			tries -= 1
			try:
				self.cursor.execute("SELECT users_using FROM specialwords WHERE archive='{}'".format(treat_str_SQL(archive)))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_users_using {}".format(archive), exc_info=True)
				time.sleep(1)
		return 0

	def erase_specialword(self, word_text):
		archive = word_text
		tries = 5
		while tries > 0:
			tries -= 1
			try:
				if self.check_existence(archive):
					users_using = self.get_users_using(archive)
					if users_using == 1:
						os.remove(archive.split()[1])
						self.logger.info("Erase file {}".format(archive))
						self.cursor.execute("DELETE FROM specialwords WHERE archive='{}'".format(treat_str_SQL(archive)))
						self.conn.commit()
					else:
						self.cursor.execute("UPDATE specialwords SET users_using={} WHERE archive='{}'".format(users_using - 1, treat_str_SQL(archive)))
				return
			except:
				self.logger.error("Error in erase_specialword".format(archive), exc_info=True)
				time.sleep(1)	

	def add_specialword(self, word):
		archive = word.get_word()
		tries = 5
		while tries > 0:
			tries -= 1
			try:
				if self.check_existence(archive):
					users_using = self.get_users_using(archive)
					self.cursor.execute("UPDATE specialwords SET users_using={} WHERE archive='{}'".format(users_using + 1, treat_str_SQL(archive)))
				else:
					self.cursor.execute("INSERT INTO specialwords VALUES (DEFAULT, '{}');".format(treat_str_SQL(archive)))
					self.conn.commit()
				return
			except:
				self.logger.error("Error add_specialword".format(archive), exc_info=True)
				time.sleep(1)			
