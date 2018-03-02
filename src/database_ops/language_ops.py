import database_ops.word_ops


class LanguageOps():

	def __init__(self, conn, cursor, debug_mode):
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.word_ops = database_ops.word_ops.WordOps(conn,cursor, debug_mode)


	def add_language(self, user_id, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == language:
				return "{} is already added".format(language)

		self.cursor.execute("INSERT INTO languages VALUES (%s, %s);", (user_id, language))
		self.conn.commit()
		return "{} added successfully to your languages".format(language)

	def erase_language(self, user_id, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			return "{} is not in your languages".format(language)

		self.cursor.execute("SELECT user_word_id FROM words WHERE user_id=%s AND language=%s;", (user_id, language))
		words = self.cursor.fetchall()

		for word in words:
			self.word_ops.erase_word(user_id, word[0])

		self.cursor.execute("DELETE FROM languages WHERE user_id=%s AND language_name=%s;", (user_id, language))
		self.conn.commit()
		return "{} removed successfully".format(language)


	def get_user_languages(self, user_id):
		languages = []
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id=%s;", (user_id, ))
		rows = self.cursor.fetchall()
		for row in rows:
			languages.append(row[0])

		return languages