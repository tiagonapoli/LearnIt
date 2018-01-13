import os
import telebot
import time
import scrape_images
import psycopg2
import flags
import utils
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

def get_keybutton(text):
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

@BOT.message_handler(commands = ['add_word'])
def get_word_info(message):
	ID = get_id(message)
	vocab = message.text[16:]
	
	if len(vocab) == 0:
		BOT.send_message(ID, "Please, try again with a non-empty word")
		return

	markup = telebot.types.ForceReply(selective = False)
	BOT.send_message(ID, "Type english translation", reply_markup=markup)
	temp_user[ID] = []
	temp_user[ID].append(vocab)
	rt_data.set_state(ID, '1')
@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '1'))

def get_word_name(message):
	ID = get_id(message)
	temp_user[ID].append(message.text)
	btn1 = get_key_button('Send image')
	btn2 = get_key_button('Choose one from suggestions')
	btn3 = get_key_button('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3)
	BOT.send_message(ID, "Choose one way to link images to word: ", reply_markup=markup)
	rt_data.set_state(ID, '2')

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '2') and message.text == "Send image")
def get_word_receive_image(message):
	ID = get_id(message)
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Send an image:",reply_markup=markup)
	rt_data.set_state(ID, '3')

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '3', content_type=['photo'])
def get_word_ImagesFromUser1(message):
	ID = get_id(message)
	contador_user[ID] = 0
	btn1 = get_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)
	rt_data.set_state(ID, '4')
	save_image(message,"{}/{}/img{}".format(ID,temp_user[ID][0],contador_user[ID]))

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '4', content_type=['photo', 'text'])
def get_word_ImagesFromUser2(message):
	contador_user[ID] += 1
	ID = get_id(message)
	if message.text == "Done":
		add_word(ID)
		rt_data.set_state(ID, '0')
		markup = telebot.types.ReplyKeyboardRemove()
		BOT.send_message(ID,"Successfully done!",reply_markup=markup)
	else:
		save_image(message,"{}/{}/img{}".format(ID,temp_user[ID][0],contador_user[ID]))

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


BOT.polling()
turn_off()
