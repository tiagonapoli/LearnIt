import time
import datetime

class FlashCardSM:
	n = None
	ef = None
	interval = None
	last_date = None

	def __init__(self,_n=0, _ef=2.5,_interval=0, _last_date = datetime.datetime.now()):
		self.n = _n
		self.ef = _ef
		self.interval = _interval
		self.last_date = _last_date


	def set_variables(self,_n, _ef,_interval, _last_date = datetime.datetime.now()):
		self.n = _n
		self.ef = _ef
		self.interval = _interval
		self.last_date = _last_date


	def go_next_state(self,q):
		self.n += 1
		if self.n == 1:
			self.interval = 1
		elif self.n == 2:
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
		end_date = self.last_date + datetime.timedelta(days=int(self.interval))

		self.last_date = end_date
		return end_date
	
	def get_date(self):
		return last_date

	def get_data(self):
		return self.n,self.ef,self.interval,self.last_date


