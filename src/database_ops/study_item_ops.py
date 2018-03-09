import os
import logging
import database_ops.card_ops
from Flashcard import StudyItemDeck, Card


class StudyItemOps():


	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor
		self.card_ops = database_ops.card_ops.CardOps(conn,cursor, debug_mode)


	def get_highest_study_item_id(self, user_id):
		self.cursor.execute("SELECT highest_study_item_id FROM users WHERE user_id=%s", (user_id, ))
		row = self.cursor.fetchall()
		if len(row) == 0:
			self.logger.warning("User {} doesn't exist".format(user_id))
			return
		return row[0][0]


	def add_study_item_deck(self, deck):
		
		user_id = deck.user_id
		study_item_id = deck.study_item_id
		active = deck.active
		subject = deck.subject
		topic = deck.topic
		study_item = deck.study_item
		study_item_type = deck.study_item_type 

		highest_study_item_id = self.get_highest_study_item_id(user_id)
		
		if highest_study_item_id < study_item_id:
			self.cursor.execute("UPDATE users SET highest_study_item_id=%s WHERE user_id=%s", (study_item_id, user_id))

		#maybe add subjects
		self.cursor.execute("SELECT subject FROM subjects WHERE user_id=%s AND subject=%s;", (user_id, subject))
		rows = self.cursor.fetchall()
		if len(rows) == 0:		
			self.cursor.execute("INSERT INTO subjects VALUES (%s, %s, %s);", (user_id, 0, subject))
			self.conn.commit()

		#maybe add topic
		self.cursor.execute("SELECT topic FROM topics WHERE user_id=%s AND subject=%s AND topic=%s;", (user_id, subject, topic))
		rows = self.cursor.fetchall()
		if len(rows) == 0:		
			self.cursor.execute("INSERT INTO topics VALUES (%s, %s, %s, %s);", (user_id, 0, subject, topic))
			self.conn.commit()

		self.cursor.execute("INSERT INTO study_items VALUES (%s, %s, %s, %s, %s, %s, %s)",
			 (user_id, study_item_id, active, subject, topic, study_item, study_item_type))
		self.conn.commit()

		for card_type, card in deck.cards.items():
			self.card_ops.add_card(card)

		self.sum_delta_active_to_upper_tables(user_id, study_item_id, active)


	def erase_study_item(self, user_id, study_item_id):
		self.cursor.execute("SELECT subject,topic,study_item,study_item_type,active FROM study_items WHERE user_id=%s AND study_item_id=%s;", (user_id, study_item_id))
		rows = self.cursor.fetchall()

		if len(rows) == 0:
			self.logger.warning("Invalid study_item {} {}".format(study_item_id, user_id))
			return 

		subject = rows[0][0]
		topic = rows[0][1]
		study_item = rows[0][2]
		study_item_type = rows[0][3]
		active = rows[0][4]
		self.sum_delta_active_to_upper_tables(user_id, study_item_id, -active)

		self.cursor.execute("SELECT card_id FROM cards WHERE user_id=%s AND study_item_id=%s;", (user_id, study_item_id))
		rows = self.cursor.fetchall()

		
		#erasing cards
		for card in rows:
			self.card_ops.erase_card(user_id, card[0])

		# erasing study_item from the database
		self.cursor.execute("DELETE FROM study_items WHERE user_id=%s AND study_item_id=%s;", (user_id, study_item_id))
		self.conn.commit()

		if study_item_type == 1:
			try:
				os.remove(study_item)
			except:
				self.logger.error("Error erasing study_item file {} {}".format(study_item, user_id), exc_info=True)



		#maybe erase topic
		self.cursor.execute("SELECT topic FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s;", (user_id, subject, topic))
		rows = self.cursor.fetchall()
		if len(rows) == 0:		
			self.cursor.execute("DELETE FROM topics WHERE user_id=%s AND subject=%s AND topic=%s;", (user_id, subject, topic))
			self.conn.commit()

		#maybe erase subjects
		self.cursor.execute("SELECT subject FROM study_items WHERE user_id=%s AND subject=%s;", (user_id, subject))
		rows = self.cursor.fetchall()
		if len(rows) == 0:		
			self.cursor.execute("DELETE FROM subjects WHERE user_id=%s AND subject=%s;", (user_id, subject))
			self.conn.commit()



		if self.debug_mode:
			if os.path.exists('../data_debug/{}/{}'.format(user_id, study_item_id)):
				try:
					os.rmdir('../data_debug/{}/{}'.format(user_id, study_item_id))
					self.logger.info("Erased directory {}".format('../data_debug/{}/{}'.format(user_id, study_item_id)))
				except Exception as e:
					self.logger.error("ERROR in erase_study_item - directory {}".format('../data_debug/{}/{}'.format(user_id, study_item_id)), exc_info=True)
		else:
			if os.path.exists('../data/{}/{}'.format(user_id, study_item_id)):
				try:
					os.rmdir('../data/{}/{}'.format(user_id, study_item_id))
					self.logger.info("Erased directory {}".format('../data/{}/{}'.format(user_id, study_item_id)))
				except Exception as e:
					self.logger.error("ERROR in erase_study_item - directory {}".format('../data/{}/{}'.format(user_id, study_item_id)), exc_info=True)

		self.logger.info("Study_item {} erased successfully!".format(study_item))
		return 


	def get_study_item_deck(self, user_id, study_item_id):
		self.cursor.execute("SELECT * FROM cards WHERE user_id=%s and study_item_id=%s;", (user_id, study_item_id))
		cards_info = self.cursor.fetchall()
		cards = []
		for card_info in cards_info:
			cards.append(Card.from_list(card_info))
		return StudyItemDeck.from_cards(cards)


	def get_study_items_on_topic(self, user_id, subject, topic):
		self.cursor.execute("SELECT user_id, study_item_id FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s;", (user_id, subject, topic))
		study_items = self.cursor.fetchall()
		ret = []
		for item in study_items:
			ret.append(self.get_study_item_deck(item[0], item[1]))
		return ret


	def get_active_study_items(self, user_id, subject, topic):
		self.cursor.execute("SELECT user_id, study_item_id FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s AND active=1;", (user_id, subject, topic))
		study_items = self.cursor.fetchall()
		ret = []
		for item in study_items:
			ret.append(self.get_study_item_deck(item[0], item[1]))
		return ret


	def is_study_item_active(self, user_id, study_item_id):
		self.cursor.execute("SELECT active FROM study_items WHERE user_id=%s and study_item_id=%s;", (user_id, study_item_id))
		study_item = self.cursor.fetchall()
		return study_item[0][0]


	def sum_delta_active_to_upper_tables(self, user_id, study_item_id, delta):
		self.cursor.execute("SELECT subject,topic FROM study_items WHERE user_id=%s AND study_item_id=%s", (user_id, study_item_id))
		info = self.cursor.fetchall()
		subject = info[0][0]
		topic = info[0][1]
		if delta != 0:
			self.cursor.execute("SELECT active FROM topics WHERE user_id=%s AND subject=%s AND topic=%s", (user_id, subject, topic))
			topic_active = self.cursor.fetchall()
			self.cursor.execute("UPDATE topics SET active=%s WHERE user_id=%s AND subject=%s AND topic=%s", (topic_active[0][0] + delta, user_id, subject, topic))
			
			self.cursor.execute("SELECT active FROM subjects WHERE user_id=%s AND subject=%s ", (user_id, subject))
			subject_active = self.cursor.fetchall()
			self.cursor.execute("UPDATE subjects SET active=%s WHERE user_id=%s AND subject=%s", (subject_active[0][0] + delta, user_id, subject))



	def set_study_item_active(self, user_id, study_item_id, active):
		if active > 1:
			active = 1

		self.cursor.execute("SELECT active FROM study_items WHERE user_id=%s AND study_item_id=%s", (user_id, study_item_id))
		last_active = self.cursor.fetchall()
		delta = active - last_active[0][0]
		self.sum_delta_active_to_upper_tables(user_id, study_item_id, delta)
		self.cursor.execute("UPDATE study_items SET active=%s WHERE user_id=%s and study_item_id=%s", (active, user_id, study_item_id))
		self.cursor.execute("SELECT card_id FROM cards WHERE user_id=%s and study_item_id=%s;", (user_id, study_item_id))
		cards = self.cursor.fetchall()
		for card in cards:
			self.card_ops.set_card_active(user_id, card[0], active)
			


	def check_study_item_existence(self, user_id, subject, topic, study_item):
		self.cursor.execute("SELECT study_item_id FROM study_items WHERE user_id=%s AND subject=%s AND topic=%s AND study_item=%s;", (user_id, subject, topic, study_item))
		study_item_id = self.cursor.fetchall()
		if len(study_item_id) == 0:
			return False, -1
		else:
			return True, study_item_id[0][0]
