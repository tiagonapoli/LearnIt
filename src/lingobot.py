#! /usr/bin/python3
import sys
import telebot
import utils
import signal
import systemtools
import time
import fsm
from runtimedata import RuntimeData
from flashcard import Card, Word 


"""
	Bot message handlers source file
"""


def signal_handler(signal, frame):
	"""
		Handles CTRL+C signal that exits gently the bot
	"""
	bot.send_message(359999978,"Bot turned off")
	utils.turn_off(rtd)
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
	
rtd = RuntimeData()
rtd.reset_all_states()
systemtools.schedule_daily_setup()

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

#=====================SETUP USER=====================

@bot.message_handler(commands = ['start'])
def setup_user(msg):
	"""
		Register user into database.
	"""
	user_id = get_id(msg)
	if user_id in rtd.known_users:
		return
	m = rtd.add_user(user_id)
	bot.send_message(user_id, m)
	rtd.set_state(user_id, fsm.IDLE)
	

#=====================CANCEL=====================


@bot.message_handler(func = lambda msg: rtd.not_locked(get_id(msg)) , commands = ['cancel'])
def cancel(msg):
	"""
		Cancels any ongoing events for the user.
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id, "canceled...", reply_markup=markup)
	rtd.set_state(user_id, fsm.IDLE)


#=====================ANSWER CARD=====================


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.WAITING_ANS, 
				content_types = ['text'])
def answer_card(msg):
	"""
		Get user answer to card sequence
	"""

	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	card_id = rtd.get_card_waiting(user_id)
	card = rtd.get_card(user_id, card_id)
	res = msg.text.strip().lower()
	rtd.temp_user[user_id] = []
	rtd.temp_user[user_id].append(card)
	if res == card.foreign_word.lower():
		bot.send_message(user_id, "That was correct!")
	else:
		bot.send_message(user_id, "There was a mistake :(")
	bot.send_message(user_id, "Answer: " + card.foreign_word)
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
	rtd.set_state(user_id, fsm.next_state[fsm.WAITING_ANS])




@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.WAITING_POLL_ANS,
				content_types=['text'])
def poll_difficulty(msg):
	"""
		Get user performance grade
	"""
	
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	card = rtd.temp_user[user_id][0]
	try:
		grade = int(msg.text)
	except:
		bot.send_message(user_id, "Please use the custom keyboard")
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
		return
	
	if not (grade <= 5 and grade >= 0):
		bot.send_message(user_id, "Please use the custom keyboard")
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
		return
	
	card.calc_next_date(grade)
	rtd.set_supermemo_data(card)
	print(card.get_next_date())
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"OK!", reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['done'])

#=====================REMEMBER CARD=====================

@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.WAITING_POLL_REMEMBER,
				content_types=['text'])
def poll_difficulty(msg):
	"""
		Get user performance grade
	"""
	
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	card_id = rtd.get_card_waiting(user_id)
	card = rtd.get_card(user_id, card_id)
	try:
		grade = int(msg.text)
	except:
		bot.send_message(user_id, "Please use the custom keyboard")
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
		return
	
	if not (grade <= 5 and grade >= 0):
		bot.send_message(user_id, "Please use the custom keyboard")
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
		return
	
	card.calc_next_date(grade)
	rtd.set_supermemo_data(card)
	print(card.get_next_date())
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"OK!", reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['done'])

#=====================ADD LANGUAGE=====================


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.IDLE, 
				commands = ['add_language'])
def add_language(msg):
	""" 
		Add language sequence
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	bot.send_message(user_id, "Text me the language you want to add")
	rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['add_language'])




@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.ADD_LANGUAGE, 
				content_types = ['text'])
