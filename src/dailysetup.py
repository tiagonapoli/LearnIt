#! /usr/bin/python3
import systemtools
import datetime
from runtimedata import RuntimeData
from flashcard import Card

"""
	Script that schedules all send jobs that have to be sent today.
	
	Global Constant:
		ACTIVE_MINUTES: Minutes past 8 AM that the user is able to receive messages.

"""

ACTIVE_MINUTES = 60
db = RuntimeData()
today = datetime.datetime.now()

for user_id in db.get_known_users():
	cards = db.get_all_words_info(user_id)
	for card in cards:
		cnt = 0
		if card.get_date().date() <= today.date():
			cnt += 1
	time_acumulated = 5
	for card in cards:
		if card.get_date().date() <= today.date():
			systemtools.set_new_at_job_card(time_accumulated + 
					ACTIVE_MINUTES // cnt, user_id, card.wordID)
			time_accumulated += ACTIVE_MINUTES // cnt
