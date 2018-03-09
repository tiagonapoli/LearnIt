import logging
import os
from Flashcard import Card


class CardOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		

	def get_highest_card_id(self, user_id):
		self.cursor.execute("SELECT highest_card_id FROM users WHERE user_id=%s", (user_id,))
		row = self.cursor.fetchall()
		if len(row) == 0:
			self.logger.warning("User {} doesn't exist".format(user_id))
			return 
		return row[0][0]


	def add_card(self, card):
		
		user_id = card.user_id
		study_item_id = card.study_item_id
		active = card.active
		subject = card.subject
		topic = card.topic
		study_item = card.study_item
		study_item_type = card.study_item_type 
		card_id = card.card_id
		question = card.question
		question_type = card.question_type

		#Update user's highest_card_id
		highest_card_id = self.get_highest_card_id(user_id)
		
		if highest_card_id < card_id:
			self.cursor.execute("UPDATE users SET highest_card_id=%s WHERE user_id=%s", (card_id, user_id))

		self.cursor.execute("INSERT INTO cards VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
			 (user_id, study_item_id, active, subject, topic, study_item, study_item_type,
			  card_id, question, question_type,
	    	  card.attempts, card.ef, card.interval,
			  str(card.next_date.year) + '-' + str(card.next_date.month) + '-' + str(card.next_date.day)))

		self.conn.commit()


	def get_card(self, user_id, card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND card_id=%s", 
							(user_id, card_id))
		card_info = self.cursor.fetchall()
		if len(card_info) == 0:
			self.logger.warning("Card {}, {} doesn't exist".format(user_id, card_id))
			return None
		card_info = card_info[0]
		return Card.from_list(card_info)


	def get_cards_on_topic(self, user_id, subject, topic):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND subject=%s AND topic=%s", (user_id, subject, topic))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			self.logger.warning("Cards on {}, {}, {} doesn't exist".format(user_id, subject, topic))
			return []
		cards = []
		for row in rows:
			cards.append(Card.from_list(card))
		return cards


	def get_all_active_cards(self, user_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s and active=1", (user_id, ))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			self.logger.warning("{} - There's no cards registered or active".format(user_id))
			return []
		cards = []
		for row in rows:
			cards.append(Card.from_list(row))
		return cards
	

	def erase_card(self, user_id, card_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s AND card_id=%s", (user_id, card_id))
		rows = self.cursor.fetchall()
		if len(rows) == 0:
			self.logger.warning("Card {}, {} doesn't exist".format(user_id, card_id))
			return 

		card = Card.from_list(rows[0])
		question_type, question = card.get_question()
		if (question_type == 'image' or question_type == 'audio'):
			try:
				os.remove(question)
				self.logger.info("Erased file {}".format(question))
			except:
				self.logger.error("Error erasing card {}".format(question), exc_info=True)
		self.cursor.execute("DELETE FROM cards WHERE user_id=%s AND card_id=%s", (user_id, card_id))
		self.conn.commit()
		self.logger.info("Card {}, {} successfuly removed".format(user_id, card_id))
		return 


	def set_supermemo_data(self, card):
		if self.check_card_existence(card.get_user(), card):
			self.cursor.execute("UPDATE cards SET attempts=%s, easiness_factor=%s, interval=%s, next_date=%s WHERE user_id=%s AND card_id=%s;",
								(card.attempts, card.ef, card.interval, card.next_date.strftime('%Y-%m-%d'), card.user_id, card.card_id))
			self.conn.commit()

	
	def is_card_active(self, user_id, card_id):
		self.cursor.execute("SELECT active FROM cards WHERE user_id=%s and card_id=%s;", (user_id, card_id))
		card = self.cursor.fetchall()
		return card[0][0]


	def set_card_active(self, user_id, card_id, active):
		self.cursor.execute("UPDATE cards SET active=%s WHERE user_id=%s and card_id=%s", (active, user_id, card_id))
		

	def check_card_existence(self, user_id, card_id):
		self.cursor.execute("SELECT card_id FROM cards WHERE user_id=%s AND card_id=%s;", 
																		(user_id, card_id))
		card = self.cursor.fetchall()
		if len(card) == 0:
			return False
		return True


