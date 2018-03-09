import fsm
from flashcard import Word
from utilities.bot_utils import get_id
from utilities import utils
from utilities import bot_utils
import logging



def handle_list(bot, user_manager, debug_mode):	

	#=====================LIST WORDS=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['list'])
	def list_words(msg):
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		options = user.get_active_subjects()

		if len(options) == 0:
			user.send_message("#no_active_subjects")
			user.set_state(fsm.IDLE)
			return

		user.send_navigation_string_keyboard("#list_subject_selection", end_btn="End selection", txt_args=(len(options)+1,))
		user.set_state(fsm.next_state[fsm.IDLE]['list'])



	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.LIST, fsm.GET_SUBJECT),
					content_types=['text'])
	def list_words1(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		operation, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		print(operation, subject, keyboard_option, keyboard_len)

		if operation == 'Error':
			user.send_message("#choose_from_keyboard")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_SUBJECT)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_SUBJECT)][operation])
			return

		topics = user.get_active_topics(subject)
		topics.sort()
		user.send_navigation_string_keyboard("#list_topic_selection", end_btn="End selection", back_btn="Go back", txt_args=(len(topics)+1, len(topics)+2))


		user.temp_study_item = StudyItemDeck(user_id, None, None)
		user.temp_study_item.subject = subject
		user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_SUBJECT)][operation])
	


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.LIST, fsm.GET_TOPIC), 
					content_types=['text'])
	def list_words2(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		operation, topic, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if operation == 'Error':
			user.send_message("#choose_from_keyboard")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return

		if operation == 'Back':
			options = user.get_active_subjects()
			user.send_navigation_string_keyboard("#list_subject_selection", end_btn="End selection", txt_args=(len(options)+1,))
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return


		subject = user.temp_study_item.get_subject()
		study_items = user.get_study_items_on_topic(subject, topic)
		user.temp_study_items_list = study_items
		study_items_string = utils.study_items_to_string_list(study_items)

		user.send_navigation_string_keyboard("#list_study_item_selection", 
			end_btn="End selection", back_btn="Go back", txt_args=(len(study_items_string)+1, len(study_items_string)+2))
		user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.LIST, fsm.GET_STUDY_ITEM), 
					content_types=['text'])
	def list_words3(msg):
		"""
			Get topic
		"""
		
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		operation, topic, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if operation == 'Error':
			user.send_message("#choose_from_keyboard")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		if operation == 'Back':
			topics = user.get_active_topics(subject)
			topics.sort()
			user.send_navigation_string_keyboard("#list_topic_selection", end_btn="End selection", back_btn="Go back", txt_args=(len(topics)+1, len(topics)+2))
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		user.send_message("#study_item")
		user.send_all_cards(user.temp_study_items_list[option])
		
		user.send_navigation_string_keyboard("#list_study_item_selection", 
			end_btn="End selection", back_btn="Go back", txt_args=(len(study_items_string)+1, len(study_items_string)+2))
		user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_WORD)]['continue'])
