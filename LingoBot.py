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
contador_user = {}
step_id = {'0': 'IDLE',
		   '1': 'get_word_info->WAITING VOCABULARY',
		   '2': 'get_word_info->IMAGE_SOURCE',
		   '3': 'get_word_info->Receiving images', 
		   '4': 'get_word_info->Send image loop',
		   '5': 'get_word_info->Google image selection loop'
		   }

def get_user_state(ID):
	print("id:{}  state:{}".format(ID, userState[ID]))
	return userState[ID]

def add_user(ID):
	cursor.execute("SELECT id from users WHERE id={}".format(ID))
	rows = cursor.fetchall()
	for row in rows:
		if row[0] == ID:
			BOT.send_message(ID, "Welcome back to LingoBot!")
			return

	cursor.execute("INSERT INTO users VALUES ({}, 0);".format(ID))
	conn.commit()
	BOT.send_message(ID,"Welcome to LingoBot")

def add_word(ID):
	#temp_user -> idioma outro_idioma ingles path1 path2 path3 ... final da lista
	idiom = temp_user[ID][0]
	foreign_word = temp_user[ID][1]
	english_word = temp_user[ID][2]

	cursor.execute("INSERT INTO words VALUES ({}, '{}', '{}', '{}')".format(ID, idiom, foreign_word, english_word))	

	for i in range(3, len(temp_user[ID])):
		img_path = temp_user[ID][i]
		cursor.execute("INSERT INTO images VALUES ({}, '{}', '{}', DEFAULT, '{}')".format(ID, idiom, foreign_word, img_path))

	conn.commit()
	BOT.send_message(ID, "Word and images added successfully!")

def erase_word(ID, idiom, foreign_word):
	cursor.execute("SELECT FROM word WHERE id = {} AND english_word = '{}' AND foreign_word = '{}'".format(ID, idiom, foreign_word))
	rows = cursos.fetchall
	
	if len(rows) == 0:
		BOT.send_message(ID, "Invalid english word or foreign word")
		return

	cursor.execute("DELETE FROM word WHERE id = {} AND idiom = '{}' AND foreign_word = '{}'".format(ID, idiom, foreign_word))

	conn.commit()
	BOT.send_message(ID, "Word erased successfully!")

def save_image(image_msg, path):
	f = image_msg.photo[-1].file_id
	arq = bot.get_file(f)
	downloaded_file = bot.download_file(arq.file_path)
	tipo = []
	for c in arq.file_path[::-1]:
		print(c)
		if c == '.' :
			break
		tipo.append(c)
	tipo = "".join(tipo[::-1])
	with open(path + "." + tipo, 'wb') as new_file:
		new_file.write(downloaded_file)
	
@BOT.message_handler(commands = ['start'])
def setup_user(message):
	ID = message.chat.id
	print("NEW USER {}".format(ID))
	add_user(ID)
	userState[ID] = '0'

@BOT.message_handler(commands = ['cancel'])
def cancel(message):
	ID = message.chat.id
	userState[ID] = '0'

@BOT.message_handler(commands = ['add_word'])
def get_word_info(message):
	ID = message.chat.id
	vocab = message.text[16:]
	
	if len(vocab) == 0:
		BOT.send_message(ID, "Please, try again with a non-empty word")
		return

	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID, "Type english translation", reply_markup=markup)
	temp_user[ID] = []
	temp_user[ID].append(vocab)
	userState[ID] = '1'

@BOT.message_handler(func= lambda m: (get_user_state(m.chat.id) == '1'))
def get_word_name(message):
	ID = message.chat.id
	temp_user[ID].append(message.text)
#	f = open(str(ID) + '.txt', "a")
#	f.write("{} {}\n".format(temp_user[ID],message.text))
#	f.close();
	btn1 = telebot.types.KeyboardButton('Send image')
	btn2 = telebot.types.KeyboardButton('Choose one from suggestions')
	btn3 = telebot.types.KeyboardButton('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3)
	BOT.send_message(ID, "Choose one way to link images to word: ", reply_markup=markup)
	userState[ID] = '2'


@BOT.message_handler(func= lambda message: (get_user_state(message.chat.id) == '2') and message.text == "Send image")
def get_word_receive_image(message):
	ID = message.chat.id
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Send an image:",reply_markup=markup)
	userState[ID] = '3'

@BOT.message_handler(func= lambda message: get_user_state(message.chat.id) == '3', content_type=['photo'])
def get_word_ImagesFromUser1(message):
	ID = message.chat.id
	contador_user[ID] = 0
	btn1 = telebot.types.KeyboardButton('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)
	userState[ID] = '4'
	save_image(message,"{}/{}/img{}".format(ID,temp_user[ID][0],contador_user[ID]))

@BOT.message_handler(func= lambda message: get_user_state(message.chat.id) == '4', content_type=['photo', 'text'])
def get_word_ImagesFromUser2(message):
	contador_user[ID] += 1
	ID = message.chat.id
	if message.text == "Done":
		add_word(ID)
		userState[ID] = '0'
		markup = telebot.types.ReplyKeyboardRemove()
		BOT.send_message(ID,"Successfully done!",reply_markup=markup)
	else:
		save_image(message,"{}/{}/img{}".format(ID,temp_user[ID][0],contador_user[ID]))


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


BOT.polling()
turn_off()
