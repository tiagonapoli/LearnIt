import sys
import datetime
import telebot
import fsm
from collections import deque
from flashcard import Card
from random import shuffle, randint
from utilities import utils, logging_utils
import logging

LEARNING = 1
REVIEW = 2

def sending_queue_to_str(dequeue):
	text = "["
	cnt = 0
	for x in dequeue:
		if cnt == 0:
			text += "("
		else:
			text += ", ("
		text += "{}, {}, {}".format(x[0], x[1], x[2].get_card_id())
		text += ")"
		cnt += 1
	text += "]"
	return text

def stack_to_str(stack):
	text = "["
	cnt = 0
	for x in stack:
		if cnt != 0:
			text += ", "
		text += "{}".format(x.get_card_id())
		cnt += 1
	text += "]"
	return text

class UserCardQueue():

	def __init__(self, user, bot, debug_mode):
		self.user = user
		self.user_id = self.user.get_id()
		self.logger = logging.getLogger(__name__ + str(self.user_id))
		logging_utils.setup_logger_UserCardQueue(self.logger, self.user_id, debug_mode)
		logging_utils.add_bot_handler(self.logger, bot)

		
		self.logger.info("Starting UserCardQueue")
		self.NUMBER_OF_LAST_CARDS = 2

		self.logger.debug("Set card waiting 0")
		self.user.set_card_waiting(0)
		self.sending_queue= deque()
		
		
		self.now_review_stack = []
		
		self.now_learn_stack = []
		self.next_learn_stack = []
		self.grades_for_day = {}
		self.learn_cards_day_set = set()

		self.learn_cnt_day = 0
		self.learn_cnt_hourly = 0
		self.learn_total_hourly = 0

		self.review_cnt_day = 0
		self.review_cnt_hourly = 0
		self.review_total_hourly = 0

		self.user.set_card_waiting(0)
		self.sending_queue= deque()

		self.initialized_for_day = False

		self.cards_expired = []
		self.init_day()
		self.logger.info("End init UserCardQueue")

	def init_day(self):
		self.logger.info("Init Day")

		self.upd_cards_expired()
		self.add_learning_cards()
		self.add_review_cards()	

		self.logger.debug("Set card waiting 0")
		
		self.learn_cnt_day = 0
		self.learn_cnt_hourly = 0
		self.learn_total_hourly = 0

		self.review_cnt_day = 0
		self.review_cnt_hourly = 0
		self.review_total_hourly = 0

		self.hourly_init()
		self.logger.info("Initialized for day")
		self.initialized_for_day = True
		self.logger.info("End init Day")

	

	def add_learning_cards(self):

		distinct_words = self.user.get_learning_words_limit()
		words_set = set()

		for card in self.now_learn_stack:
			words_set.add(card.get_word_id())

		for card in self.next_learn_stack:
			words_set.add(card.get_word_id())

		if len(words_set) >= distinct_words:
			return

		self.logger.info('Try add Learning Cards')

		cards = self.cards_expired
		added = 0
		new_cards = []
		for card in cards:
			if card.is_learning() and (not card.get_card_id() in self.learn_cards_day_set):
				if len(words_set) < distinct_words:
					added += 1
					new_cards.append(card.get_card_id())
					self.next_learn_stack.append(card)
					words_set.add(card.get_word_id())
					self.learn_cards_day_set.add(card.get_card_id())
					self.grades_for_day[card.get_card_id()] = []
				elif len(words_set) == distinct_words and (card.get_word_id() in words_set):
					added += 1
					new_cards.append(card.get_card_id())
					self.next_learn_stack.append(card)
					self.learn_cards_day_set.add(card.get_card_id())
					self.grades_for_day[card.get_card_id()] = []

		if added > 0:
			self.logger.debug('Added {} learning cards: '.format(added) + str(new_cards))
			shuffle(self.next_learn_stack)

		self.logger.info('End add Learning Cards')


	def remove_learning_card(self, card):
		card_id = card.get_card_id()
		self.logger.info('Remove learning card {}'.format(card_id))
		self.grades_for_day.pop(card_id, None)
		i = 0
		while i < len(self.now_learn_stack):
			if card_id == self.now_learn_stack[i].get_card_id():
				 self.now_learn_stack.pop(i)
			else:
				i += 1

		i = 0
		while i < len(self.next_learn_stack):
			if card_id == self.next_learn_stack[i].get_card_id():
				 self.next_learn_stack.pop(i)
			else:
				i += 1

		self.logger.debug("now:" + stack_to_str(self.now_learn_stack) + 
			"\n 						next: " + stack_to_str(self.next_learn_stack)) 
		self.logger.info('End remove learning card {}'.format(card_id))


	def upd_cards_expired(self):
		self.logger.info("Upd cards expired")
		now = datetime.datetime.now()
		self.cards_expired = self.user.get_cards_expired(now)
		self.logger.info("End upd cards expired")

	

	def add_review_cards(self):
		self.logger.info("Add review cards")
		cards = self.cards_expired
		review_limit = self.user.get_review_cards_limit()
		added = 0
		for card in cards:
			if (not card.is_learning()) and len(self.now_review_stack) < review_limit:
				added += 1
				self.now_review_stack.append(card)
		self.logger.debug('Added {} review cards'.format(added))
		self.logger.info("End add review cards")



	def hourly_init(self):
		self.logger.info("Hourly init")
		now = datetime.datetime.now()
		hour = now.hour

		self.learn_cnt_hourly = 0
		self.review_cnt_hourly = 0
		
		qtd = self.user.get_cards_per_hour()
		if qtd == 1:
			if hour % 2 == 0:
				self.learn_total_hourly = 1
			else:
				self.learn_total_hourly = 0
			remaining = qtd - self.learn_total_hourly
			self.review_total_hourly = remaining
		else:
			self.learn_total_hourly = int(0.5 * qtd)
			remaining = qtd - self.learn_total_hourly
			self.review_total_hourly = remaining

		self.logger.debug("Learning cards for hour = {} / Review cards for hour = {}".format(self.learn_total_hourly, self.review_total_hourly))
		self.logger.info("End hourly init")


 
	def get_remaining_learn_cards(self):
		return len(self.now_learn_stack) + len(self.next_learn_stack)


	def prepare_queue(self):
		self.logger.info("Prepare queue")
		now = datetime.datetime.now()
		hour = now.hour
		minute = now.minute

		total = self.learn_total_hourly + self.review_total_hourly
		total_sent = self.learn_cnt_hourly + self.review_cnt_hourly
		send_time_ini = int(60 * total_sent/total)

		self.logger.info("Hourly process: {}/{}".format(total_sent, total))
		self.logger.debug("Remaining cards: L={}  R={}".format(self.get_remaining_learn_cards(), len(self.now_review_stack)))
		self.logger.debug("Queue: " + sending_queue_to_str(self.sending_queue))
		self.logger.debug("learn now:" + stack_to_str(self.now_learn_stack)) 
		self.logger.debug("learn next:" + stack_to_str(self.next_learn_stack)) 
		self.logger.debug("review now:" + stack_to_str(self.now_review_stack)) 
		self.logger.debug("min: {}  send_time_ini: {}".format(minute, send_time_ini))

		if (self.user.working_hours(hour) == False):
			return

		if (send_time_ini <= minute and 
			len(self.sending_queue) < 2):
			
			if (self.review_cnt_hourly < self.review_total_hourly and
				  len(self.now_review_stack) == 0 and
				  self.get_remaining_learn_cards() > 0):
				self.learn_total_hourly += 1
				self.review_total_hourly -= 1
			elif self.get_remaining_learn_cards() == 0 and self.learn_cnt_hourly < self.learn_total_hourly:
				self.learn_total_hourly -= 1
				self.review_total_hourly += 1

			if (self.learn_cnt_hourly < self.learn_total_hourly and
				self.get_remaining_learn_cards() > 0):

				if len(self.now_learn_stack) == 0:
					shuffle(self.next_learn_stack)
					while len(self.next_learn_stack) > 0:
						self.now_learn_stack.append(self.next_learn_stack.pop())

				
				aux_card = self.now_learn_stack.pop()
				while (len(self.now_learn_stack) > 0 and
						self.user.check_card_existence(aux_card) == False):
					aux_card = self.now_learn_stack.pop()
				
				if self.user.check_card_existence(aux_card):
					self.sending_queue.append((self.learn_cnt_day + 1, LEARNING, aux_card))
					self.next_learn_stack.append(aux_card)
					self.learn_cnt_hourly += 1
					self.learn_cnt_day += 1

			elif (self.review_cnt_hourly < self.review_total_hourly and
				  len(self.now_review_stack) > 0):
				
				aux_card = self.now_review_stack.pop()
				while (len(self.now_review_stack) > 0 and
						self.user.check_card_existence(aux_card) == False):
					aux_card = self.now_review_stack.pop()
				
				if self.user.check_card_existence(aux_card):
					self.sending_queue.append((self.review_cnt_day + 1, REVIEW, aux_card))
					self.review_cnt_hourly += 1
					self.review_cnt_day += 1
		self.logger.info("End prepare queue")


	def send_card(self, bot, card, card_type, number):
		self.user.set_card_waiting_type(card_type)
		if card_type == LEARNING:
			self.logger.info("Sending Learning Card {}".format(card.get_card_id()))
			success = utils.send_review_card(bot, card, self.user, 'Learning', number, logger=self.logger)
		elif card_type == REVIEW:
			self.logger.info("Sending Review Card {}".format(card.get_card_id()))
			success = utils.send_review_card(bot, card, self.user, 'Review', number, logger=self.logger)

		if success == False:
			return False

		self.user.set_state(fsm.next_state[fsm.IDLE]['card_query'])
		return True


	def check_card_finished(self, card, card_type):
		if card_type == REVIEW:
			return False
		if card.get_card_id() in self.grades_for_day.keys():
			return False
		return True

	def process_queue(self, bot):

		now = datetime.datetime.now()
		hour = now.hour
		self.do_grading()

		if (self.user.working_hours(hour) == False):
			return True

		self.logger.debug("Process queue -> User State = {}".format(self.user.get_state()))
		if len(self.sending_queue) != 0 and self.user.get_state() == fsm.IDLE:
			self.user.set_state(fsm.LOCKED)
			self.do_grading(True)
			self.logger.info("Process Queue")
			number, waiting_type, aux_card = self.sending_queue.popleft()
			self.logger.debug("Card id {}".format(aux_card.get_card_id()))
			if self.user.check_card_existence(aux_card) and self.check_card_finished(aux_card, waiting_type) == False:
				return self.send_card(bot, aux_card, waiting_type, number)
			else:
				self.user.set_state(fsm.IDLE)
			self.logger.info("End Process Queue")



		return True

	def finish_process_learn_card(self, card):
		grades = self.grades_for_day[card.get_card_id()]
		self.logger.info("Finish Learning Card {}".format(card.get_card_id()))

		cnt = 0
		grade = 0
		self.logger.debug("Grades {}: ".format(card.get_card_id()) + str(grades))
		while cnt < 3 and len(grades) > 0:
			grade += grades.pop()
			cnt += 1
		if cnt == 0:
			return
		grade /= cnt
		card.calc_next_date(grade)

		self.logger.debug("Card_id = {}  grade = {}  next_date = {}".format(card.get_card_id(), grade, card.next_date))
		self.user.set_supermemo_data(card)
		self.remove_learning_card(card)
		self.logger.info("End Finish Learning Card {}".format(card.get_card_id()))



	def do_grading(self, green_light = False):
		if green_light == False and self.user.get_state() != fsm.IDLE:
			return

		
		user_id = self.user_id
		waiting = self.user.get_card_waiting()
		self.logger.debug("Do Grading - get card waiting {}".format(waiting))
		self.user.set_card_waiting(0)
		waiting_type = self.user.get_card_waiting_type()
		grade = self.user.get_grade_waiting()
		if waiting == 0:
			return

		aux_card = self.user.get_card(waiting)
		if aux_card != None:
			if waiting_type == LEARNING:
				self.logger.info("Do Grading Learning Card {} = {}".format(aux_card.get_card_id(), grade))
				self.grades_for_day[aux_card.get_card_id()].append(grade)
				
				debug_txt = "\n"
				for numero, lst in self.grades_for_day.items():
					debug_txt += "".format(numero) + str(lst) + "\n"
				
				self.logger.debug(debug_txt)


				if len(self.grades_for_day[aux_card.get_card_id()]) >= 1:
					cnt = 0
					tot = 0
					last = self.grades_for_day[aux_card.get_card_id()][-1]
					for i in reversed(self.grades_for_day[aux_card.get_card_id()]):
						tot += 1
						cnt += i
						if tot >= self.NUMBER_OF_LAST_CARDS:
							break;

					self.logger.debug("Tentar eliminar card {} -> Media= {} tot= {} Last= {}".format(aux_card.get_card_id(), cnt / tot, tot, last))
					if (tot >= self.NUMBER_OF_LAST_CARDS and (cnt / tot) >= 4.0) or last == 5:
						self.logger.debug("Card Eliminada {}".format(aux_card.get_card_id()))
						self.finish_process_learn_card(aux_card)
				self.logger.info("End Do Grading Learning Card {} = {}".format(aux_card.get_card_id(), grade))


			elif waiting_type == REVIEW:
				self.logger.info("Do Grading Review Card {} = {}".format(aux_card.get_card_id(), grade))
				aux_card.calc_next_date(grade)
				self.logger.debug("grade = {}  next_date = {}".format(grade, aux_card.next_date))
				self.user.set_supermemo_data(aux_card)
				self.logger.info("End Do Grading Review Card {} = {}".format(aux_card.get_card_id(), grade))




	def process_end_day(self):
		self.logger.info("Process End Day")

		for card in self.now_learn_stack:
			self.finish_process_learn_card(card)

		for card in self.next_learn_stack:
			self.finish_process_learn_card(card)
		self.logger.info("End Process End Day")



	def get_initialized(self):
		return self.initialized_for_day

	def reset_initialized(self):
		self.logger.info("Reset initialized for day")
		self.initialized_for_day = False









