import time
import datetime

class FlashCardSM:
	attempts = None
	ef = None
	interval = None
	next_date = None

	def __init__(self,_attempts=1, _ef=2.5,_interval=1, _next_date = datetime.datetime.now() + datetime.timedelta(days=1)):
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

	def get_next_date(self, quality_answer):
		
		self.go_next_state(quality_answer)
		end_date = self.next_date + datetime.timedelta(days=int(self.interval))

		self.next_date = end_date
		return end_date
	
	def get_date(self):
		return next_date

	def get_data(self):
		return self.attempts,self.ef,self.interval,self.next_date



class Word(FlashCardSM):
	
	userID = None
	language = None
	foreign_word = None
	english_word = None
	wordID = None
	
	def __init__(self,_userId,_language,_foreign_word,_english_word,_wordID,_attempts=1, _ef=2.5,_interval=1, _next_date = datetime.datetime.now() + datetime.timedelta(days=1)):
		self.userID = _userID
		self.language = _language
		self.foreign_word = _foreign_word
		self.english_word = _english_word
		self.wordID = _wordID
		FlashCardSM.__init__(_attempts,_ef,_interval,_next_date)
	
	

