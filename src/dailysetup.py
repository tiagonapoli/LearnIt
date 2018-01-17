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

systemtools.schedule_daily_setup()
ACTIVE_MINUTES = 840
db = RuntimeData()
today = datetime.datetime.now()
print("Today: " + today.strftime('%m/%d/%Y'))

for user_id in db.known_users:
	cards = db.get_all_words_info(user_id)
	cnt = 0
	for card in cards:
		if card.get_next_date().date() <= today.date():
			cnt += 1
	time_accumulated = 0
	for card in cards:
		if card.get_next_date().date() <= today.date():
		
			print(time_accumulated + (ACTIVE_MINUTES // cnt))
			systemtools.set_new_at_job_card(time_accumulated + 
					(ACTIVE_MINUTES // cnt), user_id, card.word_id)
			time_accumulated += (ACTIVE_MINUTES // cnt)
