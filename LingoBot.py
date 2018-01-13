#! /usr/bin/python3
import sys
import os
import telebot
import time
import scrape_images
import psycopg2
import utils
import signal
from RuntimeData import RuntimeData

try:
	arq = open("bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	BOT = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)

rt_data = RuntimeData()

def get_id(message):
	return message.chat.id

def create_key_button(text):
	return telebot.types.KeyboardButton(text)

@BOT.message_handler(commands = ['start'])
def setup_user(message):
	ID = get_id(message)
	print("NEW USER {}".format(ID))
	m = rt_data.add_user(ID)
	BOT.send_message(ID, m)

@BOT.message_handler(commands = ['cancel'])
def cancel(message):
	ID = get_id(message)
	rt_data.set_state(ID, '0')

@BOT.message_handler(commands = ['add_language'])
def add_language(message):
	ID = get_id(message)
	language = message.text[14:]
	language = language.lstrip().rstrip()
	print(language)
	
	if(len(language) == 0):
		BOT.reply_to(message, "Usage: /add_language 'language you want to add' (without quotes)")
		return

	BOT.send_message(ID, rt_data.add_language(ID, language))

@BOT.message_handler(commands = ['add_word'])
def get_word_info(message):
	ID = get_id(message)
	known_languages = rt_data.get_user_languages(ID)
	
	btn = []
	for language in known_languages:
		btn.append(create_key_button(language))
	
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for i in range(0,len(btn)//2):
		markup.row(btn[2*i], btn[2*i+1])

	if len(btn)%2 == 1:
		markup.row(btn[len(btn)-1])

	BOT.send_message(ID, "Please select the word's language", reply_markup=markup)	
	rt_data.set_state(ID, '1')

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '1'), content_types=['text'])
def get_lang(message):
	ID = get_id(message)
	known_languages = rt_data.get_user_languages(ID)
	if not (message.text in known_languages):
		BOT.reply_to(message, "Please choose from keyboard")
		return

	markup = telebot.types.ReplyKeyboardRemove()

	BOT.send_message(ID, "Send word to add (in {})".format(message.text), reply_markup=markup)
	rt_data.temp_user[ID] = []
	rt_data.temp_user[ID].append(message.text)
	rt_data.set_state(ID, '2')

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '2'), content_types=['text'])
def get_word_foreign(message):
	ID = get_id(message)
	word = message.text
	word = word.strip()

	rt_data.temp_user[ID].append(word)

	BOT.send_message(ID, "Send english translation")
	rt_data.set_state(ID, '3')


@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '3'), content_types=['text'])
def get_word_translation(message):
	ID = get_id(message)
	word = message.text
	word = word.strip()
	rt_data.temp_user[ID].append(word)
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Choose one from suggestions')
	btn3 = create_key_button('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3)
	BOT.send_message(ID, "Choose one way to link images to word: ", reply_markup=markup)
	rt_data.set_state(ID, '4')

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '4') and message.text == "Send image")
def get_word_receive_image_option(message):
	ID = get_id(message)
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Send an image:",reply_markup=markup)
	rt_data.set_state(ID, '5')

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '5', content_types=['photo'])
def get_word_ImagesFromUser1(message):
	ID = get_id(message)
	rt_data.contador_user[ID] = 0
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)

	BOT.send_message(ID, "Keep sending images or click on the 'Done' button", reply_markup=markup)
	
	rt_data.set_state(ID, '6')
	filename = rt_data.temp_user[ID][1].replace(' ', '_')
	path = utils.save_image(message,"{}/{}/".format(ID, rt_data.temp_user[ID][0]), "{}{}".format(filename,rt_data.contador_user[ID]), BOT)
	rt_data.temp_user[ID].append(path)

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '6', content_types=['photo', 'text'])
def get_word_ImagesFromUser2(message):
	ID = get_id(message)
	rt_data.contador_user[ID] += 1
	if message.text == "Done":
		rt_data.add_word(ID)
		rt_data.set_state(ID, '0')
		markup = telebot.types.ReplyKeyboardRemove()
		BOT.send_message(ID,"Successfully done!",reply_markup=markup)
	else:
		filename = rt_data.temp_user[ID][1].replace(' ', '_')
		path = utils.save_image(message,"{}/{}/".format(ID, rt_data.temp_user[ID][0]), "{}{}".format(filename,rt_data.contador_user[ID]), BOT)
		rt_data.temp_user[ID].append(path)

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '2') and message.text == "Choose one from suggestions")
def get_word_google_images(message):
	ID = get_id(message)
	fetch_images(temp_user[ID],"tmp/{}".format(ID))
	loop[ID].clear()
	loop[ID] = os.listdir()
	rt_data.set_state(ID, '5')	

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '2') and message.text == "Use only english translation")
def get_word_english_translation(message):
	return 0

@BOT.message_handler(commands = ['set_state'])
def set_state(message):
	ID = get_id(message)
	number = message.text[11:]
	if len(number) == 0:
		BOT.sent_message(ID, "don't forget the new state")
		return 0
	print("new state:{}".format(int(number)))
	rt_data.set_state(ID, str(int(number)))
	print("id:{} state:{}".format(ID, userState[ID]))


@BOT.message_handler(commads = ['settings'])
def set_settings(message):
	return 0	

def signal_handler(signal, frame):
	utils.turn_off()
	print('Exiting bot...')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit gently')
signal.pause()

BOT.polling()
