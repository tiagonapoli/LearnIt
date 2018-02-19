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
from random import shuffle, randint
from utilities import utils


LEARNING = 1
REVIEW = 2

def process_card_end_day(user, card, grades):
	print("------------ {} PROCESS CARD END DAY------------".format(user.get_id()))
	cnt = 0
	grade = 0
	print(str(grades))
	while cnt < 3 and len(grades) > 0:
		grade += grades.pop()
		cnt += 1
	if cnt == 0:
		return
	grade /= cnt
	print(card)
	card.calc_next_date(grade)
	print("grade: {}  next_date: {}".format(grade, card.next_date))
	user.set_supermemo_data(card)



def process_end_day(user, cards_learning_for_day_user, grades_for_day_user):
	for card in cards_learning_for_day_user:
		process_card_end_day(user, card, grades_for_day_user[card.get_card_id()])


def init_user(user,
			  cards_review_for_day, cards_learning_for_day, grades_for_day,
			  learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
			  review_cnt_day, review_cnt_hourly, review_total_hourly,
			  sending_queue,
			  now):
	if user.get_active() == 0:
		return

	user_id = user.get_id()
	(cards_learning_for_day[user_id],
	 cards_review_for_day[user_id]) =  user.get_cards_for_day(now,
	 														  user.get_learning_words_limit(),
	 														  user.get_review_cards_limit())
	user.set_card_waiting(0)
	user.set_card_waiting_type(0)

	sending_queue[user_id] = deque()
	grades_for_day[user_id] = {}
	for card in cards_learning_for_day[user_id]:
		grades_for_day[user_id][card.get_card_id()] = []
	learning_cnt_hourly[user_id] = 0
	review_cnt_hourly[user_id] = 0
	learning_total_hourly[user_id] = 0
	review_total_hourly[user_id] = 0
	learning_cnt_day[user_id] = 0
	review_cnt_day[user_id] = 0


def init_user_day(user,
			  cards_review_for_day, cards_learning_for_day, grades_for_day,
			  learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
			  review_cnt_day, review_cnt_hourly, review_total_hourly,
			  sending_queue,
			  now):
	if user.get_active() == 0:
		return
	init_user(user,
			  cards_review_for_day, cards_learning_for_day, grades_for_day,
			  learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
			  review_cnt_day, review_cnt_hourly, review_total_hourly,
			  sending_queue,
			  now)


def hourly_init(user,
				learning_cnt_hourly, learning_total_hourly,
				review_cnt_hourly, review_total_hourly):
	if user.get_active() == 0:
		return

	user_id = user.get_id()
	learning_cnt_hourly[user_id] = 0
	review_cnt_hourly[user_id] = 0
	
	qtd = user.get_cards_per_hour()
	if qtd < 2:
		qtd = 2
	learning_total_hourly[user_id] = int(0.5 * qtd)
	remaining = qtd - learning_total_hourly[user_id]
	review_total_hourly[user_id] = remaining
	print("--------------- {} HOURLY INIT l:{}  r:{} ---------------".format(user_id,
																			 learning_total_hourly[user_id],
										  									 review_total_hourly[user_id]))


