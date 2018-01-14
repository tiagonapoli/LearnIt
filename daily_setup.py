#! /usr/bin/python3
import systemtools
import datetime
from RuntimeData import RuntimeData

ACTIVE_MINUTES = 60
db = RuntimeData()
today = datetime.datetime.now()

for user in db.knowUsers:
	cards = db.get_all_words_info(user)
	#tuple unpacking
	for IDcard,card in cards:
		cnt = 0
		if card.get_date().date() <= today.date():
			cnt += 1
	time_acumulated = 0
	for IDcard,card in cards:
		if card.get_date().date() <= today.date():
			systemtools.set_new_at_job_card(time_accumulated + ACTIVE_MINUTES // cnt,user,IDcard)
			time_accumulated += ACTIVE_MINUTES // cnt
