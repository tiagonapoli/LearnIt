#!/usr/bin/python3
import telebot
import sys
import systemtools 
from RuntimeData import RuntimeData
from FlashCard import Word
#USAGE: ./sender.py IDUSER IDCARD tries

try:
	arq = open("bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	BOT = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)


IDuser = int(sys.argv[1])
IDcard = int(sys.argv[2])
tried = int(sys.argv[3])
rt_data = RuntimeData()

if rt_data.get_state(IDuser) == '0':
	word = rt_data.get_word(IDuser,IDcard)
	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID,word.english_word, reply_markup=markup)
	rt_data.set_state(ID, 'WAITING_ANS/{}'.format(IDcard))
else:
	tried += 1
	systemtools.set_new_at_job_card(min(tried,10),IDuser,IDcard, tried)	


