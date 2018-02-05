import telebot
import fsm
import utils
from flashcard import Word, Card
from bot_utils import get_id, create_key_button


def handle_add_word(bot, rtd):	

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
		language = utils.treat_special_chars(msg.text)
		if not (language in known_languages):
			bot.reply_to(msg, "Please choose from keyboard")
			rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['error'])
			return

		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id, "Send the word's topic, either a new topic or select from existing".format(language),
						reply_markup=markup)
		topics = rtd.get_all_topics(user_id, language)
		topics.sort()

		if len(topics) > 0:

			btn = []
			for topic in topics:
				btn.append(create_key_button(topic))

			markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

			for i in range(0,len(btn)//3):
				markup.row(btn[3*i], btn[3*i+1], btn[3*i+2])

			if len(btn)%3 == 2:
				markup.row(btn[len(btn)-2],btn[len(btn)-1])

			if len(btn)%3 == 1:
				markup.row(btn[len(btn)-1])

			str = "Topics registered:\n"
			aux_cnt = 1
			for topic in topics:
				str += "/{}. ".format(aux_cnt) + topic + '\n'
				aux_cnt += 1
			bot.send_message(user_id, str, reply_markup=markup)
		else: 
			bot.send_message(user_id, "There are no topics registered in this language yet.")
		rtd.temp_user[user_id] = []
		rtd.temp_user[user_id].append(Word(user_id, rtd.get_highest_word_id(user_id) + 1))
		rtd.temp_user[user_id][0].language = language
		rtd.temp_user[user_id].append(topics)
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
		
		valid, topic = utils.parse_option(msg.text.strip(), rtd.temp_user[user_id][1])
		if valid == False:
			topic = utils.treat_special_chars(msg.text)

		markup = telebot.types.ReplyKeyboardRemove()
		rtd.temp_user[user_id][0].topic = topic
		bot.send_message(user_id, "Word's topic: {}".format(topic))
		bot.send_message(user_id, "Send word to add (in {})".format(language), reply_markup=markup)
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

		word = utils.treat_special_chars(msg.text)
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
		
		translation = utils.treat_special_chars(msg.text)
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
			translation = utils.treat_special_chars(msg.text)
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
