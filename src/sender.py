#!/usr/bin/python3
import telebot
import sys
import fsm
from runtimedata import RuntimeData
from flashcard import Card
from utilities import utils
from utilities import systemtools 
from utilities import bot_utils

"""
	Script to send a card query through message in Telegram. If this was 
	unsuccessful it will be rescheduled to min(10,tries) minutes from
	now.

	Usage:
		./sender.py user_id card_id tries

	Args:
		user_id: id of the receiver of the message
		card_id: id of the card to send
		tries: tries unsuccessfuly done to send this card to this user
"""


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


user_id = int(sys.argv[1])
card_id = int(sys.argv[2])
tried = int(sys.argv[3])

rtd = RuntimeData()
user = rtd.get_user(user_id)

print(sys.argv[1])
print("card id = " + sys.argv[2])
print(sys.argv[3])

if user.get_state() == fsm.IDLE:
	
	print("POSSO MANDAR A CARD ALEATORIA")

	user.set_state(fsm.LOCKED)	
	card = user.get_card(card_id)
	language = card.get_language()
	
	user.set_card_waiting(card.card_id)
	question = card.get_question()
	content = card.get_type()

	utils.send_review_card(bot, rtd, card, user)

	if content == 'default':
		text = ("*5* - _perfect response_\n" +
			 "*4* - _correct response after a hesitation_\n" +
			 "*3* - _correct response recalled with serious difficulty_\n" + 
			 "*2* - _incorrect response; where the correct one seemed easy to recall_\n" + 
			 "*1* - _incorrect response; the correct one remembered_\n" +
			 "*0* - _complete blackout._")
		markup = bot_utils.create_keyboard(['0','1','2','3','4','5'], 6)
		bot.send_message(user_id,"_Please grade how difficult is this word_\n" + text,
						reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.IDLE]['card_remember'])
	else:
		user.set_state(fsm.next_state[fsm.IDLE]['card_query'])
		
else:
	print("NAOO POSSO MANDAR A CARD ALEATORIA")
	tried += 1
	systemtools.set_new_at_job_card(min(tried,10),user_id,card_id, tried)	


