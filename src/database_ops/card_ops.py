import psycopg2
import time
import datetime
from flashcard import Card
from database_ops.db_utils import treat_str_SQL, create_card_with_row
import database_ops.archive_ops



class CardOps():

	def __init__(self, conn, cursor, debug_mode):
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.archive_ops = database_ops.archive_ops.ArchiveOps(conn,cursor, debug_mode)

	def get_highest_card_id(self, user_id):
		self.cursor.execute("SELECT highest_card_id FROM users WHERE id={}".format(user_id))
		row = self.cursor.fetchall()
		if len(row) == 0:
			return "User doesn't exist"
		return row[0][0]


	def add_card(self, card):
		
		user_id = card.get_user()
		word_id = card.get_word_id()
		card_id = card.get_card_id()
		language = card.get_language()
		content_type = card.get_type()
		foreign_word = card.get_word()
		topic = card.get_topic()

		#Update user's highest_card_id
		self.cursor.execute("SELECT highest_card_id FROM users WHERE id={};".format(user_id))
		highest_card_id = self.cursor.fetchall()
		highest_card_id = highest_card_id[0][0]
		
		if highest_card_id < card_id:
			self.cursor.execute("UPDATE users SET highest_card_id={} WHERE id={}".format(card_id, user_id))


		self.cursor.execute("INSERT INTO cards VALUES ({}, {}, '{}', '{}', '{}', {}, '{}', {}, {}, {}, '{}')"
			.format(user_id, word_id, treat_str_SQL(language), treat_str_SQL(topic), treat_str_SQL(foreign_word),
					card_id, treat_str_SQL(content_type),
					card.attempts, card.ef, card.interval,
				str(card.next_date.year) + '-' + str(card.next_date.month) + '-' + str(card.next_date.day)))

		self.conn.commit()

		counter = 0
		for path in card.archives:
			counter += 1
			self.cursor.execute("INSERT INTO archives VALUES ({}, {}, {}, '{}', '{}')"
									.format(user_id, card_id, counter, treat_str_SQL(content_type), treat_str_SQL(path)))

		self.conn.commit()


	def get_card(self, user_id, user_card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} AND user_card_id={}"
				.format(user_id, user_card_id))
		row = self.cursor.fetchall()

		if len(row) == 0:
			print("Error in get_card")
			print("Card {}, {} doesn't exist".format(user_id, user_card_id))		
			return None

		row = row[0]
		card = create_card_with_row(row)

		self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
		rows = self.cursor.fetchall()
		for row in rows:
			card.add_archive(row[0])
		return card

	def get_cards_on_topic(self, user_id, language, topic, get_default):
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} AND language='{}' AND topic='{}'"
				.format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			print("Error in get_cards_on_topic")
			print("Card {}, {}, {} doesn't exist".format(user_id, language, topic))		
			return []

		cards = []
		for row in rows:
			card = create_card_with_row(row)
			if card.get_type() == 'default' and  get_default == False:
					continue
			user_card_id = card.get_card_id()
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
			archives = self.cursor.fetchall()
			for archive in archives:
				card.add_archive(archive[0])
			cards.append(card)

		return cards

	def get_all_cards(self, user_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id={}"
				.format(user_id))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			print("EMPTY in get_all_cards")
			return []

		cards = []
		for row in rows:
			card = create_card_with_row(row)
			user_card_id = card.get_card_id()
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
			archives = self.cursor.fetchall()
			for archive in archives:
				card.add_archive(archive[0])
			cards.append(card)

		return cards
	

	def erase_card(self, user_id, user_card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id={} AND user_card_id={}"
						.format(user_id, user_card_id))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			print("Error in erase_card, dbapi")
			print("Card {}, {} doesn't exist".format(user_id, user_card_id))
			return "Card {}, {} doesn't exist".format(user_id, user_card_id)

		# erasing archives of the card
		self.cursor.execute("SELECT counter FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
		rows = self.cursor.fetchall()
		for row in rows:
			self.archive_ops.erase_archive(user_id,user_card_id,row[0])

		self.cursor.execute("DELETE FROM cards WHERE user_id={} AND user_card_id={}"
						.format(user_id, user_card_id))
		self.conn.commit()
		return "Card successfuly removed"


	def set_supermemo_data(self, card):
		"""Updates on the database the information about the supermemo algorithm that are contained in a word.

		Args:
		word: A Word instance.
		"""
		if self.check_card_existence(card.get_user(), card):
			self.cursor.execute("UPDATE cards SET attempts={}, easiness_factor={}, interval={}, next_date='{}' WHERE user_id={} AND user_card_id={};"
			.format(card.attempts, card.ef, card.interval, card.next_date.strftime('%Y-%m-%d'), card.get_user(), card.card_id))
			self.conn.commit()


	def check_card_existence(self, user_id, card):
		self.cursor.execute("SELECT user_card_id FROM cards WHERE user_id={} AND user_card_id={};".format(user_id, card.get_card_id()))
		card = self.cursor.fetchall()
		if len(card) == 0:
			return False
		return True


