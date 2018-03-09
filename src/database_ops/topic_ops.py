import logging
import database_ops.study_item_ops


class TopicOps():


	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.study_item_ops = database_ops.study_item_ops.StudyItemOps(conn,cursor, debug_mode)


	def erase_topic(self, user_id, subject, topic):
		self.cursor.execute("SELECT study_item_id FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s;", 
			(user_id, subject, topic))
		rows = self.cursor.fetchall()
		for row in rows:
			self.study_item_ops.erase_study_item(user_id, row[0])


	def get_topics(self, user_id, subject):
		self.cursor.execute("SELECT topic, active FROM topics WHERE user_id=%s and subject=%s;", (user_id, subject))
		topics = self.cursor.fetchall()
		ret = []
		for topic in topics:
			ret.append((topic[0], topic[1]))
		return ret


	def get_active_topics(self, user_id, subject):
		self.cursor.execute("SELECT topic,active FROM topics WHERE user_id=%s and subject=%s and active!=0;", (user_id, subject))
		topics = self.cursor.fetchall()
		ret = []
		for topic in topics:
			ret.append((topic[0], topic[1]))
		return ret


	def is_topic_active(self, user_id, subject, topic):
		self.cursor.execute("SELECT active FROM topics WHERE user_id=%s and subject=%s AND topic=%s;", (user_id, subject, topic))
		topics = self.cursor.fetchall()
		if len(topics) == 0:
			return None
		return topics[0][0]


	def set_topic_active(self, user_id, subject, topic, active):
		self.cursor.execute("SELECT study_item_id FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s;", 
			(user_id, subject, topic))
		rows = self.cursor.fetchall()
		for row in rows:
			self.study_item_ops.set_study_item_active(user_id, row[0], active)

	