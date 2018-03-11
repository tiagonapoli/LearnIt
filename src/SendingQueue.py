from random import shuffle


class SendingQueue():

	def __init__(self, user):
		self.max_size = 1
		self.user = user

		self.cards_per_hour = 0
		self.learn_cnt_day = 0
		self.learn_cnt_hourly = 0
		self.learn_total_hourly = 0

		self.review_cnt_day = 0
		self.review_cnt_hourly = 0
		self.review_total_hourly = 0

		self.learn_queue = LearningQueue()
		self.review_queue = ReviewQueue()
		self.cards_expired = []

		self.queue = deque()

	def hourly_init(self):
		self.logger.info("Hourly init")
		now = datetime.datetime.now()
		hour = now.hour

		self.learn_cnt_hourly = 0
		self.review_cnt_hourly = 0
		
		qtd = self.cards_per_hour
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


	def init_day(self):
		self.logger.info("Init Day")
		self.logger.debug("Set card waiting 0")

		self.hourly_init()
		self.learn_queue.init_day()
		self.review_queue.init_day()
		self.logger.info("Initialized for day")
		self.logger.info("End init Day")


	def update(self):
		self.logger.info("Upd cards expired")
		now = datetime.datetime.now()
		self.cards_expired = self.user.get_cards_expired(now)

		expired_learning_cards = []
		expired_review_cards = []

		for card in self.user.expired_cards:
			if card.is_learning():
				expired_learning_cards.append(card)
			else:
				expired_review_cards.append(card)

		self.learn_queue.update(expired_learning_cards)
		self.review_queue.update(expired_review_cards)

		self.logger.info("End upd cards expired")

	def pop(self):
		self.prepare_queue()

		if len(self.queue) == 0:
			return (None, -1, -1)

		return self.queue.pop_left()

	def prepare_queue(self):
		now = datetime.datetime.now()
		minute = now.minute

		total = self.learn_total_hourly + self.review_total_hourly
		total_sent = self.learn_cnt_hourly + self.review_cnt_hourly
		send_time_ini = int(60 * total_sent/total)

		# self.logger.info("Hourly process: {}/{}".format(total_sent, total))
		# self.logger.debug("Remaining cards: L={}  R={}".format(self.get_remaining_learn_cards(), len(self.now_review_stack)))
		# self.logger.debug("Queue: " + sending_queue_to_str(self._queue))
		# self.logger.debug("learn now:" + stack_to_str(self.now_learn_stack)) 
		# self.logger.debug("learn next:" + stack_to_str(self.next_learn_stack)) 
		# self.logger.debug("review now:" + stack_to_str(self.now_review_stack)) 
		# self.logger.debug("min: {}  send_time_ini: {}".format(minute, send_time_ini))


		if send_time_ini <= minute and len(self.queue) < self.max_size:
	
			if self.learn_queue.size() > 0 or self.review_queue.size() > 0:			
				if self.review_cnt_hourly < self.review_total_hourly and self.review_queue.size() == 0:
					self.learn_total_hourly += 1
					self.review_total_hourly -= 1
				elif self.learn_cnt_hourly < self.learn_total_hourly and self.learn_queue.size() == 0:
					self.learn_total_hourly -= 1
					self.review_total_hourly += 1

			if self.learn_cnt_hourly < self.learn_total_hourly and self.learn_queue.size() > 0:
				card, number = self.learn_queue.pop()
				while (learn_queue.size() > 0 and self.user.check_card_existence(card) == False):
					card, number = self.learn_queue.pop()
				
				if self.user.check_card_existence(card):
					self.queue.append((card, number, 'Learning'))
					self.learn_cnt_hourly += 1

			elif (self.review_cnt_hourly < self.review_total_hourly and self.review_queue.size() > 0):
				card, number = self.review_queue.pop()
				while (review_queue.size() > 0 and self.user.check_card_existence(card) == False):
					card, number = self.review_queue.pop()
				
				if self.user.check_card_existence(card):
					self.queue.append((card, number, 'Review'))
					self.review_cnt_hourly += 1

		self.logger.info("End prepare queue")


class LearningQueue():

	def __init__():
		self.queue = []
		self.queue_aux = []
		self.cards_set = set()
		self.study_items_limit = 3
		self.cards_sent = 0

	def __str__(self):
		pass

	def daily_init(self, expired_cards):
		self.cards_sent = 0
		self.update(expired_cards)


	def update(self, expired_cards):
		study_items_set = set()

		for card in self.queue:
			study_items_set.add(card.get_study_item_id())

		for card in self.queue_aux:
			study_items_set.add(card.get_study_item_id())

		if len(study_items_set) >= self.study_items_limit:
			return

		cards = expired_cards
		added = 0
		new_cards = []
		for card in cards:
			if not card.get_card_id() in self.cards_set:
				if (len(study_items_set) < self.study_items_limit
					or (len(study_items_set) == study_items_limit and (card.get_study_item_id() in study_items_set))):
					added += 1
					new_cards.append(card.get_card_id())
					self.queue_aux.append(card)
					study_items_set.add(card.get_study_item_id())
					self.cards_set.add(card.get_card_id())

		if added > 0:
			self.logger.debug('Added {} learning cards: '.format(added) + str(new_cards))


	def get_size(self):
		return len(self.queue) + len(self.queue_aux)

	def remove_card(self, card):
		card_id = card.get_card_id()
		self.logger.info('Remove learning card {}'.format(card_id))

		i = 0
		while i < len(self.queue):
			if card_id == self.queue[i].get_card_id():
				 self.queue.pop(i)
			else:
				i += 1

		i = 0
		while i < len(self.queue_aux):
			if card_id == self.queue_aux[i].get_card_id():
				 self.queue_aux.pop(i)
			else:
				i += 1

		self.logger.debug("now:" + stack_to_str(self.now_learn_stack) + 
			"\n 						next: " + stack_to_str(self.next_learn_stack)) 
		self.logger.info('End remove learning card {}'.format(card_id))


	def pop(self):
		if self.size() == 0:
			return (None, -1)

		if len(self.queue) == 0:
			while len(self.queue_aux) > 0:
				self.queue.append(self.queue_aux.pop())

		card = self.queue.pop()
		self.cards_sent += 1
		return (card, self.cards_sent)

class ReviewQueue():

	def __init__(self):
		self.queue = []
		self.cards_set = set()
		self.cards_sent = 0
		self.max_size = 15

	def __str__(self):
		pass


	def daily_init(self, expired_cards):
		self.cards_sent = 0
		self.update(expired_cards)


	def update(self, expired_cards):
		for card in expired_cards:
			if len(self.queue) == self.max_size:
				break

			if not (card.get_card_id() in self.cards.set):
				self.queue.append(card)

		shuffle(self.queue)
		self.queue.sort()


	def get_size(self):
		return len(self.queue)


	def pop(self):
		if len(self.queue) == 0:
			return (None, -1)

		card = self.queue.pop()
		self.cards_sent += 1
		return (card, self.cards_sent)