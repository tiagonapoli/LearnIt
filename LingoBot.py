#! /usr/bin/python3
import sys
import telebot
import scrape_images
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
	sys.exit(0)	

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

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '0'), commands = ['add_language'])
def add_language(message):
	ID = get_id(message)
	language = message.text[14:]
	language = language.lstrip().rstrip()
	print(language)
	
	if(len(language) == 0):
		BOT.reply_to(message, "Usage: /add_language 'language you want to add' (without quotes)")
		return

	BOT.send_message(ID, rt_data.add_language(ID, language))

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '0'), commands = ['add_word'])
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
	rt_data.set_state(ID, '1_0')

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '1_0'), content_types=['text'])
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
	rt_data.set_state(ID, '1_1')

@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '1_1'), content_types=['text'])
def get_word_foreign(message):
	ID = get_id(message)
	word = message.text
	word = word.strip()

	rt_data.temp_user[ID].append(word)

	BOT.send_message(ID, "Send english translation")
	rt_data.set_state(ID, '1_2')


@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '1_2'), content_types=['text'])
def get_word_translation(message):
	ID = get_id(message)
	word = message.text
	word = word.strip()
	rt_data.temp_user[ID].append(word)
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Choose one from suggestions')
	btn3 = create_key_button('Use only english translation')
	btn4 = create_key_button('Send audio')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3,btn4)
	BOT.send_message(ID, "Choose one way to relate images to word: ", reply_markup=markup)
	rt_data.set_state(ID, '1_3')

def back_to_word_options(message):
	#Retira o tipo do content
	rt_data.temp_user[ID].pop()
	ID = get_id(message)
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Choose one from suggestions')
	btn3 = create_key_button('Use only english translation')
	btn4 = create_key_button('Send audio')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3,btn4)
	BOT.send_message(ID, "Choose one way to relate to word: ", reply_markup=markup)
	rt_data.set_state(ID, '1_3')

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '1_3') and message.text == "Send image")
def get_word_receive_image_option(message):
	ID = get_id(message)
	rt_data.temp_user[ID].append("Image")
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Send an image:",reply_markup=markup)
	rt_data.set_state(ID, '1_3-opt1')

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '1_3') and message.text == "Choose one from suggestions")
def get_word_google_images(message):
	ID = get_id(message)
	rt_data.temp_user[ID].append("Image")
	fetch_images(temp_user[ID][2],"tmp/{}".format(ID))
	rt_data.loop[ID] = []
	rt_data.loop[ID] = os.listdir("./tmp/{}".format(ID))
	if len(rt_data.loop[ID]) == 0:
		BOT.send_message(ID, "Sorry, something wrong happened, we couldn't find images")
		return 0

	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn1 = create_key_button('Add Image')
	btn2 = create_key_button('Skip Image')
	markup.row(btn1,btn2)
	BOT.send_message(ID, "We will present you some images from google images (the query is the english translation). Please use the custom keyboard to select the images you want.", reply_markup=markup)
	
	photo = open('./tmp/{}/{}'.format(ID,rt_data.loop[ID][len(loop[ID])-1]))
	BOT.send_photo(ID, photo)

	rt_data.set_state(ID, '1_3-opt2_0')	


@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '1_3') and message.text == "Use only english translation")
def get_word_english_translation(message):
	ID = get_id(message)
	rt_data.temp_user[ID].append("Translation")
	rt_data.add_word(ID)
	rt_data.set_state(ID, '0')
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Successfully done!",reply_markup=markup)

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '1_3') and message.text == "Send audio")
def get_word_english_translation(message):
	rt_data.temp_user[ID].append("Audio")
	rt_data.add_word(ID)
	rt_data.set_state(ID, '0')
	markup = telebot.types.ReplyKeyboardRemove()
	BOT.send_message(ID,"Successfully done!",reply_markup=markup)

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '1_3-opt1', content_types=['photo'])
def get_word_ImagesFromUser1(message):
	ID = get_id(message)
	rt_data.contador_user[ID] = 0
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)

	BOT.send_message(ID, "Keep sending images or click on the 'Done' button", reply_markup=markup)
	
	rt_data.set_state(ID, '1_3-opt1_0')
	filename = rt_data.temp_user[ID][1].replace(' ', '_')
	path = utils.save_image(message,"{}/{}/".format(ID, rt_data.temp_user[ID][0]), "{}{}".format(filename,rt_data.contador_user[ID]), BOT)
	rt_data.temp_user[ID].append(path)

@BOT.message_handler(func= lambda message: rt_data.get_state(get_id(message)) == '1_3-opt1_0', content_types=['photo', 'text'])
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

@BOT.message_handler(func= lambda message: (rt_data.get_state(get_id(message)) == '1_3-opt2_0'), content_types=['text'])
def get_word_google_images_loop(message):
	ID = get_id(message)
	
	if message.text == "Add Image":
		rt_data.temp_user[ID].append(rt_data.loop[ID].pop())
	elif message.text == "Skip Image":
		rt_data.loop[ID].pop()

	if len(loop[ID]) == 0:
		markup = telebot.types.ReplyKeyboardRemove()
		if len(rt_data.temp_user[ID]) == 4:
			BOT.send_message(ID, "Sorry, the suggestions weren't so good, you can change the link type now", reply_markup=markup)
			back_to_word_options(message)
			return 0
		else:
			rt_data.add_word(ID)
			rt_data.set_state(ID, '0')
			markup = telebot.types.ReplyKeyboardRemove()
			BOT.send_message(ID,"Successfully done!",reply_markup=markup)
	else:
		photo = open('./tmp/{}/{}'.format(ID,rt_data.loop[ID][len(loop[ID])-1]))
		BOT.send_photo(ID, photo)

		
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


@BOT.message_handler(func= lambda m: (rt_data.get_state(m.chat.id) == '0'), commands = ['settings'])
def set_settings(message):
	return 0	





def signal_handler(signal, frame):
	utils.turn_off()
	print('Exiting bot...')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit gently')

print("Bot Polling")
BOT.polling()
