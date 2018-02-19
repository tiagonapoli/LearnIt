#! /usr/bin/python3
import sys
import datetime
import telebot
import random
import time
import signal

import fsm
from queue import Queue
from runtimedata import RuntimeData
from flashcard import Card
from utilities import sending_utils



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


cards_review_for_day = {}
grades_for_day = {}
cards_learning_for_day = {}

learning_cnt_day = {}
learning_cnt_hourly = {}
learning_total_hourly = {}

review_cnt_day = {}
review_cnt_hourly = {}
review_total_hourly = {}

sending_queue = {}
initialized_for_day = {}

now = datetime.datetime.now()
last_hour = (now.hour - 1 + 24) % 24


while True:
	try:
		print("WOKE UP")

		now = datetime.datetime.now()
		hour = now.hour 
		rtd.get_known_users()

		users = rtd.users

		for user_id, user in users.items():
			if (user_id in cards_review_for_day.keys()) and hour == 0 and initialized_for_day[user_id] == False:
				sending_utils.process_end_day(user, 
											  cards_learning_for_day[user_id], 
											  grades_for_day[user_id])
				sending_utils.init_user_day(user,
										cards_review_for_day, cards_learning_for_day, grades_for_day,
										learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
										review_cnt_day, review_cnt_hourly, review_total_hourly,
										sending_queue,
										now)
				initialized_for_day[user_id] = True
			
			if (not (user_id in cards_review_for_day.keys())):
				sending_utils.init_user(user,
										cards_review_for_day, cards_learning_for_day, grades_for_day,
										learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
										review_cnt_day, review_cnt_hourly, review_total_hourly,
										sending_queue,
										now)
				sending_utils.hourly_init(user,
									      learning_cnt_hourly, learning_total_hourly,
										  review_cnt_hourly, review_total_hourly)
				initialized_for_day[user_id] = True

				print("--------------- {} REVIEW QTD {} ---------------".format(user_id, len(cards_review_for_day[user_id])))
				#for card in cards_review_for_day[user_id]:
				#	print(card)
				
				print("--------------- {} LEARNING QTD {} ---------------".format(user_id, len(cards_learning_for_day[user_id])))
				#for card in cards_learning_for_day[user_id]:
				#	print(card)

			if hour != 0:
				initialized_for_day[user_id] = False
				


		if last_hour != hour:
			last_hour = hour
			for user_id, user in users.items():
				sending_utils.hourly_init(user,
									      learning_cnt_hourly, learning_total_hourly,
										  review_cnt_hourly, review_total_hourly)
		

		now = datetime.datetime.now()
		minute = now.minute

		for user_id, user in users.items():
			sending_utils.prepare_queue(user,
								  	    cards_review_for_day, cards_learning_for_day, grades_for_day,
								  	    learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
								  	    review_cnt_day, review_cnt_hourly, review_total_hourly,
								  	    sending_queue,
								  	    hour, minute)


			

		for user_id, user in users.items():
			sending_utils.process_queue(bot, user,
								  	    cards_review_for_day, cards_learning_for_day, grades_for_day,
								  	    learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
								  	    review_cnt_day, review_cnt_hourly, review_total_hourly,
								  	    sending_queue,
								  	    hour)



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
		time.sleep(60)

	