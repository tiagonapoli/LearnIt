import datetime
import fsm
import logging
import time
from utilities import logging_utils
from SendingQueue import SendingQueue

def map_to_str(map):
	txt = ""
	for key, item in map.items():
		txt += "{}: {}\n".format(key, str(item))
	return txt

REVIEW = 1
LEARNING = 2


class UserSendingCardManager():

	def __init__(self, user):
		self.user = user
		self.logger = logging.getLogger(str(user.get_id()))
		self.grades_for_day = {}
		self.user.set_card_waiting(0)
		self.initialized_for_day = False
		self.sending_queue = SendingQueue(self.user)
		self.NUMBER_OF_LAST_CARDS = 2
		self.last_hour = datetime.datetime.now().hour
		self.last_update = time.time()
		self.update_interval = 180
		self.hourly_init()
		self.update()


	def init_day(self):
		now = datetime.datetime.now()
		hour = now.hour
		if self.initialized_for_day == False and hour == 0:
			self.logger.info("Daily Init")
			self.sending_queue.init_day()
			self.initialized_for_day = True


	def hourly_init(self):
		self.logger.info("Hourly Init")
		hour =  datetime.datetime.now().hour
		self.last_hour = hour
		self.sending_queue.hourly_init()
		if hour != 0:
			self.initialized_for_day = False
		else:
			self.init_day()

	def update(self):
		self.last_update = time.time()
		self.sending_queue.update()

		keys = list(self.grades_for_day.keys())
		self.logger.debug("Keys on grades_for_day: " + str(keys))
		for card_id in keys:
			if self.user.is_card_active(card_id) == 0:
				self.logger.debug("Obsolete key removed grades_for_day {}".format(card_id))
				self.grades_for_day.pop(card_id, None)


	def run(self):
		now = datetime.datetime.now()
		hour = now.hour
		if self.last_hour != hour:
			self.hourly_init()

		now = time.time()
		if now - self.last_update >= self.update_interval:
			self.logger.info("Update sending queue")
			self.update()

		self.do_grading()
		if self.user.get_state() == fsm.IDLE:
			self.user.set_state(fsm.LOCKED)
			
			self.logger.debug("Grades map:\n{}".format(map_to_str(self.grades_for_day)))			
			self.logger.debug("Sending queue state:\n{}".format(str(self.sending_queue)))

			card, number, card_type = self.sending_queue.pop()
			if card == None:
				self.user.set_state(fsm.IDLE)
				return
			self.do_grading(True)
			card_id = card.get_card_id()
			if self.user.is_card_active(card_id) > 0:
				success = self.user.send_card_query(card, card_type, number)
				self.logger.debug("Send Learning card {}".format(card_id))
			else:
				success = False
			if success:
				if card_type == 'Learning' and (not card_id in self.grades_for_day.keys()):
					self.grades_for_day[card_id] = []
				self.user.set_card_waiting(card.get_card_id())
				if card_type == 'Learning':
					self.user.set_card_waiting_type(LEARNING)
				else:
					self.user.set_card_waiting_type(REVIEW)
				self.user.set_state(fsm.next_state[fsm.IDLE]['card_query'])
			else:
				self.user.set_state(fsm.IDLE)


	def finish_learn_card(self, card):
		grades = self.grades_for_day[card.get_card_id()]
		self.logger.debug("Finish learn card {} -> {}".format(card.get_card_id(), str(grades)))
		cnt = 0
		grade = 0
		while cnt < 3 and len(grades) > 0:
			grade += grades.pop()
			cnt += 1
		if cnt == 0:
			return
		grade /= cnt
		card.calc_next_date(grade)
		self.user.set_supermemo_data(card)
		self.logger.debug("Grade = {}  -  NextDate = {}".format(grade, card.get_next_date()))
		self.sending_queue.remove_card(card)
		self.grades_for_day.pop(card.get_card_id(), None)


	def do_grading(self, green_light = False):
		if green_light == False and self.user.get_state() != fsm.IDLE:
			return

		waiting = self.user.get_card_waiting()
		waiting_type = self.user.get_card_waiting_type()
		grade = self.user.get_grade_waiting()
		self.user.set_card_waiting(0)
		if waiting == 0:
			return

		aux_card = self.user.get_card(waiting)
		if aux_card != None:
			self.logger.debug("Do grading {} - Grade= {}".format(aux_card.get_card_id(), grade))
			card_id = aux_card.get_card_id()
			if waiting_type == LEARNING:
				self.grades_for_day[card_id].append(grade)
				tot = 0
				cnt = 0
				last = self.grades_for_day[card_id][-1]
				for i in reversed(self.grades_for_day[card_id]):
					cnt += 1
					tot += i
					if cnt >= self.NUMBER_OF_LAST_CARDS:
						break;

				if (cnt >= self.NUMBER_OF_LAST_CARDS and (tot / cnt) >= 4.0) or last == 5:
					self.finish_learn_card(aux_card)
			elif waiting_type == REVIEW:
				aux_card.calc_next_date(grade)
				self.user.set_supermemo_data(aux_card)




	

	







	








 


	














