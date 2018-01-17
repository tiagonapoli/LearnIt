#!/usr/bin/python3
import telebot
import sys
import systemtools 
from runtimedata import RuntimeData
from flashcard import Card

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
	print("Can't retrieve the bot's token or couldn't initialize bot")
	print(e)
	sys.exit(0)

print(sys.argv[1])
print("card id = " + sys.argv[2])
print(sys.argv[3])

user_id = int(sys.argv[1])
card_id = int(sys.argv[2])
tried = int(sys.argv[3])
rt_data = RuntimeData()

if rt_data.get_state(user_id) == '0':
	rt_data.set_state(user_id, 'LOCKED')
	card = rt_data.get_word_info(user_id,card_id)
	
	bot.send_message(user_id,
			"Review card! Answer with the respective word in {}".format(
				card.get_language()))
	
	markup = telebot.types.ForceReply(selective = False)
	question = card.get_question()
	content = card.get_question_content()
	if content == 'Image':
		question = open(question,'rb')
		bot.send_photo(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'Audio':
		question = open(question,'rb')
		bot.send_audio(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'Translation':
		bot.send_message(user_id, question, reply_markup = markup)
	
	rt_data.set_state(user_id, 'WAITING_ANS', card_id)
else:
	tried += 1
	systemtools.set_new_at_job_card(min(tried,10),user_id,card_id, tried)	


