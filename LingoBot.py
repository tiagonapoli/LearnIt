import os
import telebot
import time

arq = open("bot_token.txt", "r")
TOKEN = (arq.read().splitlines())[0]
arq.close()

BOT = telebot.TeleBot(TOKEN)


temp_user = {}
knownUsers = set()
userState = {}
step_id = {0: 'IDLE',
		   1: 'get_vocab_inf->WAITING VOCABULARY'}


def setup():
	filename = "knownusers.txt"
	f = 0
	if os.path.isfile(filename) == False:
		f  = open(filename, "w")
	else:
		f  = open(filename, "r+")
		knownusers = f.read().split(' ')
		for user in knownusers:
			knownUsers.add(int(user))
			userState[int(user)] = 0
	f.close()

def get_user_state(ID):
	print("id:{}  state:{}".format(ID, userState[ID]))
	return userState[ID]

def add_user(ID):
	if ID in knownUsers:
		return

	knownUsers.add(ID)
	userState[ID] = 0
	f = open("knownusers.txt", "a")
	f.write(' ' + str(ID))
	f.close()

@BOT.message_handler(commands = ['start'])
def setup_user(message):
	ID = message.chat.id;
	print("NEW USER {}".format(ID))
	BOT.send_message(ID,"Welcome to LingoBot")
	add_user(ID)
	userState[ID] = 0

@BOT.message_handler(commands = ['add_vocabulary'])
def get_vocab_info(message):
	ID = message.chat.id
	vocab = message.text[16:]
	
	if len(vocab) == 0:
		BOT.send_message(ID, "Please, try again with a non-empty word")
		return

	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID, "Type english translation", reply_markup=markup)
	temp_user[ID] = vocab
	userState[ID] = 1;

@BOT.message_handler(commands = ['set_state'])
def set_state(message):
	ID = message.chat.id
	number = message.text[11:]
	print("new state:{}".format(int(number)))
	userState[ID] = int(number)
	print("id:{} state:{}".format(ID, userState[ID]))

@BOT.message_handler(func= lambda message: get_user_state(message.chat.id) == 1)
def get_vocab_name(message):
	ID = message.chat.id
	
	f = open(str(ID), "a")
	f.write("{} {}\n".format(temp_user[ID],message.text))
	f.close();

setup()
BOT.polling()