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
		return self.next_date

	def get_data(self):
		return self.attempts,self.ef,self.interval,self.next_date


class WordInfo(object):
	
	def __init__ (self, user_id, word_id, language, topic, foreign_word):
		self.user_id = user_id
		self.word_id = word_id
		self.language = language
		self.topic = topic
		self.foreign_word = foreign_word

	def get_word_id(self):
		return self.word_id

	def get_user(self):
		return self.user_id

	def get_word(self):
		return self.foreign_word
	
	def get_language(self):
		return self.language


class Card(TimeControl, Word):
	
	"""
	Class that represents a flashcard. 
	In LingoBot each card is an word or phrase to learn (for now).

	Atribbutes:
		user_id: User ID
		card_id: Card ID (on database)
		content_type: Type of the message that will be sent to refer the card
	"""
	
	def __init__(self,
			user_id, word_id, language, foreign_word,
			card_id, content_type, archives = [], 
			attempts = 1, ef = 2.5, interval = 1,
			next_date = datetime.datetime.now() + datetime.timedelta(days=1)):
		self.card_id = card_id
		self.content_type = content_type
		self.archives = archives
		WordInfo.__init__(self, user_id, word_id, language, foreign_word)
		TimeControl.__init__(self,attempts,ef,interval,next_date)
	
	def get_content(self):
		return self.content_type

	def get_archives(self):
		return archives

	def get_question(self):
		"""
			Returns path to the image or audio if the question
			is that. Returns english translation if the question
			is the english translation
		"""
		rand = randint(0,len(self.path)-1)
		return self.path[rand]

	def get_card_id(self):
		return self.card_id


class Word(WordInfo):
	
	"""
	Class that represents a flashcard. 
	In LingoBot each card is an word or phrase to learn (for now).

	Atribbutes:
		user_id: User ID
		language: Language of the word or phrase
		foreign_word: ...
		word_id: Card ID (on database)
		cards: ...
	"""

	def __init__(self, 
			user_id = None, word_id = None,  language = None, foreign_word = None, 
			cards = {'images': None,
					 'audio': None,
					 'translation': None}):
		WordInfo.__init__(user_id, word_id, language, foreign_word)
		self.cards = cards
	
	def set_card(self, card):
		card.word_id = self.word_id
		card.user_id = self.user_id
		cards[card.get_content()] = card

	def del_card_type(self, card_type):
		pass	

	
	


def main():
	x = Card(12,"meme", "wololo", "wolo", 1)
	print(x.get_next_date())

if __name__ == '__main__':
	main()

