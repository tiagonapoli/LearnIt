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

	def add_user(self, ID):
		self.cursor.execute("SELECT id from users WHERE id={}".format(ID))
		rows = self.cursor.fetchall()
		for row in rows:
			if row[0] == ID:
				return flags.Message.WELCOME

		self.cursor.execute("INSERT INTO users VALUES ({}, 0);".format(ID))
		self.conn.commit()
		return flags.Message.WELCOME_BACK

	def add_word(ID):
		#temp_user -> idioma outro_idioma ingles path1 path2 path3 ... final da lista
		idiom = temp_user[ID][0]
		foreign_word = temp_user[ID][1]
		english_word = temp_user[ID][2]

		cursor.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}')".format(ID, idiom, foreign_word, english_word))	

		for i in range(3, len(temp_user[ID])):
			img_path = temp_user[ID][i]
			cursor.execute("INSERT INTO images VALUES ({}, '{}', '{}', DEFAULT, '{}')".format(ID, idiom, foreign_word, img_path))

		conn.commit()
		BOT.send_message(ID, "Word and images added successfully!")

	def erase_word(ID, idiom, foreign_word):
		cursor.execute("SELECT FROM word WHERE id = {} AND english_word = '{}' AND foreign_word = '{}'".format(ID, idiom, foreign_word))
		rows = cursos.fetchall
		
		if len(rows) == 0:
			BOT.send_message(ID, "Invalid english word or foreign word")
			return

		cursor.execute("DELETE FROM word WHERE id = {} AND idiom = '{}' AND foreign_word = '{}'".format(ID, idiom, foreign_word))

		conn.commit()
		BOT.send_message(ID, "Word erased successfully!")