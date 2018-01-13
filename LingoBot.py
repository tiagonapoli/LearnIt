import os
import telebot
import time
import scrape_images
import psycopg2
import utils
import flags
from db_api import Database

try:
	arq = open("bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	BOT = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)

db = Database()
	
@BOT.message_handler(commands = ['start'])
def setup_user(message):
	ID = message.chat.id
	print("NEW USER {}".format(ID))
	m = db.add_user(ID)
	if m == flags.Message.WELCOME:
		BOT.send_message(ID, "Welcome to LingoBot!")
	else:
		BOT.send_message(ID, "Welcome back to LingBot!")
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


BOT.polling()
turn_off()
