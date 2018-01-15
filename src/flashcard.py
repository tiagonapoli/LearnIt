import time
import datetime
from random import randint

class TimeControl(object):

	"""Class that controls card query intervals.

	Uses SuperMemo2 algorithm, credited to Piotr Wozniak, to control intervals

	Atribbutes:
		attempts: Number of card attempts already scheduled and made
		ef: easinesss factor (1.3 <= ef <= 2.5). 1.3 is harder, 2.5 is easier.
		interval: interval between last attempt a next attempt
		next_date: date of the next attempt
	"""

	def __init__(self,_attempts=1, _ef=2.5,_interval=1,
			     _next_date = 
				 datetime.datetime.now() + datetime.timedelta(days=1)):
		self.attempts = _attempts
		self.ef = _ef
		self.interval = _interval
		self.next_date = _next_date

	def go_next_state(self,q):
		self.attempts += 1
		if self.attempts == 1:
			self.interval = 1
		elif self.attempts == 2:
			self.interval = 3
		else:
			self.interval = self.interval * self.ef
		self.ef = self.ef-0.8+0.28*q-0.02*q*q
		if self.ef > 2.5:
			self.ef = 2.5
		if self.ef < 1.3:
			self.ef = 1.3

	def calc_next_date(self, quality_answer):
		"""	Calculates next date.
			Args:
				quality_answer: Grade user gave to his answer
		"""
		self.go_next_state(quality_answer)
		end_date = self.next_date + datetime.timedelta(days=int(self.interval))
		self.next_date = end_date
	
	def get_next_date(self):
		return next_date

	def get_data(self):
		return self.attempts,self.ef,self.interval,self.next_date

class Card(TimeControl):
	
	"""Class that represents a flashcard. 
	In LingoBot each card is an word or phrase to learn (for now).

	Atribbutes:
		user_id: User ID
		language: Language of the word or phrase
		foreign_word: ...
		english_word: Translation of the word
		card_id: Card ID (on database)
		query_content_type: Type of the message that will be sent to refer the card
		path: List of paths to archives data will be used by the card
	"""
	
	def __init__(self, user_id, language, foreign_word, english_word, 
			card_id, query_content_type, path = [],
			attempts = 1, ef = 2.5, interval = 1,
			next_date = datetime.datetime.now() + datetime.timedelta(days=1)):
		self.user_id = user_id
		self.language = language
		self.foreign_word = foreign_word
		self.english_word = english_word
		self.word_id = word_id
		self.query_content_type = query_content_type
		self.path = path
		TimeControl.__init__(self,attempts,ef,interval,next_date)
	
	def get_question_content(self):
		return self.query_content_type

	def get_paths(self):
		return path

	def get_question(self):
		"""
			Returns path to the image or audio if the question
			is that. Returns english translation if the question
			is the english translation
		"""
		if query_content_type == 'Translation':
			return english_word
		elif query_content_type == 'Image' or query_content_type == 'Audio':
			rand = randint(0,len(path)-1)
			return path[rand]

	def get_user(self):
		return user_id
	
	def get_card_id(self):
		return card_id

	def get_ans(self):
		return foreign_word
	
def main():
	return 0

if __name__ == '__main__':
	main()

