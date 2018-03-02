import fsm
import message_handlers.add_word_audio
import message_handlers.add_word_text
import message_handlers.add_word_images
from utilities import utils
from utilities import bot_utils
from flashcard import Word, Card
from utilities.bot_utils import get_id
from queue import Queue
import logging

def prepare_to_receive(bot, user, content_type):
	"""
		Add word: User just chose to send some content type
	"""
	user_id = user.get_id()
	content_type_aux = content_type[5:]
	print("content type = {}".format(content_type_aux))

	article = 'an'
	if content_type_aux == 'text':
		article = 'a'

	bot.send_message(user_id,"Send {} *{}*:".format(article, content_type_aux), parse_mode="Markdown")
	if content_type_aux == 'image':
		bot.send_message(user_id, "_Use_ @pic _<image_\__name> or_ @bing _<image_\__name> to select an image_", parse_mode="Markdown")
	if content_type_aux == 'audio':
		bot.send_message(user_id, "_Hint: You can download pronunciations on forvo.com and then send them to me. This process is way easier on PC (Telegram Desktop)_", parse_mode="Markdown")

def save_word(bot, user):
	word = user.temp_word
	user.add_word(word)
	bot.send_message(user.get_id(), "_Successfully done!_", parse_mode="Markdown")

def handle_add_word(bot, rtd, debug_mode):



	#=====================ADD WORD=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['add_word'])
	def add_word(msg):
		"""
			Add word: Get word sequence
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		known_languages = user.get_languages()
		
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "_Please, add a language first._", parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)

		bot.send_message(user_id, "_Hint: The process to add a word is way easier on Telegram Desktop_", parse_mode="Markdown")

		text = "*Please select the word's language:*\n" + bot_utils.create_string_keyboard(known_languages)

		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		user.keyboard_options = known_languages
		user.set_state(fsm.next_state[fsm.IDLE]['add_word'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.GET_LANGUAGE),
					content_types=['text'])
	def add_word1(msg):
		"""
			Add word: Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "*Send the word's topic*. You can send a *new topic* or *select from existing*",
						reply_markup=markup, parse_mode="Markdown")
		topics = user.get_all_topics(language)
		topics.sort()

		if len(topics) > 0:
			markup = bot_utils.create_keyboard(topics, 3)
			text = "_Topics registered:_\n" + bot_utils.create_string_keyboard(topics)
			bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		else: 
			bot.send_message(user_id, "_There are no topics registered in this language yet, so please_ *send a new topic*", parse_mode="Markdown")
		
		user.temp_word = Word(user_id, user.get_highest_word_id() + 1)
		user.temp_word.language = language
		user.keyboard_options = topics 
		user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['done'])



	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.GET_TOPIC), 
					content_types=['text'])
	def add_word2(msg):
		"""
			Add word: Get topic
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		language = user.temp_word.get_language()
		
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if len(topic) >= 45:
			bot.send_message(user_id, "Please, don't exceed 45 characters. You digited {} characters. Send the topic again:".format(len(topic)))
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_TOPIC)]['error'])
			return

		if len(topic) == 0:
			bot.send_message(user_id, "Please, don't user / or \ or _ or *. Send the topic again:")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_TOPIC)]['error'])
			return


		markup = bot_utils.keyboard_remove()
		user.temp_word.topic = topic
		bot.send_message(user_id, "Word's topic: *{}*".format(utils.treat_msg_to_send(topic, "*")), parse_mode="Markdown")
		bot.send_message(user_id, "*Send word to add* (in _{}_)".format(utils.treat_msg_to_send(language, "_")), reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_TOPIC)]['done'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.GET_WORD), 
					content_types=['text'])
	def add_word3(msg):
		"""
			Add word: Get foreign word
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		word_text = utils.treat_special_chars(msg.text)
		if len(word_text) >= 190:
			bot.send_message(user_id, "Please, don't exceed 190 characters. You digited {} characters. Send the word again:".format(len(word_text)))
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)]['error'])
			return

		if len(word_text) == 0:
			bot.send_message(user_id, "Please, don't user / or \ or _ or *. Send the word again:")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)]['error'])
			return

		if word_text == "&img":
			bot.send_message(user_id, "_Please,_ *send an image* _to use instead of a word:_", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)]['word img'])
			return

		user.temp_word.foreign_word = word_text

		word = user.temp_word

		exist, aux_word_id = user.check_word_existence(word.language, word.topic, word.foreign_word)
		if exist == True:
			bot.send_message(user_id, "This word is already registered, if you want to add it anyway, please, erase it first. The process will be canceled")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)]['error_idle'])
			return


		options = ['Send image', 'Send audio', 'Send text']
		btn = bot_utils.create_inline_keys_sequential(options)
		btn_set = set()
		markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ('End selection', 'DONE'))

		user.btn_set = btn_set
		user.keyboard_options = btn

		bot.send_message(user_id, "_Select the ways you want to relate to the word (one or more):_",
						reply_markup=markup, parse_mode="Markdown")	
		user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_WORD)]['done'])


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.GET_IMAGE), 
					content_types=['photo'])
	def add_word4(msg):
		"""
			Add word: Get foreign word
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))
		word = user.temp_word

		filename = "{}_{}".format(user_id, word.get_word_id())
		path = utils.save_image(msg,
								"../data/special/", 
								filename, 
								bot)

		user.temp_word.foreign_word = '&img ' + path

		options = ['Send text']
		btn = bot_utils.create_inline_keys_sequential(options)
		btn_set = set()
		markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ('End selection', 'DONE'))

		user.btn_set = btn_set
		user.keyboard_options = btn

		bot.send_message(user_id, "_Select the ways you want to relate to the word (one or more):_",
						reply_markup=markup, parse_mode="Markdown")	
		user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_IMAGE)]['done'])


	@bot.callback_query_handler(func=lambda call:
							rtd.get_user(get_id(call.message)).get_state() == (fsm.ADD_WORD, fsm.RELATE_MENU))

	def callback_select_words(call):
		""" 
			Add word: Create relate menu 
		"""
		user = rtd.get_user(get_id(call.message))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))

		btn_set = user.btn_set
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = user.keyboard_options
		
		if done == True:
			user.receive_queue = Queue()
			for i in btn_set:
				user.receive_queue.put(btn[i][0])

			if user.receive_queue.empty() == True:
				markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
				try:
					bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Please, select *at least one way* to relate to the word: ", 
							reply_markup=markup, parse_mode="Markdown")
				except Exception as e:
					print("CANT EDIT MESSAGE")
					
				user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['continue'])
			else:
				bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
				content_type = user.receive_queue.get()
				prepare_to_receive(bot, user, content_type)
				user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)][content_type])
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="_Select the ways you want to relate to the word (one or more):_", 
							reply_markup=markup, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.RELATE_MENU)]['continue'])


	#=================GET AUDIO=================
	message_handlers.add_word_audio.handle_add_word_audio(bot, rtd, debug_mode)

	#=================GET TEXT=================
	message_handlers.add_word_text.handle_add_word_text(bot, rtd, debug_mode)

	#=================GET IMAGES=================
	message_handlers.add_word_images.handle_add_word_images(bot, rtd, debug_mode)
	
	
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.GET_CONTINUE), 
					content_types=['text'])
	def add_word5(msg):

		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		valid, should_continue = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_CONTINUE)]['error'])
			return
			
		if should_continue == 'No':
			markup = bot_utils.keyboard_remove()
			bot.send_message(user.get_id(), "_OK!_",reply_markup=markup, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_CONTINUE)]['done'])
			return

		word =	user.temp_word
		language = word.get_language()
		topic = word.get_topic()

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "Word's topic: *{}*".format(utils.treat_msg_to_send(topic, "*")), reply_markup=markup, parse_mode="Markdown")
		bot.send_message(user_id, "*Send word to add* (in _{}_)".format(utils.treat_msg_to_send(language, "_")), parse_mode="Markdown")

		user.temp_word = Word(user_id, user.get_highest_word_id() + 1)
		user.temp_word.language = language
		user.temp_word.topic = topic
		
		user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_CONTINUE)]['continue'])