def prepare_queue(user,
			  	  cards_review_for_day, cards_learning_for_day, grades_for_day,
			  	  learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
			  	  review_cnt_day, review_cnt_hourly, review_total_hourly,
			  	  sending_queue,
			  	  hour, minute):
	if user.get_active() == 0:
		return

	user_id = user.get_id()
	total = learning_total_hourly[user_id] + review_total_hourly[user_id]
	total_sent = learning_cnt_hourly[user_id] + review_cnt_hourly[user_id]
	send_time_ini = int(60 * total_sent/total)



	print("--------------- Prepare queue {} ---------------".format(user_id))
	print("Hourly Process {}/{}\n".format(total_sent, total))
	print("Queue Len: {}".format(len(sending_queue[user_id])))
	print("min: {}  sending_time_ini: {}".format(minute, send_time_ini))
	if (user.working_hours(hour) == False):
		return

	if send_time_ini <= minute and len(sending_queue[user_id]) < 4:
		if (review_cnt_hourly[user_id] < review_total_hourly[user_id] and
			  review_cnt_day[user_id] >= len(cards_review_for_day[user_id])):
			learning_total_hourly[user_id] += 1
			review_total_hourly[user_id] -= 1

		if (learning_cnt_hourly[user_id] < learning_total_hourly[user_id] and
			len(cards_learning_for_day[user_id]) > 0):
			pos = learning_cnt_day[user_id] % len(cards_learning_for_day[user_id])
			sending_queue[user_id].append((learning_cnt_day[user_id] + 1, LEARNING, cards_learning_for_day[user_id][pos]))
			learning_cnt_hourly[user_id] += 1
			learning_cnt_day[user_id] += 1
			if (learning_cnt_day[user_id] % len(cards_learning_for_day[user_id])) == 0:
				shuffle(cards_learning_for_day[user_id])

		elif (review_cnt_hourly[user_id] < review_total_hourly[user_id] and
			  review_cnt_day[user_id] < len(cards_review_for_day[user_id])):
			pos = review_cnt_day[user_id]
			sending_queue[user_id].append((review_cnt_day[user_id] + 1, REVIEW, cards_review_for_day[user_id][pos]))
			review_cnt_hourly[user_id] += 1
			review_cnt_day[user_id] += 1


def do_grading(user, grades_for_day_user, green_light = False):
	if green_light == False and user.get_state() != fsm.IDLE:
		return
	
	waiting = user.get_card_waiting()
	user.set_card_waiting(0)
	waiting_type = user.get_card_waiting_type()
	grade = user.get_grade_waiting()
	if waiting == 0:
		return
	print("------------ {} DO GRADING - GRADE {} ------------".format(user.get_id(), grade))

	aux_card = user.get_card(waiting)
	print(aux_card)
	if aux_card != None:
		if waiting_type == LEARNING:
			print("TYPE LEARNING")
			grades_for_day_user[aux_card.get_card_id()].append(grade)
		elif waiting_type == REVIEW:
			print("TYPE REVIEW")
			aux_card.calc_next_date(grade)

			print(aux_card)
			print("grade: {}  next_date: {}".format(grade, aux_card.next_date))

			user.set_supermemo_data(aux_card)
	print("\n\n")




def send_card(bot, user, card, card_type, number):
	user_id = user.get_id()
	user.set_card_waiting_type(card_type)
	if card_type == LEARNING:
		print("{} SENDING LEARNING CARD".format(user_id))
		utils.send_review_card(bot, card, user, 'Learning', number)
	elif card_type == REVIEW:
		print("{} SENDING REVIEW CARD".format(user_id))
		utils.send_review_card(bot, card, user, 'Review', number)

	if card.get_type() == 'default':
		user.set_state(fsm.next_state[fsm.IDLE]['card_remember'])
	else:
		user.set_state(fsm.next_state[fsm.IDLE]['card_query'])

def process_queue(bot, user,
			  	  cards_review_for_day, cards_learning_for_day, grades_for_day,
			  	  learning_cnt_day, learning_cnt_hourly, learning_total_hourly,
			  	  review_cnt_day, review_cnt_hourly, review_total_hourly,
			  	  sending_queue,
			  	  hour):
	if user.get_active() == 0:
		return
		
	user_id = user.get_id()
	do_grading(user, grades_for_day[user_id])


	if (user.working_hours(hour) == False):
		return

	if len(sending_queue[user_id]) != 0 and user.get_state() == fsm.IDLE:
		user.set_state(fsm.LOCKED)
		do_grading(user, grades_for_day[user_id], True)
		print("--------------- {} PROCESS QUEUE ---------------".format(user_id))
		number, waiting_type, aux_card = sending_queue[user_id].popleft()
		print(aux_card)
		if user.check_card_existence(aux_card):
			send_card(bot, user, aux_card, waiting_type, number)
		else:
			user.set_state(fsm.IDLE)
