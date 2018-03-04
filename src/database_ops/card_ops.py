from database_ops.db_utils import create_card_with_row
import database_ops.archive_ops
import logging
from utilities import logging_utils

class CardOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.archive_ops = database_ops.archive_ops.ArchiveOps(conn,cursor, debug_mode)

	def get_highest_card_id(self, user_id):
		self.cursor.execute("SELECT highest_card_id FROM users WHERE id=%s", (user_id,))
		row = self.cursor.fetchall()
		if len(row) == 0:
			self.logger.warning("User {} doesn't exist".fomrat(user_id))
			return 
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
		self.cursor.execute("SELECT highest_card_id FROM users WHERE id=%s;", (user_id,))
		highest_card_id = self.cursor.fetchall()
		highest_card_id = highest_card_id[0][0]
		
		if highest_card_id < card_id:
			self.cursor.execute("UPDATE users SET highest_card_id=%s WHERE id=%s", (card_id, user_id))


		self.cursor.execute("INSERT INTO cards VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
			 (user_id, word_id, language, topic, foreign_word,
					card_id, content_type,
					card.attempts, card.ef, card.interval,
				str(card.next_date.year) + '-' + str(card.next_date.month) + '-' + str(card.next_date.day)))

		self.conn.commit()

		counter = 0
		for path in card.archives:
			counter += 1
			self.cursor.execute("INSERT INTO archives VALUES (%s, %s, %s, %s, %s)", 
									(user_id, card_id, counter, content_type, path))

		self.conn.commit()


	def get_card(self, user_id, user_card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND user_card_id=%s", 
							(user_id, user_card_id))
		row = self.cursor.fetchall()

		if len(row) == 0:
			self.logger.warning("Card {}, {} doesn't exist".format(user_id, user_card_id))
			return None

		row = row[0]
		card = create_card_with_row(row)

		self.cursor.execute("SELECT content_path FROM archives WHERE user_id=%s AND user_card_id=%s;", (user_id, user_card_id))
		rows = self.cursor.fetchall()
		for row in rows:
			card.add_archive(row[0])
		return card

	def get_cards_on_topic(self, user_id, language, topic, get_default):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND language=%s AND topic=%s", 
				(user_id, language, topic))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			self.logger.warning("Card {}, {}, {} doesn't exist".format(user_id, language, topic))
			return []

		cards = []
		for row in rows:
			card = create_card_with_row(row)
			if card.get_type() == 'default' and  get_default == False:
					continue
			user_card_id = card.get_card_id()
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id=%s AND user_card_id=%s;", (user_id, user_card_id))
			archives = self.cursor.fetchall()
			for archive in archives:
				card.add_archive(archive[0])
			cards.append(card)

		return cards

	def get_all_cards(self, user_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s", (user_id, ))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			self.logger.warning("{} - There's no cards registered".format(user_id))
			return []

		cards = []
		for row in rows:
			card = create_card_with_row(row)
			user_card_id = card.get_card_id()
			self.cursor.execute("SELECT content_path FROM archives WHERE user_id=%s AND user_card_id=%s;", (user_id, user_card_id))
			archives = self.cursor.fetchall()
			for archive in archives:
				card.add_archive(archive[0])
			cards.append(card)

		return cards
	

	def erase_card(self, user_id, user_card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND user_card_id=%s",
						(user_id, user_card_id))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			self.logger.warning("Card {}, {} doesn't exist".format(user_id, user_card_id))
			return 

		# erasing archives of the card
		self.cursor.execute("SELECT counter FROM archives WHERE user_id=%s AND user_card_id=%s;", (user_id, user_card_id))
		rows = self.cursor.fetchall()
		for row in rows:
			self.archive_ops.erase_archive(user_id,user_card_id,row[0])

		self.cursor.execute("DELETE FROM cards WHERE user_id=%s AND user_card_id=%s", (user_id, user_card_id))
		self.conn.commit()

		self.logger.info("Card {}, {} successfuly removed".format(user_id, user_card_id))
		return 


	def set_supermemo_data(self, card):
		"""Updates on the database the information about the supermemo algorithm that are contained in a word.

		Args:
		word: A Word instance.
		"""
		if self.check_card_existence(card.get_user(), card):
			self.cursor.execute("UPDATE cards SET attempts=%s, easiness_factor=%s, interval=%s, next_date=%s WHERE user_id=%s AND user_card_id=%s;",
								(card.attempts, card.ef, card.interval, card.next_date.strftime('%Y-%m-%d'), card.get_user(), card.card_id))
			self.conn.commit()


	def check_card_existence(self, user_id, card):
		self.cursor.execute("SELECT user_card_id FROM cards WHERE user_id=%s AND user_card_id=%s;", 
																		(user_id, card.get_card_id()))
		card = self.cursor.fetchall()
		if len(card) == 0:
			return False
		return True


