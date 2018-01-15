import psycopg2
import time
import datetime
from FlashCard import FlashCardSM

class Database:
	conn = None
	cursor = None

	def __init__(self):
		try:
			arq = open("connect_str.txt", "r")
			connect_str = arq.read()
			arq.close()
			print(connect_str)
			# use our connection values to establish a connection
			self.conn = psycopg2.connect(connect_str)
			# create a psycopg2 cursor that can execute queries
			self.cursor = self.conn.cursor()
			print("Connected with database!")
		except Exception as e:
			print("Uh oh, can't connect. Invalid dbname, user or password?")
			print(e)

	def __del__(self):
		self.conn.close()
		self.cursor.close()

	def add_user(self, ID):
		self.cursor.execute("SELECT id from users WHERE id={};".format(ID))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "Welcome back to LingoBot!"

		self.cursor.execute("INSERT INTO users VALUES ({}, DEFAULT, DEFAULT, DEFAULT, DEFAULT);".format(ID))
		self.conn.commit()
		return "Welcome to LingoBot!"

	def add_language(self, ID, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id={} AND language_name='{}';".format(ID, language))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == language:
				return "'{}' is already added".format(language)

		self.cursor.execute("INSERT INTO languages VALUES ({}, '{}');".format(ID, language))
		self.conn.commit()
		return "'{}' added successfully to your languages".format(language)

	def erase_language(self, ID, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE language_name={};".format(language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			return "{} is not in your languages".format(language)

		self.cursor.execute("DELETE FROM languages WHERE user_id={} AND language_name={};".format(ID, language))
		self.conn.commit()
		return "{} removed successfully".format()

	def add_word(self, ID, lst):
		#temp_user -> idioma outro_idioma ingles path1 path2 path3 ... final da lista
		language = lst[0]
		foreign_word = lst[1]
		english_word = lst[2]
		content_type = lst[3]

		self.cursor.execute("SELECT foreign_word FROM words WHERE user_id={} AND language='{}' AND foreign_word='{}';".format(ID, language, foreign_word))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "{} is already in your words"

		self.cursor.execute("SELECT highest_word_id FROM users WHERE id={};".format(ID))
		rows = self.cursor.fetchall()
		user_word_id = rows[0][0] + 1

		#UPDATE user's highest_word_id
		self.cursor.execute("UPDATE users SET highest_word_id={} WHERE id={}".format(user_word_id, ID))
		
		fc = FlashCardSM()
		self.cursor.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}', {}, {}, {}, {}, '{}')".format(ID, language, foreign_word, english_word, user_word_id,
																							fc.attempts, fc.ef, fc.interval,
																							str(fc.next_date.year) + '-' + str(fc.next_date.month) + '-' + str(fc.next_date.day)))
		self.conn.commit()

		counter = 0
		for i in range(4, len(lst)):
			content_path = lst[i]
			self.cursor.execute("INSERT INTO content VALUES ({}, '{}', '{}', {}, '{}', {}, '{}');".format(ID, language, foreign_word, user_word_id, content_type, counter, content_path))
			counter += 1

		self.conn.commit()
		return "Word and content added successfully!"

	def erase_word(self, ID, language, foreign_word):
		self.cursor.execute("SELECT FROM words WHERE id = {} AND language = '{}' AND foreign_word = '{}';".format(ID, language, foreign_word))
		rows = self.cursor.fetchall
		
		if len(rows) == 0:
			return "Invalid english word or foreign word"

		self.cursor.execute("DELETE FROM words WHERE id = {} AND language = '{}' AND foreign_word = '{}';".format(ID, language, foreign_word))

		self.conn.commit()
		return "Word erased successfully!"

	def get_known_users(self):
		known = set()
		self.cursor.execute("SELECT id FROM users;")
		rows = self.cursor.fetchall()
		for row in rows:
			known.add(row[0])

		return known

	def get_user_languages(self, ID):
		languages = []
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id={};".format(ID))
		rows = self.cursor.fetchall()
		for row in rows:
			languages.append(row[0])

		return languages

	def get_word(self, user_id, word_id):
		self.cursor.execute("SELECT * FROM words WHERE user_id={} AND user_word_id={};".format(user_id, word_id))
		rows = self.cursor.fetchall()
		return rows[0]

	def get_all_words_info(self, user_id):
		self.cursor.execute("SELECT * FROM words WHERE user_id={};".format(user_id))
		rows = self.cursor.fetchall()
		return rows

	def set_supermemo_data(self, word):
		self.cursor.execute("UPDATE words SET attempts={}, easiness_factor={}, interval={}, next_date='{}' WHERE user_id={} AND user_word_id={};"
			.format(word.attempts, word.ef, word.interval, word.next_date.strftime('%Y-%m-%d'), word.userID, word.wordID))
		self.conn.commit()

	def set_state(self, user_id, state, state2=0):
		self.cursor.execute("UPDATE users SET state={}, state2={} WHERE id={}".format(state, state2, user_id))
		self.conn.commit()

	def get_state(self, user_id):
		self.cursor.execute("SELECT state, state2 FROM users WHERE id={}".format(user_id))
		rows = self.cursor.fetchall()
		return rows[0]