import fsm
from utilities import utils
from utilities.bot_utils import get_id
import translation
import logging



def handle_erase(bot, user_manager, debug_mode):	

	#=====================ERASE WORDS=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['erase'])
	def erase_words(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		known_subjects = user.get_only_subjects()
		if len(known_subjects) == 0:
			user.send_message("#no_subjects")
			user.set_state(fsm.IDLE)
			return

		options = ['Subjects', 'Topics', 'Study Items']
		user.send_string_keyboard("#ask_what_to_erase", options, translate_options=True) 
		user.set_state(fsm.next_state[fsm.IDLE]['erase'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ERASE, fsm.GET_OPTION),
					content_types=['text'])
	def erase_words(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_options")
			user.set_state(fsm.next_state[(fsm.ERASE, fsm.GET_OPTION)]['error'])
			return

		known_subjects = user.get_only_subjects()
		if keyboard_option == 0:
			user.send_selection_inline_keyboard("#erase_select_subjects", known_subjects)
			user.set_state(fsm.next_state[(fsm.ERASE, fsm.GET_OPTION)]['subject'])
		elif keyboard_option == 1:
			user.send_string_keyboard("#subject_selection", known_subjects)
			user.set_state(fsm.next_state[(fsm.ERASE, fsm.GET_OPTION)]['topic'])
		elif keyboard_option == 2:
			user.send_string_keyboard("#subject_selection", known_subjects)
			user.set_state(fsm.next_state[(fsm.ERASE, fsm.GET_OPTION)]['study_item'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.TOPIC_ERASE, fsm.GET_SUBJECT),
					content_types=['text'])
	def erase_words1(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)
		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.TOPIC_ERASE, fsm.GET_SUBJECT)]['error'])
			return

		user.temp_subject = subject
		topics = user.get_only_topics(subject)
		topics.sort()
		user.send_selection_inline_keyboard("#erase_select_topics", topics)
		user.set_state(fsm.next_state[(fsm.TOPIC_ERASE, fsm.GET_SUBJECT)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ITEM_ERASE, fsm.GET_SUBJECT),
					content_types=['text'])
	def erase_words1(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)
		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.GET_SUBJECT)]['error'])
			return

		user.temp_subject = subject
		topics = user.get_only_topics(subject)
		topics.sort()
		user.send_string_keyboard("#topic_selection", topics)
		user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.GET_SUBJECT)]['done'])




	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ITEM_ERASE, fsm.GET_TOPIC), 
					content_types=['text'])
	def erase_words2(msg):

		user = user_manager.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))

		valid, topic, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)
		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.GET_TOPIC)]['error'])
			return			

		subject = user.temp_subject
		study_items = user.get_study_items_on_topic(subject, topic)
		user.temp_study_items_list = study_items
		study_items_string_list = utils.study_items_to_string_list(study_items)
		
		user.send_selection_inline_keyboard("#erase_select_study_items", study_items_string_list)
		user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.GET_TOPIC)]['done'])




	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.SUBJECT_ERASE, fsm.SELECT))

	def callback_select_words(call):
		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)
		
		if done == True:
			text = translation.translate("#subjects_erased", user.get_native_language()) + "\n"
			txt_args = ()
			for i in btn_set:
				user.erase_subject(btn[i][0])
				text += "*.%s*\n"
				txt_args += (btn[i][0], )
			user.send_message(text, txt_args, translate_flag=False)
			user.set_state(fsm.next_state[(fsm.SUBJECT_ERASE, fsm.SELECT)]['done'])		
		else:
			user.set_state(fsm.next_state[(fsm.SUBJECT_ERASE, fsm.SELECT)]['continue'])

	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.ITEM_ERASE, fsm.SELECT))

	def callback_select_words(call):
		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)
		
		if done == True:
			study_items = user.temp_study_items_list
			text = translation.translate("#items_erased", user.get_native_language()) + "\n"
			txt_args = ()
			for i in btn_set:
				user.erase_study_item(study_items[i].get_study_item_id())
				text += "*.%s*\n"
				txt_args += (study_items[i].get_sendable_study_item(), )
			user.send_message(text, txt_args, translate_flag=False)
			user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.SELECT)]['done'])		
		else:
			user.set_state(fsm.next_state[(fsm.ITEM_ERASE, fsm.SELECT)]['continue'])


	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.TOPIC_ERASE, fsm.SELECT))

	def callback_select_words(call):
		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)
		
		if done == True:
			text = translation.translate("#topics_erased", user.get_native_language()) + "\n"
			txt_args = ()
			for i in btn_set:
				user.erase_topic(user.temp_subject, btn[i][0])
				text += "*.%s*\n"
				txt_args += (btn[i][0], )
			user.send_message(text, txt_args, translate_flag=False)
			user.set_state(fsm.next_state[(fsm.TOPIC_ERASE, fsm.SELECT)]['done'])		
		else:
			user.set_state(fsm.next_state[(fsm.TOPIC_ERASE, fsm.SELECT)]['continue'])


