import database_ops.word_ops
import logging
from utilities import logging_utils

class TopicOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor


	def add_topic(self, user_id, language, topic):
		self.cursor.execute("SELECT topic FROM topics WHERE user_id=%s AND language=%s AND topic=%s;", (user_id, language, topic))
		row = self.cursor.fetchall()

		if(len(row) > 0):
			return

		self.cursor.execute("INSERT INTO topics VALUES (%s, %s, %s)", (user_id, language, topic))
		self.conn.commit()



	def get_all_topics(self, user_id, language):
		self.cursor.execute("SELECT topic FROM topics WHERE user_id=%s AND language=%s;", (user_id, language))
		topics = self.cursor.fetchall()

		ret = []
		for topic in topics:
			ret.append(topic[0])

		return ret;


	def erase_topic_empty_words(self, user_id, language, topic):
		self.cursor.execute("SELECT * FROM topics WHERE user_id=%s AND language=%s AND topic=%s;", (user_id,language,topic))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			self.logger.warning("Topic {},{},{} doesn't exist.".format(user_id,language,topic))
			return

		self.cursor.execute("DELETE FROM topics WHERE user_id=%s AND language=%s AND topic=%s;", (user_id, language,topic))
		self.conn.commit()

		self.logger.info("Topic {},{},{} erased.".format(user_id, language, topic))
		return