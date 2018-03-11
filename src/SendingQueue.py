
class SendingQueue():

	def __init__(self):

		self.cards_per_hour = 
		self.learn_cnt_day = 0
		self.learn_cnt_hourly = 0
		self.learn_total_hourly = 0

		self.review_cnt_day = 0
		self.review_cnt_hourly = 0
		self.review_total_hourly = 0

		self.learn_queue = LearningQueue()
		self.review_queue = ReviewQueue()
		self.cards_expired = []



	def update(self):
		self.logger.info("Upd cards expired")
		now = datetime.datetime.now()
		self.cards_expired = self.user.get_cards_expired(now)
		self.logger.info("End upd cards expired")

	def get_next(self):
		se o sending_queue vazio retorn none
		return self.sending_queue.front()

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
			len(self.sending_queue) < 1):
			
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

class LearningQueue():

	def __init__():
		self.learn_cards_day_set = set()



	def get_remaining_learn_cards(self):
		return len(self.now_learn_stack) + len(self.next_learn_stack)

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


class ReviewQueue():

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