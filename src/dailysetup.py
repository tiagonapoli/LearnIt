#! /usr/bin/python3
import datetime
from runtimedata import RuntimeData
from flashcard import Card
from utilities import systemtools

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
	words = db.get_all_words(user_id)

	cards = []
	for word in words:
		aux = word.get_cards()
		for card in aux:
			cards.append(card)

	cnt = 0
	for card in cards:
		if card.get_next_date() <= today.date():
			cnt += 1
	time_accumulated = 0
	for card in cards:
		if card.get_next_date() <= today.date():
			print("CARDSSSSSSSSSSS-------------------------------------")
			print(card)
			print(time_accumulated + (ACTIVE_MINUTES // cnt))
			systemtools.set_new_at_job_card(time_accumulated + 
					(ACTIVE_MINUTES // cnt), user_id, card.card_id)
			time_accumulated += (ACTIVE_MINUTES // cnt)
