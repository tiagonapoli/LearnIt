import telebot
import fsm
import utils
import bot_utils
import message_handlers.add_word_audio
import message_handlers.add_word_translation
import message_handlers.add_word_images
from flashcard import Word, Card
from bot_utils import get_id
from queue import Queue

def prepare_to_receive(bot, user_id, content_type):
	"""
		Add word: User just chose to send some content type
	"""
	content_type_aux = content_type[5:]
	print("content type = {}".format(content_type_aux))

	article = 'an'
	if content_type_aux == 'translation':
		article = 'a'

	bot.send_message(user_id,"Send {} {}:".format(article, content_type_aux))
	if content_type_aux == 'image':
		bot.send_message(user_id, "Use @pic <image_name> or @bing <image_name> to select an image")

def save_word(bot, rtd, user_id):
	word = rtd.temp_user[user_id][0]
	rtd.add_word(word)
	bot.send_message(user_id, "Successfully done!")

def handle_add_word(bot, rtd):



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
		
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "Please, add a language first.")
			rtd.set_state(user_id, fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)

		text = "Please select the word's language:\n" + bot_utils.create_string_keyboard(known_languages)

		bot.send_message(user_id, text, reply_markup=markup)
		rtd.temp_user[user_id] = known_languages
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
		known_languages = rtd.temp_user[user_id]
		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, known_languages)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "Send the word's topic, either a new topic or select from existing".format(language),
						reply_markup=markup)
		topics = rtd.get_all_topics(user_id, language)
		topics.sort()

		if len(topics) > 0:
			markup = bot_utils.create_keyboard(topics, 3)
			text = "Topics registered:\n" + bot_utils.create_string_keyboard(topics)
			bot.send_message(user_id, text, reply_markup=markup)
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
		
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, rtd.temp_user[user_id][1])

		markup = bot_utils.keyboard_remove()
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

		word_text = utils.treat_special_chars(msg.text)
		rtd.temp_user[user_id][0].foreign_word = word_text

		word = rtd.temp_user[user_id][0]
		default_card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word, rtd.get_highest_card_id(user_id) + 1, 'default')
		default_card.add_archive(default_card.foreign_word)
		rtd.temp_user[user_id][0].set_card(default_card)

		options = ['Send image', 'Send audio', 'Send translation']
		btn = bot_utils.create_inline_keys_sequential(options)
		btn_set = set()
		markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ('End selection', 'DONE'))

		rtd.temp_user[user_id].append(btn_set)
		rtd.temp_user[user_id].append(btn)

		bot.send_message(user_id, "Select the ways you want to relate to the word:",
						reply_markup=markup)	
		rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)])

	@bot.callback_query_handler(func=lambda call:
							rtd.get_state(get_id(call.message)) == (fsm.ADD_WORD, fsm.RELATE_MENU))

	def callback_select_words(call):
		""" 
			Add word: Create relate menu 
		"""
		user_id = get_id(call.message)
		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))

		btn_set = rtd.temp_user[user_id][2]
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = rtd.temp_user[user_id][3]
		
		if done == True:
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			rtd.receive_queue[user_id] = Queue()
			for i in btn_set:
				rtd.receive_queue[user_id].put(btn[i][0])

			if rtd.receive_queue[user_id].empty():
				save_word(bot, rtd, user_id)
				rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['done'])
			else:
				content_type = rtd.receive_queue[user_id].get()
				prepare_to_receive(bot, user_id, content_type)
				rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)][content_type])
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select words to erase:", reply_markup=markup)
			rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['continue'])


	
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.RELATE_MENU))
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



	message_handlers.add_word_audio.handle_add_word_audio(bot, rtd)

	message_handlers.add_word_translation.handle_add_word_translation(bot, rtd)

	message_handlers.add_word_images.handle_add_word_images(bot, rtd)