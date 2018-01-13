import psycopg2
import flags

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
		self.cursor.execute("SELECT id from users WHERE id={}".format(ID))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == ID:
				return "Welcome to LingoBot!"

		self.cursor.execute("INSERT INTO users VALUES ({}, 0);".format(ID))
		self.conn.commit()
		return "Welcome back to LingoBot!"

	def add_language(ID, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE language_name={};".format(language))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == language:
				return "{} is already added".format(language)

		self.cursor.execute("INSERT INTO languages VALUES ({}, '{}');".format(ID, language))
		self.conn.commit()
		return "{} added successfully to your languages".format(language)

	def erase_language(ID, language):
		self.cursor.execute("SELECT language_name FROM languages WHERE language_name={};".format(language))
		rows = self.cursor.fetchall()
		if(len(rows) == 0):
			return "{} is not in your languages".format(language)

		self.cursor.execute("DELETE FROM languages WHERE user_id={} AND language_name={};".format(ID, language))
		self.conn.commit()
		return "{} removed successfully".format()

	def add_word(ID):
		#temp_user -> idioma outro_idioma ingles path1 path2 path3 ... final da lista
		language = temp_user[ID][0]
		foreign_word = temp_user[ID][1]
		english_word = temp_user[ID][2]

		self.cursor.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}')".format(ID, language, foreign_word, english_word))

		for i in range(3, len(temp_user[ID])):
			image_path = temp_user[ID][i]
			cursor.execute("INSERT INTO images VALUES ({}, '{}', '{}', DEFAULT, '{}');".format(ID, language, foreign_word, image_path))

		self.conn.commit()
		return "Word and images added successfully!"

	def erase_word(ID, language, foreign_word):
		self.cursor.execute("SELECT FROM words WHERE id = {} AND language = '{}' AND foreign_word = '{}';".format(ID, language, foreign_word))
		rows = self.cursos.fetchall
		
		if len(rows) == 0:
			return "Invalid english word or foreign word"

		self.cursor.execute("DELETE FROM words WHERE id = {} AND language = '{}' AND foreign_word = '{}';".format(ID, language, foreign_word))

		self.conn.commit()
		return "Word erased successfully!"

	def get_known_users():
		known = set()
		self.cursor.execute("SELECT id FROM users;")
		rows = self.cursor.fetchall()
		for row in rows:
			known.add(row[0])

		return known

	def get_user_languages(ID):
		languages = []
		self.cursor.execute("SELECT language_name FROM languages WHERE user_id={};".format(ID))
		rows = self.cursor.fetchall()
		for row in rows:
			languages.append(row[0])

		return languages