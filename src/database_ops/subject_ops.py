import logging
import database_ops.topic_ops


class SubjectOps():


	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.topic_ops = database_ops.topic_ops.TopicOps(conn,cursor, debug_mode)


	def erase_subject(self, user_id, subject):
		self.cursor.execute("SELECT topic FROM topics WHERE user_id=%s AND subject=%s;", 
			(user_id, subject))
		rows = self.cursor.fetchall()
		for row in rows:
			self.topic_ops.erase_topic(user_id, subject, row[0])


	def get_subjects(self, user_id):
		self.cursor.execute("SELECT subject, active FROM subjects WHERE user_id=%s;", (user_id, ))
		subjects = self.cursor.fetchall()
		ret = []
		for subject in subjects:
			ret.append((subject[0], subject[1]))
		return ret


	def get_active_subjects(self, user_id):
		self.cursor.execute("SELECT subject,active FROM subjects WHERE user_id=%s AND active!=0;", (user_id, ))
		subjects = self.cursor.fetchall()
		ret = []
		for subject in subjects:
			ret.append((subject[0], subject[1]))
		return ret


	def is_subject_active(self, user_id, subject):
		self.cursor.execute("SELECT active FROM subjects WHERE user_id=%s and subject=%s;", (user_id, subject))
		subject = self.cursor.fetchall()
		if len(subject) == 0:
			return None
		return subject[0][0]


	def set_subject_active(self, user_id, subject, active):
		self.cursor.execute("SELECT topic FROM topics WHERE user_id=%s AND subject=%s;", 
			(user_id, subject))
		rows = self.cursor.fetchall()
		for row in rows:
			self.topic_ops.set_topic_active(user_id, subject, row[0], active)