def add_language_0(msg):
	"""
		Get language text - Add language
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	language = msg.text
	language = language.strip()
	print(language)
	bot.send_message(user_id, rtd.add_language(user_id, language))
	rtd.set_state(user_id, fsm.next_state[fsm.ADD_LANGUAGE])

#=====================ADD WORD=====================


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == fsm.IDLE, 
				commands = ['add_word'])
def add_word(msg):
	"""
		Add word: Get word sequence
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	known_languages = rtd.get_user_languages(user_id)
	
	btn = []
	for language in known_languages:
		btn.append(create_key_button(language))
	
	if len(btn) == 0:
		bot.send_message(user_id, "Please, add a language first.")
		rtd.set_state(user_id, fsm.IDLE)
		return 	

	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

	for i in range(0,len(btn)//2):
		markup.row(btn[2*i], btn[2*i+1])

	if len(btn)%2 == 1:
		markup.row(btn[len(btn)-1])

	bot.send_message(user_id, "Please select the word's language", 
					reply_markup=markup)	
	rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['add_word'])




@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.GET_LANGUAGE),
				content_types=['text'])
def add_word1(msg):
	"""
		Add word: Get word's language
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	known_languages = rtd.get_user_languages(user_id)
	language = msg.text.strip()
	if not (language in known_languages):
		bot.reply_to(msg, "Please choose from keyboard")
		rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['error'])
		return



	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id, "Send the word's topic, either a new topic or select from existing".format(language),
					reply_markup=markup)
	topics = rtd.get_all_topics(user_id, language)

	if len(topics) > 0:
		str = "Topics registered:\n"
		for topic in topics:
			str += "/" + topic.replace(' ', '_') + '\n'
		bot.send_message(user_id, str)
	else: 
		bot.send_message(user_id, "There are no topics registered in this language yet.")
	rtd.temp_user[user_id] = []
	rtd.temp_user[user_id].append(Word(user_id, rtd.get_highest_word_id(user_id) + 1))
	rtd.temp_user[user_id][0].language = language
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['done'])



@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.GET_TOPIC), 
				content_types=['text'])
def add_word2(msg):
	"""
		Add word: Get topic
	"""
	
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	language = rtd.temp_user[user_id][0].get_language()
	topic = msg.text.strip()
	topic = topic.replace('_', ' ')
	topic = topic.replace('/', '')

	rtd.temp_user[user_id][0].topic = topic
	bot.send_message(user_id, "Send word to add (in {})".format(language))
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_TOPIC)])




@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.GET_WORD), 
				content_types=['text'])
def add_word3(msg):
	"""
		Add word: Get foreign word
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)

	word = msg.text.strip()
	rtd.temp_user[user_id][0].foreign_word = word
	word = rtd.temp_user[user_id][0]
	card_default = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word, rtd.get_highest_card_id(user_id) + 1, 'default')
	card_default.add_archive(card_default.foreign_word)
	rtd.temp_user[user_id][0].set_card(card_default)

	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Send audio')
	btn3 = create_key_button('Send translation')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3)
	bot.send_message(user_id, "Choose one way to relate to the word: ",
					reply_markup=markup)	
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)])


def back_to_relate_menu(msg):
	"""
		Add word: Back to menu with choices to relate to the word
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	btn1 = create_key_button('Send image')
	btn2 = create_key_button('Send audio')
	btn3 = create_key_button('Send translation')
	btn4 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1,btn2)
	markup.row(btn3,btn4)
	bot.send_message(user_id, "Choose another way to relate to the word (if a way already filled is chosen, the data will be overwritten): ",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)])


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.RELATE_MENU) and 
				msg.text == "Done")
def relate_menu_done(msg):
	"""
		Add word: User just chose 'Done' on Relate Menu
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	word = rtd.temp_user[user_id][0]
	rtd.add_word(word)
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Successfully done!",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['done'])



@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.RELATE_MENU) and 
				msg.text == "Send audio")
