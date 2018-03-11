import fsm

import message_handlers.add_item_audio
import message_handlers.add_item_text
import message_handlers.add_item_image


from utilities import string_treating, bot_utils
from Flashcard import StudyItemDeck, Card
from utilities.bot_utils import get_id
from queue import Queue
import logging



import sys
def prepare_to_receive(user, content_type):
	user_id = user.get_id()
	if content_type == '1':
		user.send_message("#ask_to_send_image")
		user.send_message("#send_image_hint")
	elif content_type == '2':
		user.send_message("#ask_to_send_audio")
		user.send_message("#send_audio_hint")
	elif content_type == '0':
		user.send_message("#ask_to_send_text")

def save_word(user):
	study_item_deck = user.temp_study_item
	subject = study_item_deck.subject
	topic = study_item_deck.topic

	active_topic = user.is_topic_active(subject, topic)
	active_subject = user.is_subject_active(subject)
	active_item = 0
	if active_topic == None and active_subject == None:
		active_item = 1
	elif active_topic == None and active_subject != None and active_subject > 0:
		active_item = 1
	elif active_topic != None and active_subject != None and active_topic > 0 and active_subject > 0:
		active_item = 1

	study_item_deck.active = active_item
	for key in study_item_deck.cards.keys():
		study_item_deck.cards[key].active = active_item

	user.add_study_item_deck(study_item_deck)
	if active_item:
		user.send_message("#add_item_active_success")
	else:
		user.send_message("#add_item_unactive_success")
		


def handle_add_item(bot, user_manager, debug_mode):

	#=====================ADD WORD=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['add_item'])
	def ADD_ITEM(msg):
		"""
			Add word: Get word sequence
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		known_subjects = user.get_subjects()
		options = []
		for option in known_subjects:
			options.append(option[0])

		user.send_message("#add_item_initial_hint")
		user.send_message("#add_item_subject_intro")
		if len(known_subjects) == 0:
			user.send_string_keyboard("#add_item_no_subjects", options)
		else:
			user.send_string_keyboard("#list_subjects", options)		
		user.set_state(fsm.next_state[fsm.IDLE]['add_item'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.GET_SUBJECT),
					content_types=['text'])
	def ADD_ITEM1(msg):
		"""
			Add word: Get word's language
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		user.send_message("#item_subject", (subject,))
		user.send_message("#add_item_topic_intro")

		known_topics = user.get_topics(subject)
		topics = []
		for topic in known_topics:
			topics.append(topic[0])
		topics.sort()

		if len(topics) > 0:
			user.send_string_keyboard("#list_topics", topics)
		else: 
			user.send_string_keyboard("#add_item_no_topics", topics)
		user.temp_study_item = StudyItemDeck(user_id, user.get_highest_study_item_id() + 1, 0, subject)
		user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_SUBJECT)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.GET_TOPIC), 
					content_types=['text'])
	def ADD_ITEM2(msg):
		"""
			Add word: Get topic
		"""
		
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger
		
		valid, topic, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if len(topic) >= 45:
			user.send_message("#character_exceeded", (45, len(topic)))
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_TOPIC)]['error'])
			return

		if len(topic) == 0:
			user.send_message("#character_null")
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_TOPIC)]['error'])
			return

		subject = user.temp_study_item.subject
		user.temp_study_item.topic = topic
		user.send_message("#item_topic", (topic,)) 
		user.send_message("#add_item_ask_study_item", (subject, )) 
		user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_TOPIC)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.GET_STUDY_ITEM), 
					content_types=['text'])
	def ADD_ITEM3(msg):
		"""
			Add word: Get foreign word
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		study_item_text = string_treating.treat_special_chars(msg.text)
		if len(study_item_text) >= 190:
			user.send_message("#character_exceeded", (190, len(study_item_text)))
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_STUDY_ITEM)]['error'])
			return

		if len(study_item_text) == 0:
			user.send_message("#character_null")
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_STUDY_ITEM)]['error'])
			return

		if study_item_text == "&img":
			user.send_message("#add_item_get_study_item_1"), 
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_STUDY_ITEM)]['study item 1'])
			return

		user.temp_study_item.set_study_item(study_item_text, 0)
		study_item_deck = user.temp_study_item

		exist, aux_study_item_id = user.check_study_item_existence(study_item_deck.subject, study_item_deck.topic, study_item_deck.study_item)
		if exist == True:
			user.send_message("#add_item_study_item_already_exists")
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_STUDY_ITEM)]['error_idle'])
			return


		options = ['Send text',
				   'Send image', 
				   'Send audio']

		user.send_selection_inline_keyboard("#add_item_relate_menu", options, 
			translate_options=True, empty_keyboard_text="#add_item_relate_menu_empty", no_empty_flag=True)
		user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_STUDY_ITEM)]['done'])

	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.GET_IMAGE), 
					content_types=['photo'])
	def ADD_ITEM4(msg):
		"""
			Add word: Get foreign word
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger
		
		study_item_deck = user.temp_study_item

		filename = "study_item"
		if debug_mode:
			debug_mode_text = "_debug"
		else:
			debug_mode_text = ""
		path = user.save_image(msg,
								"../data{}/{}/{}/".format(debug_mode_text, user_id, study_item_deck.study_item_id), 
								filename)

		user.temp_study_item.set_study_item(path, 1)

		options = ['Send text']
		user.send_selection_inline_keyboard("#add_item_relate_menu", options, 
			translate_options=True, empty_keyboard_text="#add_item_relate_menu_empty", no_empty_flag=True)
		user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_IMAGE)]['done'])


	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.ADD_ITEM, fsm.RELATE_MENU))

	def callback_select_words(call):

		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)
		
		if done == True:
			user.receive_queue = Queue()
			for i in btn_set:
				user.receive_queue.put(btn[i][1])					
			content_type = user.receive_queue.get()
			prepare_to_receive(user, content_type)
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.RELATE_MENU)][content_type])
		else:
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.RELATE_MENU)]['continue'])

	
	#=================GET AUDIO=================
	message_handlers.add_item_audio.handle_add_item_audio(bot, user_manager, debug_mode)

	#=================GET TEXT=================
	message_handlers.add_item_text.handle_add_item_text(bot, user_manager, debug_mode)

	#=================GET IMAGES=================
	message_handlers.add_item_image.handle_add_item_image(bot, user_manager, debug_mode)
	
	
	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.GET_CONTINUE), 
					content_types=['text'])
	def ADD_ITEM5(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, should_continue, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)
		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_CONTINUE)]['error'])
			return
			
		if keyboard_option == 1:
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_CONTINUE)]['done'])
			return

		study_item = user.temp_study_item
		subject = study_item.get_subject()
		topic = study_item.get_topic()

		user.send_message("#item_topic", (topic, )) 
		user.send_message("#add_item_ask_study_item", (subject, )) 

		user.temp_study_item = StudyItemDeck(user_id, user.get_highest_study_item_id() + 1, 0, subject)
		user.temp_study_item.topic = topic
		
		user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.GET_CONTINUE)]['continue'])
