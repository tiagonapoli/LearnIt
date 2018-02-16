#! /usr/bin/python3
import sys
import datetime
import telebot
import random
import time
import signal

import fsm
from collections import deque
from runtimedata import RuntimeData
from flashcard import Card
from utilities import utils

def signal_handler(sign, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	bot.send_message(359999978,"Sending manager turned off")
	print("Exiting sending manager...")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


try:
	arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot token or couldn't initialize bot")
	print(e)
	sys.exit(0)

rtd = RuntimeData()
rtd.get_known_users()
users = rtd.users
cards_for_day = {}
cards_quantity = {}
cards_sent = {}
daily_number = {}

now = datetime.datetime.now()
last_hour = (now.hour - 1 + 24) % 24

while True:
	try:
		print("WOKE UP")

		now = datetime.datetime.now()
		hour = now.hour 
		rtd.get_known_users()
		users = rtd.users

		if last_hour != hour:
			last_hour = hour
			for user_id, user in users.items():
				cards_quantity[user_id] = 5 + random.randint(1,1) 
				cards_sent[user_id] = 0

		for user_id, user in users.items():
			if (not (user_id in cards_for_day.keys())) or hour == 0:
				daily_number[user_id] = 0
			cards_for_day[user_id] = user.get_cards_expired(now)
			print("USER_ID {} cards_in_hour: {}  cards_for_day: {}".format(user_id, cards_quantity[user_id], len(cards_for_day[user_id])))

		print("\n")
		
		'''
		for user_id, user in users.items():
			print("USER CARDS {}  QTD: {}".format(user_id, len(cards_for_day[user_id])))
			for card in cards_for_day[user_id]:
				print(card)
		'''

		now = datetime.datetime.now()
		minute = now.minute
		for user_id, user in users.items():
			user_id = user.get_id()
			send_time_ini = int(60 * cards_sent[user_id]/cards_quantity[user_id])
			send_time_next = int(60 * (cards_sent[user_id] + 1)/cards_quantity[user_id])
			pos = daily_number[user_id]

			print("USER {} STATE {} TIME {} <= {} <= {}\nCARDS_SENT {}/{} FOR TODAY {}\n\n".format(
					user_id, user.get_state(), send_time_ini, minute, send_time_next, cards_sent[user_id],
					cards_quantity[user_id], len(cards_for_day[user_id])))

			if (cards_sent[user_id] == cards_quantity[user_id] or 
				user.working_hours(hour) == False):
				continue

			if send_time_ini <= minute and minute <= send_time_next and user.get_state() == fsm.IDLE:
				user.set_state(fsm.LOCKED)
				print("SENDING CARD {}".format(user_id))
				cards_sent[user_id] += 1
				aux_card = cards_for_day[user_id].pop()
				utils.send_review_card(bot, aux_card, user, daily_number[user_id])
				if aux_card.get_type() == 'default':
					user.set_state(fsm.next_state[fsm.IDLE]['card_remember'])
				else:
					user.set_state(fsm.next_state[fsm.IDLE]['card_query'])
				daily_number[user_id] += 1
			elif minute > send_time_next:
				cards_sent[user_id] += 1

			print("\n")

		sleep = 60
		print("SLEEP {}\n\n".format(sleep))
		time.sleep(sleep)
	except Exception as e:
		print("=====================An error ocurred with bot.polling======================")
		with open("exceptions_sending_manager.txt", "a") as myfile:
				myfile.write(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + "   " + str(e.__class__.__name__) + "\n")
		print(e.__class__.__name__)
		print(e)
		print("============================================================================")
		try:
			bot.send_message(359999978,"Sending manager crashed")
			bot.send_message(359999978,"{}".format(e))
		except Exception as ee:
			print(ee)
		time.sleep(240)
	