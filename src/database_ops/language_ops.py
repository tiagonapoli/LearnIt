import database_ops.word_ops
import logging
from utilities import logging_utils

class LanguageOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.word_ops = database_ops.word_ops.WordOps(conn,cursor, debug_mode)


	def add_language(self, user_id, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == language:
				self.logger.warning("{} - {} is already added".format(user_id, language))
				return False 

		self.cursor.execute("INSERT INTO languages VALUES (%s, %s);", (user_id, language))
		self.conn.commit()

		self.logger.info("{} added successfully to {} languages".format(language, user_id))
		return True

	def erase_language(self, user_id, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			self.logger.warning("{} is not in {} languages".format(language, user_id))
			return False

		self.cursor.execute("SELECT user_word_id FROM words WHERE user_id=%s AND language=%s;", (user_id, language))
		words = self.cursor.fetchall()

		for word in words:
			self.word_ops.erase_word(user_id, word[0])

		self.cursor.execute("DELETE FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		self.conn.commit()

		self.logger.info("{} - {} removed successfully".format(user_id, language))
		return True


	def get_user_languages(self, user_id):
		languages = []
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s;", (user_id, ))
		rows = self.cursor.fetchall()
		for row in rows:
			languages.append(row[0])

		return languages