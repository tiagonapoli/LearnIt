#! /usr/bin/python3
from RuntimeData import RuntimeData
import systemtools
import datetime

ACTIVE_MINUTES = 60
db = RuntimeData()
today = datetime.datetime.now()

for user in db.knowUsers:
	cards = db.get_all_words_info(user)
	#tuple unpacking
	for wordID,card in cards:
		cnt = 0
		if card.get_date().date() <= today.date():
			cnt += 1
	for wordID,card in cards:
		if card.get_date().date() <= today.date():
			systemtools.set_new_at_job_card(user, ACTIVE_MINUTES // cnt,(user,wordID)) 
