import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card
from database_ops.db_utils import treat_str_SQL


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
		return "Card {}, {} doesn't exist".format(user_id, user_card_id)

	row = row[0]
	card = Card(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

	self.cursor.execute("SELECT content_path FROM archives WHERE user_id={} AND user_card_id={};".format(user_id, user_card_id))
	rows = self.cursor.fetchall()
	for row in rows:
		card.add_archive(row[0])
	return card

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
		self.erase_archive(user_id,user_card_id,row[0])

	self.cursor.execute("DELETE FROM cards WHERE user_id={} AND user_card_id={}"
					.format(user_id, user_card_id))
	self.conn.commit()
	return "Card successfuly removed"


def set_supermemo_data(self, card):
	"""Updates on the database the information about the supermemo algorithm that are contained in a word.

	Args:
	word: A Word instance.
	"""
	self.cursor.execute("UPDATE cards SET attempts={}, easiness_factor={}, interval={}, next_date='{}' WHERE user_id={} AND user_card_id={};"
	.format(card.attempts, card.ef, card.interval, card.next_date.strftime('%Y-%m-%d'), card.get_user(), card.card_id))
	self.conn.commit()


def set_card_waiting(self, user_id, card_id):
	self.cursor.execute("UPDATE users SET card_waiting={} WHERE id={};".format(card_id, user_id))
	self.conn.commit()


def get_card_waiting(self, user_id):
	self.cursor.execute("SELECT card_waiting FROM users WHERE id={};".format(user_id))
	card = self.cursor.fetchall()
	card = card[0][0]
	return card



