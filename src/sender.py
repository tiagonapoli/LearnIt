#!/usr/bin/python3
import telebot
import sys
import systemtools 
from runtimedata import RuntimeData
from flashcard import Card
import fsm

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

def create_key_button(text):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text: Text of the button
	"""
	return telebot.types.KeyboardButton(text)


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

print(sys.argv[1])
print("card id = " + sys.argv[2])
print(sys.argv[3])

user_id = int(sys.argv[1])
card_id = int(sys.argv[2])
tried = int(sys.argv[3])
rtd = RuntimeData()

if rtd.get_state(user_id) == fsm.IDLE:
	rtd.set_state(user_id, fsm.LOCKED)
	card = rtd.get_card(user_id,card_id)
	language = card.get_language()
	
	bot.send_message(user_id, "Review card!")
	rtd.set_card_waiting(user_id, card.card_id)
	markup = telebot.types.ForceReply(selective = False)
	question = card.get_question()
	content = card.get_type()
	if content == 'image':
		bot.send_message(user_id, "Relate the image to a word in {}".format(language))
		question = open(question,'rb')
		bot.send_photo(user_id, question, reply_markup = markup)
		question.close()
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['card_query'])
	elif content == 'audio':
		bot.send_message(user_id, "Transcribe the audio in {}".format(language))
		question = open(question,'rb')
		bot.send_voice(user_id, question, reply_markup = markup)
		question.close()
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['card_query'])
	elif content == 'translation':
		bot.send_message(user_id, "Translate the word to {}".format(language))
		bot.send_message(user_id, question, reply_markup = markup)
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['card_query'])
	elif content == 'default':
		bot.send_message(user_id, "Just remember the usage and meaning of the next word.".format(language))
		bot.send_message(user_id, question)
		btn0 = create_key_button("0");
		btn1 = create_key_button("1");
		btn2 = create_key_button("2");
		btn3 = create_key_button("3");
		btn4 = create_key_button("4");
		btn5 = create_key_button("5");
		markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(btn0,btn1,btn2,btn3,btn4,btn5)

		bot.send_message(user_id,"Please grade how difficult is this word",
						reply_markup=markup)
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['card_remember'])
else:
	tried += 1
	systemtools.set_new_at_job_card(min(tried,10),user_id,card_id, tried)	


