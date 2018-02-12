import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card
from database_ops.db_utils import treat_str_SQL


def add_topic(self, user_id, language, topic):
	self.cursor.execute("SELECT topic FROM topics WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
	row = self.cursor.fetchall()

	if(len(row) > 0):
		return

	self.cursor.execute("INSERT INTO topics VALUES ({}, '{}', '{}')".format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
	self.conn.commit()



def get_all_topics(self, user_id, language):
	self.cursor.execute("SELECT topic FROM topics WHERE user_id={} AND language='{}';".format(user_id, treat_str_SQL(language)))
	topics = self.cursor.fetchall()

	ret = []
	for topic in topics:
		ret.append(topic[0])

	return ret;


def get_words_on_topic(self, user_id, language, topic):
	self.cursor.execute("SELECT user_id,user_word_id FROM words WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id, treat_str_SQL(language), treat_str_SQL(topic)))
	words = self.cursor.fetchall()

	ret = []
	for word in words:
		ret.append(self.get_word(word[0],word[1]))

	return ret

	

def erase_topic_empty_words(self, user_id, language, topic):
	self.cursor.execute("SELECT topic FROM topics WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id,treat_str_SQL(language),treat_str_SQL(topic)))
	rows = self.cursor.fetchall()

	if len(rows) == 0:
		print("Topic {},{},{} doesn't exist.".format(user_id,language,topic))
		return

	self.cursor.execute("DELETE FROM topics WHERE user_id={} AND language='{}' AND topic='{}';".format(user_id, treat_str_SQL(language),treat_str_SQL(topic)))
	self.conn.commit()
	print("Topic {},{},{} erased.".format(user_id, language, topic))
	return