def add_word4(msg):
	"""
		Add word: User just chose to send audio
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	word = rtd.temp_user[user_id][0]
	if 'audio' in word.cards.keys():
		card_id = word.cards['audio'].card_id
		word.cards['audio'].erase_all_archives_local()
	else:
		card_id = rtd.get_highest_card_id(user_id) + 1 + len(word.cards)
	
	card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
				card_id, 'audio')
	if(len(rtd.temp_user[user_id]) == 1):
		rtd.temp_user[user_id].append(card)
	else:
		rtd.temp_user[user_id][1] = card
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Send an audio:",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['send_audio'])


@bot.message_handler(func = lambda msg: rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_AUDIO),
					 content_types=['audio', 'voice'])
def add_word5(msg):
	"""
		ADD_WORD, SEND_AUDIO
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	rtd.counter_user[user_id] = 0
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)
	
	filename = rtd.temp_user[user_id][1].card_id
	path = ""
	if msg.audio != None:
		path = utils.save_audio(msg,
							"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
							"{}_{}".format(filename,rtd.counter_user[user_id]), 
							bot)
	elif msg.voice != None:
		path = utils.save_voice(msg,
							"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
							"{}_{}".format(filename,rtd.counter_user[user_id]), 
							bot)

	print(path)
	rtd.temp_user[user_id][1].add_archive(path)
	rtd.counter_user[user_id] += 1
	bot.send_message(user_id, "Keep sending audios or click on the 'Done' button",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)])


@bot.message_handler(func = lambda msg:	rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_AUDIO_LOOP),
					 content_types= ['audio', 'voice', 'text'])
def add_word6(msg):
	"""
		ADD_WORD, SEND_AUDIO_LOOP
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	if msg.text == "Done":
		card = rtd.temp_user[user_id].pop()
		rtd.temp_user[user_id][0].set_card(card)
		markup = telebot.types.ReplyKeyboardRemove()
		print(str(rtd.temp_user[user_id][0]))
		back_to_relate_menu(msg)
		return
	elif msg.audio != None or msg.voice != None:
		filename = rtd.temp_user[user_id][1].card_id
		path = ""
		if msg.audio != None:
			path = utils.save_audio(msg,
								"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
								"{}_{}".format(filename,rtd.counter_user[user_id]), 
								bot)
		elif msg.voice != None:
			path = utils.save_voice(msg,
								"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
								"{}_{}".format(filename,rtd.counter_user[user_id]), 
								bot)
		print(path)
		rtd.temp_user[user_id][1].add_archive(path)
		rtd.counter_user[user_id] += 1
		bot.send_message(user_id, "Keep sending audios or click on the 'Done' button")
		rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO_LOOP)])


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.RELATE_MENU) and 
				msg.text == "Send translation")
def add_word7(msg):
	"""
		ADD_WORD, RELATE_MENU, 'send_translation'
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	word = rtd.temp_user[user_id][0]
	if 'translation' in word.cards.keys():
		card_id = word.cards['translation'].card_id
		word.cards['translation'].erase_all_archives_local()
	else:
		card_id = rtd.get_highest_card_id(user_id) + 1 + len(word.cards)
	
	card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
				card_id, 'translation')
	if(len(rtd.temp_user[user_id]) == 1):
		rtd.temp_user[user_id].append(card)
	else:
		rtd.temp_user[user_id][1] = card
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Send a translation to {}:".format(word.foreign_word),
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['send_translation'])



@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_TRANSLATION),
				content_types=['text'])
def add_word8(msg):
	"""
		ADD_WORD, RELATE_MENU, 'send_translation'
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)
	
	translation = msg.text.strip()
	print(translation)
	word = rtd.temp_user[user_id][0].foreign_word
	rtd.temp_user[user_id][1].add_archive(translation)
	bot.send_message(user_id, "Keep sending translations to {} or click on the 'Done' button".format(word),
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_TRANSLATION)])


@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_TRANSLATION_LOOP),
				content_types=['text'])
def add_word9(msg):
	"""
		ADD_WORD, SEND_TRANSLATION_LOOP
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	if msg.text == "Done":
		card = rtd.temp_user[user_id].pop()
		rtd.temp_user[user_id][0].set_card(card)
		markup = telebot.types.ReplyKeyboardRemove()
		print(str(rtd.temp_user[user_id][0]))
		back_to_relate_menu(msg)
		return
	elif len(msg.text.strip()) != 0:
		translation = msg.text.strip()
		print(translation)
		word = rtd.temp_user[user_id][0].foreign_word
		rtd.temp_user[user_id][1].add_archive(translation)
		bot.send_message(user_id, "Keep sending translations to {} or click on the 'Done' button".format(word))
		rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_TRANSLATION_LOOP)])



