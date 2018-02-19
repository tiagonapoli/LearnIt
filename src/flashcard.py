import time
import datetime
import os
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

	def __init__(self,_attempts=1, _ef=1.3,_interval=1,
			     _next_date = None):
		self.attempts = _attempts
		self.ef = _ef
		self.interval = _interval
		self.next_date = _next_date

	def go_next_state(self,q):
		self.attempts += 1
		if self.attempts == 1:
			self.interval = 1
		elif self.attempts == 2:
			self.interval = 2
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

	def get_topic(self):
		return self.topic




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

	def __init__(self, user_id = None, word_id = None,  language = None, topic = None, foreign_word = None):
		self.cards = {}
		WordInfo.__init__(self, user_id, word_id, language, topic, foreign_word)
	
	def set_card(self, card):
		self.cards[card.get_type()] = card

	def del_card_type(self, card_type):
		if self.cards.has_key(card_type):
			del self.cards[card_type]

	def get_cards(self):
		ret = []
		for content_type, card in self.cards.items():
			ret.append(card)
		return ret

	def __str__(self):
		str = "           --Word--\nUser ID: {}\nWord ID: {}\nLanguage: {}\nTopic: {}\nWord: {}\n".format(self.user_id, self.word_id, self.language, 
												 self.topic, self.foreign_word)
		for content_type, card in self.cards.items():
			str += card.__str__()
		return str



class Card(TimeControl, WordInfo):
	
	"""
	Class that represents a flashcard. 
	In LingoBot each card is an word or phrase to learn (for now).

	Atribbutes:
		user_id: User ID
		card_id: Card ID (on database)
		content_type: Type of the message that will be sent to refer the card
	"""
	
	def __init__(self,
				user_id, word_id, language, topic, foreign_word,
				card_id, content_type, 
				attempts = 1, ef = 1.3, interval = 1,
				next_date = None):
		self.card_id = card_id
		self.content_type = content_type
		self.archives = []
		if next_date == None:
			next_date = datetime.datetime.now() #+ datetime.timedelta(days=1)
		WordInfo.__init__(self, user_id, word_id, language, topic, foreign_word)
		TimeControl.__init__(self,attempts,ef,interval,next_date)
	
	def __str__(self):
		text = "           --Card--\n" + "Word ID: {}\nCard ID: {}\nWord: {}\nContent Type: {}\nE.F: {}\nNext Date: {}\nArchives:\n".format(
										self.word_id, self.card_id, self.foreign_word, self.content_type, self.ef, str(self.get_next_date()))
		for archive in self.archives:
			text += archive + "\n"
		text += "\n"
		return text

	def __lt__(self,other):
		return self.next_date < other.next_date

	def get_type(self):
		return self.content_type

	def get_archives(self):
		return self.archives

	def add_archive(self, archive):
		self.archives.append(archive)

	def erase_all_archives_local(self):
		if self.content_type != 'translation' and self.content_type != 'default':
			for archive in self.archives:
				try:
					os.remove(archive)
					print("Erased {}.".format(archive))
				except Exception as e:
					print(e)
		self.archives = []

	def get_question(self):
		"""
			Returns path to the image or audio if the question
			is that. Returns english translation if the question
			is the english translation
		"""
		rand = randint(0,len(self.archives)-1)
		return self.archives[rand]

	def get_card_id(self):
		return self.card_id

	def is_learning(self):
		return self.ef <= 1.5



if __name__ == '__main__':
	
	cards_sort = []

	word = Word(42,1,"Portuges", "Miscelania", "Camargao")
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", 1, 'image') 
	card.add_archive('../data/ibagem.jpg')
	card.add_archive('./data/image.png')
	word.set_card(card)
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", 1, 'image') 
	card.add_archive('AAAAAAAAAAAAAAAAAAAAAAAAAAAA')
	cards_sort.append(card)
	word.set_card(card)
	time.sleep(2)
	card = Card(42,1,"Portuges", "Miscelania", "Camargao", 1, 'audio') 
	card.add_archive('BBBBBBBBBBBBBBBBB')
	cards_sort.append(card)
	word.set_card(card)
	print(word)
	time.sleep(2)

	word = Word(42,2,"ingels", "wololo", "tiagao")
	card = Card(42,2,"ingels", "wololo", "tiago", 1, 'image') 
	card.add_archive('CCCCCCCCCCCCCCCCCC')
	cards_sort.append(card)
	word.set_card(card)
	print(word)

	cards_sort.sort()

	print("\n\n\n")
	print("SORT TEST")
	for card in cards_sort:
		print(card)

