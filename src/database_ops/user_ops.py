import time
import logging
from utilities import logging_utils, bot_utils	

class UserOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor

	def get_state(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT state1, state2 FROM users WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (user_id, ))
				row = self.cursor.fetchall()
				if len(row) == 0:
					self.logger.warning("User {} doesn't exist".format(user_id))
					return 
				return (row[0][0], row[0][1])
			except:
				self.logger.error("Error get_state {}".format(user_id), exc_info=True)
				time.sleep(1)
		return []



	def set_state(self, user_id, state1, state2):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET state1=%s, state2=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (state1, state2, user_id))
				self.conn.commit()
				return
			except:
				self.logger.error("Error set_state {}".format(user_id), exc_info=True)
				time.sleep(1)
				

	def add_user(self, user_id, username):
		tries = 20
		while tries > 0:
			tries -= 1
			try:
				self.cursor.execute("SELECT user_id from users WHERE user_id=%s;", (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) > 0):
					return True
				self.cursor.execute("INSERT INTO users VALUES (%s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT);", (user_id, username))
				self.conn.commit()
				return True
			except:
				self.logger.error("Error add_user {} {}".format(user_id, username), exc_info=True)
				time.sleep(1)
				
		return False

	def get_known_users(self):
		tries = 5
		while tries > 0:
			tries -= 1
			known = []
			cmd = "SELECT user_id FROM users;"
			try:
				self.cursor.execute(cmd)
				rows = self.cursor.fetchall()
				for row in rows:
					known.append(row[0])
				return known
			except:
				self.logger.error("Error get_known_users", exc_info=True)
				time.sleep(1)
		return []

		

	def get_learning_words_limit(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT learning_words_per_day from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_learning_words_limit {}".format(user_id), exc_info=True)
				time.sleep(1)
		return 0


	def set_card_waiting(self, user_id, card_id):
		tries = 20
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET card_waiting=%s WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (card_id, user_id))
				self.conn.commit()
				return
			except:
				self.logger.error("Error set_card_waiting {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None

		
	def get_card_waiting(self, user_id):
		tries = 20
		while tries > 0:
			tries -= 1
			cmd = "SELECT card_waiting FROM users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				card = self.cursor.fetchall()
				if(len(card) == 0):
					return 0
				return card[0][0]
			except:
				self.logger.error("Error get_card_waiting {}".format(user_id), exc_info=True)
				time.sleep(1)
		return 0


	def get_grade_waiting(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT grade_waiting_for_process from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return None
				return rows[0][0]
			except:
				self.logger.error("Error get_grade_waiting {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def set_grade_waiting(self, user_id, grade):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET grade_waiting_for_process=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (grade, user_id))
				self.conn.commit()
				return
			except:
				self.logger.error("Error set_grade_waiting {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def get_card_waiting_type(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT card_waiting_type from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_card_waiting_type {}".format(user_id), exc_info=True)
				time.sleep(1)

		return None

		
	def set_card_waiting_type(self, user_id, card_waiting_type):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET card_waiting_type=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (card_waiting_type, user_id))
				self.conn.commit()
				return 
			except:
				self.logger.error("Error set_card_waiting_type {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def get_cards_per_hour(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT cards_per_hour from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_cards_per_hour {}".format(user_id), exc_info=True)
				time.sleep(1)

		return None

		
	def set_cards_per_hour(self, user_id, cards_per_hour):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET cards_per_hour=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (cards_per_hour, user_id))
				self.conn.commit()
				return 
			except:
				self.logger.error("Error set_cards_per_hour {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def get_active(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT active from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_active {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def set_active(self, user_id, active):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET active=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (active, user_id))
				self.conn.commit()
				return 
			except:
				self.logger.error("Error set_active {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def get_id_by_username(self, username):
		tries = 20
		while tries > 0:
			tries -= 1
			cmd = "SELECT user_id from users WHERE username=%s;"
			try:
				self.cursor.execute(cmd, (username, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return None
				return rows[0][0]
			except:
				self.logger.error("Error get_id_by_username {}".format(username), exc_info=True)
				time.sleep(1)
		return None
			

	def get_public(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT public from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_public {}".format(user_id), exc_info=True)
				time.sleep(1)
		return 0

	def get_username(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT username from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_username {}".format(user_id), exc_info=True)
				time.sleep(1)
		return 0


	def set_public(self, user_id, public):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET public=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (public, user_id))
				self.conn.commit()
				return 
			except:
				self.logger.error("Error set_public {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None


	def get_native_language(self, user_id):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "SELECT native_language from users WHERE user_id=%s;"
			try:
				self.cursor.execute(cmd, (user_id, ))
				rows = self.cursor.fetchall()
				if(len(rows) == 0):
					return 0
				return rows[0][0]
			except:
				self.logger.error("Error get_native_language {}".format(user_id), exc_info=True)
				time.sleep(1)
		return 0


	def set_native_language(self, user_id, language):
		tries = 5
		while tries > 0:
			tries -= 1
			cmd = "UPDATE users SET native_language=%s WHERE user_id=%s"
			try:
				self.cursor.execute(cmd, (language, user_id))
				self.conn.commit()
				return 
			except:
				self.logger.error("Error set_native_language {}".format(user_id), exc_info=True)
				time.sleep(1)
		return None



		
