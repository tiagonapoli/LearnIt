import os
import telebot
import time
import scrape_images
import psycopg2

try:
	arq = open("bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()

	BOT = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)

try:
	arq = open("connect_str.txt", "r")
	connect_str = arq.read()
	arq.close()
	print(connect_str)
	# use our connection values to establish a connection
	conn = psycopg2.connect(connect_str)
	# create a psycopg2 cursor that can execute queries
	cursor = conn.cursor()
	print("Connected with database!")
except Exception as e:
	print("Uh oh, can't connect. Invalid dbname, user or password?")
	print(e)


loop = {}
temp_user = {}
knownUsers = set()
userState = {}
step_id = {'0': 'IDLE',
		   '1': 'get_word_info->WAITING VOCABULARY',
		   '2': 'get_word_info->IMAGE_SOURCE',
		   '3': 'get_word_info->Receiving images', 
		   '4': 'get_word_info->Send image loop',
		   '5': 'get_word_info->Google image selection loop'
		   }


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
	
	for user in knownUsers:
		print("{} : {}".format(user, userState[user]))

def get_user_state(ID):
	print("id:{}  state:{}".format(ID, userState[ID]))
	return userState[ID]

def add_user(ID):
	cursor.execute("SELECT id from users")
	rows = cursor.fetchall()
	for row in rows:
		if row[0] == ID:
			BOT.send_message(ID, "Welcome back to LingoBot!")
			return

	cursor.execute("INSERT INTO users VALUES ({}, 0);".format(ID))
	conn.commit()
	BOT.send_message(ID,"Welcome to LingoBot")

@BOT.message_handler(commands = ['start'])
def setup_user(message):
	ID = message.chat.id;
	print("NEW USER {}".format(ID))
	add_user(ID)
	userState[ID] = '0'

@BOT.message_handler(commands = ['add_vocabulary'])
def get_word_info(message):
	ID = message.chat.id
	vocab = message.text[16:]
	
	if len(vocab) == 0:
		BOT.send_message(ID, "Please, try again with a non-empty word")
		return

	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID, "Type english translation", reply_markup=markup)
	temp_user[ID] = vocab
	userState[ID] = '1'

@BOT.message_handler(func= lambda m: (get_user_state(m.chat.id) == '1'))
def get_word_name(message):
	ID = message.chat.id
	temp_user[ID] = message.text
#	f = open(str(ID) + '.txt', "a")
#	f.write("{} {}\n".format(temp_user[ID],message.text))
#	f.close();
	btn1 = telebot.types.KeyboardButton('Send image')
	btn2 = telebot.types.KeyboardButton('Choose one from suggestions')
	btn3 = telebot.types.KeyboardButton('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3)
	BOT.send_message(ID, "Choose one way to link images to vocab: ", reply_markup=markup)
	userState[ID] = '2'


@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '2') and message.text == "Send image")
def get_word_receive_image(message):
	ID = message.chat.id
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Send an image:",reply_markup=markup)
	userState[ID] = '3'

@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '3'))
def get_word_receive_images_loop(message):
	#SAVE IMAGE
	ID = message.chat.id
	btn1 = telebot.types.KeyboardButton('Send another image')
	btn2 = telebot.types.KeyboardButton('End')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	BOT.send_message(ID, "Another image?: ", reply_markup=markup)
	userState[ID] = '4'

@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '4'))
def get_word_receive_loop_decide (message):
	ID = message.chat.id
	if message.text == "Send another image":
		userState[ID] = '3'
	elif message.text == "End":
		#END REGISTRATION
		#FALTA
		userState[ID] = '0'
	else:
		#TRATARRRR
		print("MSG INESPERADA")

@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '2') and message.text == "Choose one from suggestions")
def get_word_google_images(message):
	ID = message.chat.id
	fetch_images(temp_user[ID],"tmp/{}".format(ID))
	loop[ID].clear()
	loop[ID] = os.listdir()
	userState[ID] = '5'
	


@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '2') and message.text == "Use only english translation")
def get_word_english_translation(message):
	return 0

@BOT.message_handler(commands = ['set_state'])
def set_state(message):
	ID = message.chat.id
	number = message.text[11:]
	if len(number) == 0:
		BOT.sent_message(ID, "don't forget the new state")
		return 0
	print("new state:{}".format(int(number)))
	userState[ID] = str(int(number))
	print("id:{} state:{}".format(ID, userState[ID]))


@BOT.message_handler(commads = ['settings'])
def set_settings(message):
	return 0	

def turn_off():
	conn.close()
	cursor.close()
	print("YESSSSS")


setup()
BOT.polling()
turn_off()
