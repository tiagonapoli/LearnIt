import time
import datetime

class TimeControl(object):

	"""Class that controls card query intervals.

	Uses SuperMemo2 algorithm, credited to Piotr Wozniak, to control intervals

	Atribbutes:
		attempts: Number of card attempts already scheduled and made
		ef: easinesss factor (1.3 <= ef <= 2.5). 1.3 is harder, 2.5 is easier.
		interval: interval between last attempt a next attempt
		next_date: date of the next attempt
	"""

	def __init__(self,_attempts=1, _ef=1.5,_interval=1,
			     _next_date = None):
		self.attempts = _attempts
		self.ef = _ef
		self.interval = _interval
		self.next_date = _next_date

	def go_next_state(self,q):
		self.attempts += 1
		if self.attempts == 2:
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
		end_date = datetime.datetime.now() + datetime.timedelta(days=int(self.interval))
		self.next_date = end_date
	
	def get_next_date(self):
		return self.next_date

	def get_data(self):
		return self.attempts,self.ef,self.interval,self.next_date


class StudyItemInfo(object):
	
	def __init__ (self, user_id, study_item_id, active, subject, topic, study_item, study_item_type):
		self.user_id = user_id
		self.study_item_id = study_item_id
		self.active = active
		self.subject = subject
		self.topic = topic
		self.study_item = study_item
		self.study_item_type = study_item_type

	@classmethod
	def from_list(cls, lst):
		return cls(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], lst[6])

	def get_active(self):
		return self.active == 1

	def set_active(self, val):
		if val == True:
			self.active = 1
		else:
			self.active = 0

	def get_user(self):
		return self.user_id

	def set_user(self, user_id):
		self.user_id = user_id

	def get_study_item_id(self):
		return self.study_item_id

	def set_study_item_id(self, val):
		self.study_item_id = val

	def get_subject(self):
		return self.subject

	def set_subject(self, subject):
		self.subject = subject

	def get_topic(self):
		return self.topic

	def set_topic(self, topic):
		self.topic = topic

	def get_study_item(self):
		return self.study_item_type, self.study_item

	def set_study_item(self, item, item_type):
		self.study_item = item	
		self.study_item_type = item_type

	def __str__(self):
		text = ("User: {}\nStudyItemID: {}\nActive: {}\nSubject: {}\nTopic: {}\nStudyItem: {}\nStudyItemType: {}\n".format(
				self.user_id, self.study_item_id, self.active, self.subject, self.topic, self.study_item, self.study_item_type))
		return text


class StudyItemDeck(StudyItemInfo):

	def __init__(self, user_id, study_item_id, active, subject=None, topic=None, study_item=None, study_item_type=None):
		self.cards = {}
		StudyItemInfo.__init__(self, user_id, study_item_id, active, subject, topic, study_item, study_item_type)
	
	@classmethod
	def from_cards(cls, cards):
		ret = cls(cards[0].user_id, cards[0].study_item_id, cards[0].active, cards[0].subject,
				  cards[0].topic, cards[0].study_item, cards[0].study_item_type)
		for card in cards:
			ret.set_card(card)
		return ret

	def set_card(self, card):
		self.cards[card.get_question_type()] = card

	def del_card_type(self, card_type):
		if self.cards.has_key(card_type):
			del self.cards[card_type]

	def get_sendable_study_item(self):
		return self.study_item

	def get_cards(self):
		ret = []
		for content_type, card in self.cards.items():
			ret.append(card)
		return ret

	def __str__(self):
		text = ("------------------------StudyItemDeck------------------------\n" +
			    StudyItemInfo.__str__(self))
		for content_type, card in self.cards.items():
			text += card.__str__()
		return text



class Card(TimeControl, StudyItemInfo):
	
	def __init__(self,
				user_id, study_item_id, active, 
				subject, topic, study_item, study_item_type,
				card_id, 
				question=None, question_type=None, 
				attempts = 1, ef = 1.5, interval = 1,
				next_date = None):
		self.card_id = card_id
		self.question = question
		self.question_type = question_type
		if next_date == None:
			next_date = datetime.datetime.now()
		StudyItemInfo.__init__(self, user_id, study_item_id, active, subject, topic, study_item, study_item_type)
		TimeControl.__init__(self,attempts,ef,interval,next_date)
	

	@classmethod
	def from_study_info(cls, study_info, card_id, question, question_type):
		return cls(study_info.user_id, study_info.study_item_id, study_info.active,
				   study_info.subject, study_info.topic, study_info.study_item,
				   study_info.study_item_type, 
				   card_id, question, question_type)

	@classmethod
	def from_list(cls, lst):
		return cls(lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], lst[6], lst[7], lst[8], lst[9], lst[10], lst[11], lst[12], lst[13])

	def __str__(self):
		text = ("-----------Card-----------\n" +
			    StudyItemInfo.__str__(self) +
			    "CardID: {}\nQuestionType: {}\nQuestion: {}\nE.F: {}\nNext Date: {}\n".format(
				self.card_id, self.question_type, self.question, self.ef, str(self.get_next_date())))
		return text

	def __lt__(self,other):
		return self.next_date > other.next_date

	def set_question(self, question, question_type):
		self.question = question
		self.question_type = question_type

	def get_question(self):
		return self.question_type, self.question

	def get_question_type(self):
		return self.question_type

	def get_card_id(self):
		return self.card_id

	def is_learning(self):
		return self.ef <= 1.5




if __name__ == '__main__':
	
	cards_sort = []

	deck = StudyItemDeck(42, 1, 1, 'Portugues', 'Comida', 'Carne', 0)
	card = Card(42, 1, 1, 'Portugues', 'Comida', 'Carne', 0, 1, 'Meat', 'text') 
	deck.set_card(card)
	card = Card(42, 1, 1, 'Portugues', 'Comida', 'Carne que Fica', 0, 1, 'Meat', 'text') 
	deck.set_card(card)

	cards_sort.append(card)
	
	time.sleep(2)
	card = Card(42, 1, 1, 'Portugues', 'Comida', 'Carne que Fica', 0, 2, 'carne.jpg', 'image') 
	
	cards_sort.append(card)
	
	deck.set_card(card)
	print(deck)
	print("\n\n\n")
	time.sleep(2)

	card = Card(42, 1, 1, 'Portugues', 'Comida', 'Carne que Fica', 0, 3, 'carne.mp3', 'audio') 
	
	cards_sort.append(card)
	
	deck.set_card(card)
	
	print(deck)

	cards_sort.sort()

	print("\n\n\n")
	print("SORT TEST")
	for card in cards_sort:
		print(card)