@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.RELATE_MENU) and 
				msg.text == "Send image")
def add_word10(msg):
	"""
		Add word: User just chose to Send Images -> Receive images sequence
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	word = rtd.temp_user[user_id][0]
	if 'image' in word.cards.keys():
		card_id = word.cards['image'].card_id
		word.cards['image'].erase_all_archives_local()
	else:
		card_id = rtd.get_highest_card_id(user_id) + 1 + len(word.cards)
	
	card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
				card_id, 'image')
	if(len(rtd.temp_user[user_id]) == 1):
		rtd.temp_user[user_id].append(card)
	else:
		rtd.temp_user[user_id][1] = card
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(user_id,"Send an image (Suggestion, use @pic 'query' or @bing 'query' to find an image):",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['send_image'])



@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_IMAGE), 
				content_types=['photo'])
def add_word11(msg):
	"""
		Add word: Send images sequence -> Receiving images
		Creates custom keyboard with done button and receives the first image
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	rtd.counter_user[user_id] = 0
	btn1 = create_key_button('Done')
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.row(btn1)
	
	filename = rtd.temp_user[user_id][1].card_id
	path = utils.save_image(msg,
							"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
							"{}_{}".format(filename,rtd.counter_user[user_id]), 
							bot)
	
	print(path)
	rtd.temp_user[user_id][1].add_archive(path)
	rtd.counter_user[user_id] += 1
	bot.send_message(user_id, "Keep sending images or click on the 'Done' button",
					reply_markup=markup)
	rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_IMAGE)])




@bot.message_handler(func = lambda msg:
				rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_IMAGE_LOOP), 
				content_types=['photo', 'text'])
def add_word12(msg):
	"""
		Add word: Send images sequence -> Receive Done command or more images
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.LOCKED)
	if msg.text == "Done":
		card = rtd.temp_user[user_id].pop()
		rtd.temp_user[user_id][0].set_card(card)
		markup = telebot.types.ReplyKeyboardRemove()
		print(str(rtd.temp_user[user_id][0]))
		back_to_relate_menu(msg)
		return
	elif msg.photo != None:
		filename = rtd.temp_user[user_id][1].card_id
		path = utils.save_image(msg,
								"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
								"{}_{}".format(filename,rtd.counter_user[user_id]), 
								bot)

		print(path)
		rtd.temp_user[user_id][1].add_archive(path)
		rtd.counter_user[user_id] += 1
		bot.send_message(user_id, "Keep sending images or click on the 'Done' button")
		rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_IMAGE_LOOP)])


#=====================SET STATE=====================

@bot.message_handler(commands = ['set_state'])
def set_state(msg):
	"""
		Used for debug only. Set user state
	"""
	user_id = get_id(msg)
	rtd.set_state(user_id, fsm.IDLE)
	'''
	rtd.set_state(user_id, fsm.LOCKED)
	number = msg.text[11:]
	if len(number) == 0:
		bot.sent_message(user_id, "don't forget the new state")
		return 0
	print("new state:{}".format(int(number)))
	print("id:{} state:{}".format(user_id, rtd.get_state(user_id)))
	rtd.set_state(user_id, str(int(number)))
	'''
#=====================SETTINGS=====================


@bot.message_handler(func = lambda msg: 
			rtd.get_state(get_id(msg)) == fsm.IDLE, 
			commands = ['settings'])
def set_settings(msg):
	"""
		Change setting sequence
	"""
	return 0


#=====================MESSAGE NOT UNDERSTOOD=====================

@bot.message_handler(func = lambda msg: True)
def set_settings(msg):
	"""
		Change setting sequence
	"""
	user_id = get_id(msg)

	bot.send_message(user_id, "Oops, didn't understand your message")
	return 0



#while True:
#	try:
print("Press Ctrl+C to exit gently")
print("Bot Polling!!!")
try:
	bot.polling(none_stop=True)
except Exception as e:
	bot.send_message(359999978,"Bot Crashed!!")
	print(e)
#	except Exception as e:
#		print("An error ocurred with bot.polling")
#		print(e)
#		time.sleep(5)	

