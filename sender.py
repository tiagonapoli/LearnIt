#!/usr/bin/python3
import telebot
import sys
import systemtools 

#USAGE: ./sender.py ID TEXTO

arq = open("bot_token.txt", "r")
TOKEN = (arq.read().splitlines())[0]
arq.close()


BOT = telebot.TeleBot(TOKEN)
ID = int(sys.argv[1])
text = sys.argv[2].split(' ')
vocab_number = text[0]
tried = int(text[1])

print(ID)
print(text)

##### CHECK IF USERSTATE = IDLE
if False:
	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID, text, reply_markup=markup)
else:
	tried += 1
	systemtools.set_new_at_job_VocabQuery(ID,min(tried,10),"{} {}".format(vocab_number,tried))	


