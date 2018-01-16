#! /usr/bin/python3
import sys
import os
import telebot
import utils
import signal
import shutil
from scrapeimages import fetch_images
from runtimedata import RuntimeData
from flashcard import Card 

"""
	Bot message handlers source file


	State Machine Map:

	0 (idle):
		WAITING_ANS
		1_0
		2_0
	
	Where:
		
		WAITING_ANS -> WAITING_POLL_ANS -> 0

		2_0 (add new language sequence) -> 0

		1_0 (add word sequence) -> 1_1 -> 1_2 -> 1_3:
			1_3-opt1 (Send message) 
			1_3-opt2 (Choose one from suggestion)
			1_3-opt3 (Send audio)
		
			Where:	
				1_3-opt1 (Send Message) -> 1_3-opt1_1:
					1_3-opt1_1 (loop)
					0 (end loop)

				1_3-opt2 (Choose one from suggestions):
					1_3-opt2 (loop)
					0 (end loop)

				1_3-opt3 (Send audio) -> 1_3-opt3_1 -> 0

"""

def signal_handler(signal, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	utils.turn_off()
	print("Exiting bot...")
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
	arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot = telebot.TeleBot(TOKEN)
	print("Bot initialized successfully!")
except Exception as e:
	print("Can't retrieve the bot's token")
	print(e)
	sys.exit(0)	
	
rt_data = RuntimeData()
rt_data.reset_all_states()




def get_id(msg):
	"""
		Gets message user ID
		Return:
			User ID: integer
	"""
	return msg.chat.id




def create_key_button(text):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text: Text of the button
	"""
	return telebot.types.KeyboardButton(text)




@bot.message_handler(commands = ['start'])
def setup_user(msg):
	"""
		Register user into database.
	"""
	user_id = get_id(msg)
	m = rt_data.add_user(user_id)
	bot.send_message(user_id, m)




@bot.message_handler(commands = ['cancel'])
def cancel(msg):
	"""
		Cancels any ongoing events for the user.
	"""
	user_id = get_id(msg)
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id, "canceled...", reply_markup=markup)
	rt_data.set_state(user_id, '0')




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == 'WAITING_ANS', 
				content_types = ['text'])
def answer_card(msg):
	"""
		Get user answer to card sequence
	"""

	user_id = get_id(msg)
	res = msg.text.strip()
	card = rt_data.get_word(user_id,rt_data.get_state2(user_id))
	rt_data.temp_user[user_id] = []
	rt_data.temp_user[user_id].append(card)
	if res == card.get_ans():
		bot.send_message(user_id, "That was correct!")
	else:
		bot.send_message(user_id, "There was a mistake :(")
	bot.send_message(user_id, "Answer: " + card.get_ans())
	btn0 = create_key_button("0");
	btn1 = create_key_button("1");
	btn2 = create_key_button("2");
	btn3 = create_key_button("3");
	btn4 = create_key_button("4");
	btn5 = create_key_button("5");
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn0,btn1,btn2,btn3,btn4,btn5)

	bot.send_message(user_id,"Please grade your performance to answer the card",
					reply_markup=markup)
	rt_data.set_state(user_id, "WAITING_POLL_ANS")




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == 'WAITING_POLL_ANS',
				content_types=['text'])
def poll_difficulty(msg):
	"""
		Get user performance grade
	"""
	
	user_id = get_id(msg)
	card = rt_data.temp_user[user_id].pop()
	try:
		grade = int(msg.text)
	except:
		bot.send_message(user_id, "Please use the custom keyboard")
		return
	
	if not (grade <= 5 and grade >= 0):
		bot.send_message(user_id, "Please use the custom keyboard")
		return
	
	card.calc_next_date(grade)
	rt_data.set_supermemo_data(card)
	print(word.get_next_date())
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"OK!", reply_markup=markup)
	rt_data.set_state(user_id, "0")




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '0', 
				commands = ['add_language'])
def add_language(msg):
	""" 
		Add language sequence
	"""
	user_id = get_id(msg)
	bot.send_message(user_id, "Text me the language you want to add")
	rt_data.set_state(user_id, "2_0")




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '2_0', 
				content_types = ['text'])
def add_language_0(msg):
	"""
		Get language text - Add language
	"""
	user_id = get_id(msg)
	language = msg.text
	language = language.strip()
	print(language)
	bot.send_message(user_id, rt_data.add_language(user_id, language))
	rt_data.set_state(user_id, "0")




@bot.message_handler(func = lambda msg:
				rt_data.get_state(get_id(msg)) == '0', 
				commands = ['add_word'])
def get_word(msg):
	"""
		Add word: Get word sequence
	"""
	user_id = get_id(msg)
	known_languages = rt_data.get_user_languages(user_id)
	
	btn = []
	for language in known_languages:
		btn.append(create_key_button(language))
	
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for i in range(0,len(btn)//2):
		markup.row(btn[2*i], btn[2*i+1])

	if len(btn)%2 == 1:
		markup.row(btn[len(btn)-1])

	bot.send_message(user_id, "Please select the word's language", 
					reply_markup=markup)	
	rt_data.set_state(user_id, '1_0')




@bot.message_handler(func = lambda msg:
				rt_data.get_state(get_id(msg)) == '1_0',
				content_types=['text'])
def get_word_0(msg):
	"""
		Add word: Get word's language
	"""
	user_id = get_id(msg)
	known_languages = rt_data.get_user_languages(user_id)
	language = msg.text.strip()
	if not (language in known_languages):
		bot.reply_to(msg, "Please choose from keyboard")
		return

	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id, "Send word to add (in {})".format(language),
					reply_markup=markup)
	rt_data.temp_user[user_id] = []
	rt_data.temp_user[user_id].append(msg.text)
	rt_data.set_state(user_id, '1_1')




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_1', 
				content_types=['text'])
def get_word_1(msg):
	"""
		Add word: Get foreign word
	"""
	user_id = get_id(msg)
	word = msg.text.strip()
	rt_data.temp_user[user_id].append(word)
	bot.send_message(user_id, "Send english translation")
	rt_data.set_state(user_id, '1_2')




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_2',
				content_types=['text'])
def get_word_2(msg):
	"""
		Add word: Get english translation
		Creates menu of choices to relate to the word
	"""
	user_id = get_id(msg)
	word = msg.text.strip()
	rt_data.temp_user[user_id].append(word)
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Choose one from suggestions')
	btn3 = create_key_button('Send audio')
	btn4 = create_key_button('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3,btn4)
	bot.send_message(user_id, "Choose one way to relate to the word: ",
					reply_markup=markup)
	rt_data.set_state(user_id, '1_3')




def back_to_word_options(msg):
	"""
		Add word: Back to menu with choices to relate to the word
	"""
	user_id = get_id(msg)
	rt_data.temp_user[user_id].pop()
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Choose one from suggestions')
	btn3 = create_key_button('Send audio')
	btn4 = create_key_button('Use only english translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3,btn4)
	bot.send_message(user_id, "Choose one way to relate to the word: ",
					reply_markup=markup)
	rt_data.set_state(user_id, '1_3')




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3' and 
				msg.text == "Send image")
def get_word_3opt1(msg):
	"""
		Add word: User just chose to Send Images -> Receive images sequence
	"""
	user_id = get_id(msg)
	rt_data.temp_user[user_id].append("Image")
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Send an image:",
					reply_markup=markup)
	rt_data.set_state(user_id, '1_3-opt1')




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3' and 
				msg.text == "Choose one from suggestions")
def get_word_3opt2(msg):
	"""
		Add word: User just chose select image from suggestions
	"""
	user_id = get_id(msg)
	rt_data.temp_user[user_id].append("Image")
	
	bot.send_message(user_id, "This may take a few seconds...")

	path = "../data/tmp/{}".format(user_id)
	if not os.path.exists(path):
		os.makedirs(path)
	else:
		shutil.rmtree(path)
		os.makedirs(path)	

	fetch_images(rt_data.temp_user[user_id][2],path)
	rt_data.loop[user_id] = []
	rt_data.loop[user_id] = os.listdir(path)

	if len(rt_data.loop[user_id]) == 0:
		bot.send_message(user_id, 
						"Sorry, something wrong happened, we couldn't find images")
		back_to_word_options()
		return

	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn1 = create_key_button('Add Image')
	btn2 = create_key_button('Skip Image')
	markup.row(btn1,btn2)
	bot.send_message(user_id, "We will present you some images from google images(the query is the english translation). Please use the custom keyboard to select the images you want.",
					reply_markup=markup)

	
	
	photo = ('../data/tmp/{}/{}'.format(user_id,
									rt_data.loop[user_id][
										len(rt_data.loop[user_id])-1]))
	print(photo)
	photo = open(photo,'rb')
	bot.send_photo(user_id, photo)

	rt_data.set_state(user_id, '1_3-opt2_1')	




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3' and 
				msg.text == "Send audio")
def get_word_3opt3(msg):
	"""
		Add word: User just chose to send audio
	"""
	rt_data.temp_user[user_id].append("Audio")
	rt_data.add_word(user_id)
	rt_data.set_state(user_id, '0')
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Successfully done!",
					reply_markup=markup)




@bot.message_handler(func = lambda msg:
				rt_data.get_state(get_id(msg)) == '1_3' and 
				msg.text == "Use only english translation")
def get_word_3opt4(msg):
	"""
		Add word: User just chose to Send Images -> Receive images sequence
	"""
	user_id = get_id(msg)
	rt_data.temp_user[user_id].append("Translation")
	rt_data.add_word(user_id)
	rt_data.set_state(user_id, '0')
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Successfully done!",
					reply_markup=markup)




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3-opt1', 
				content_types=['photo'])
def get_word_3opt1_0(msg):
	"""
		Add word: Send images sequence -> Receiving images
		Creates custom keyboard with done button and receives the first image
	"""
	user_id = get_id(msg)
	rt_data.counter_user[user_id] = 0
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)

	bot.send_message(user_id, "Keep sending images or click on the 'Done' button",
					reply_markup=markup)
	
	rt_data.set_state(user_id, '1_3-opt1_1')
	filename = rt_data.get_highest_word_id(user_id)
	path = utils.save_image(msg,
							"../data/{}/{}/".format(user_id, rt_data.temp_user[user_id][0]), 
							"{}_{}".format(filename,rt_data.counter_user[user_id]), 
							bot)
	rt_data.temp_user[user_id].append(path)




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3-opt1_1', 
				content_types=['photo', 'text'])
def get_word_3opt1_1(msg):
	"""
		Add word: Send images sequence -> Receive Done command or more images
	"""
	user_id = get_id(msg)
	rt_data.counter_user[user_id] += 1
	if msg.text == "Done":
		rt_data.add_word(user_id)
		rt_data.set_state(user_id, '0')
		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id,"Successfully done!",
						reply_markup=markup)
	else:
		filename = rt_data.get_highest_word_id(user_id)
		path = utils.save_image(msg,
								"../data/{}/{}/".format(user_id, rt_data.temp_user[user_id][0]), 
								"{}_{}".format(filename,rt_data.counter_user[user_id]), 
								bot)
		rt_data.temp_user[user_id].append(path)




@bot.message_handler(func = lambda msg: 
				rt_data.get_state(get_id(msg)) == '1_3-opt2_1',
				content_types=['text'])
def get_word_3opt2_1(msg):
	"""
		Add word: Choose images from suggestion sequence -> loops through
		all images in tmp file for that word. User choose which will be added
	"""
	user_id = get_id(msg)
	
	if msg.text == "Add Image":
		rt_data.temp_user[user_id].append(rt_data.loop[user_id].pop())
	elif msg.text == "Skip Image":
		rt_data.loop[user_id].pop()

	if len(rt_data.loop[user_id]) == 0:
		markup = telebot.types.ReplyKeyboardRemove()
		if len(rt_data.temp_user[user_id]) == 4:
			bot.send_message(user_id,
							"Sorry, the suggestions weren't so good, you can change the link type now", 
							reply_markup=markup)
			back_to_word_options(msg)
			return 0
		else:
			rt_data.add_word(user_id)
			rt_data.set_state(user_id, '0')
			markup = telebot.types.ReplyKeyboardRemove()
			bot.send_message(user_id,"Successfully done!",reply_markup=markup)
	else:
		photo = ('../data/tmp/{}/{}'.format(user_id,
										rt_data.loop[user_id][
											len(rt_data.loop[user_id])-1]))
		print(photo)
		photo = open(photo,'rb')
		bot.send_photo(user_id, photo)




@bot.message_handler(commands = ['set_state'])
def set_state(msg):
	"""
		Used for debug only. Set user state
	"""
	user_id = get_id(msg)
	number = msg.text[11:]
	if len(number) == 0:
		bot.sent_message(user_id, "don't forget the new state")
		return 0
	print("new state:{}".format(int(number)))
	rt_data.set_state(user_id, str(int(number)))
	print("id:{} state:{}".format(user_id, rt_data.get_state(user_id)))




@bot.message_handler(func = lambda msg: 
			rt_data.get_state(get_id(msg)) == '0', 
			commands = ['settings'])
def set_settings(msg):
	"""
		Change setting sequence
	"""
	return 0


print("Press Ctrl+C to exit gently")
print("Bot Polling")
bot.polling()

