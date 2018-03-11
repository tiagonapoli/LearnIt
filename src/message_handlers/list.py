import fsm
from Flashcard import StudyItemDeck
from utilities.bot_utils import get_id
from utilities import utils
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

		markdown_options = ["_"] * len(options) + ["*"]
		user.send_navigation_string_keyboard("#list_subject_selection", options=options, markdown_options=markdown_options, 
			end_btn="End selection")
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

		if operation == 'Error':
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_SUBJECT)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_SUBJECT)][operation])
			return

		topics = user.get_active_topics(subject)
		topics.sort()
		markdown_options = ["_"] * len(topics) + ["*", "*"]
		user.send_navigation_string_keyboard("#list_topic_selection", options=topics, markdown_options=markdown_options, 
			end_btn="End selection", back_btn="Go back")


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
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return

		if operation == 'Back':
			options = user.get_active_subjects()
			markdown_options = ["_"] * len(options) + ["*"]
			user.send_navigation_string_keyboard("#list_subject_selection", options=options, markdown_options=markdown_options, 
				end_btn="End selection")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_TOPIC)][operation])
			return


		subject = user.temp_study_item.get_subject()
		study_items = user.get_study_items_on_topic(subject, topic)
		user.temp_study_items_list = study_items
		user.temp_study_items_string_list = utils.study_items_to_string_list(study_items)

		markdown_options = ["_"] * len(user.temp_study_items_string_list) + ['*', '*']
		user.send_navigation_string_keyboard("#list_study_item_selection", options=user.temp_study_items_string_list, markdown_options=markdown_options,
			end_btn="End selection", back_btn="Go back")
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

		operation, option, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if operation == 'Error':
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		if operation == 'Back':
			subject = user.temp_study_items_list[0].get_subject()
			topics = user.get_active_topics(subject)
			topics.sort()
			markdown_options = ["_"] * len(topics) + ["*", "*"]
			user.send_navigation_string_keyboard("#list_topic_selection", options=topics, markdown_options=markdown_options, 
				end_btn="End selection", back_btn="Go back")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		if operation == 'End':
			user.send_message("#ok")
			user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
			return

		user.send_message("#study_item", (user.temp_study_items_list[keyboard_option].get_sendable_study_item(),))
		user.send_all_cards(user.temp_study_items_list[keyboard_option])
		
		markdown_options = ["_"] * len(user.temp_study_items_string_list) + ['*', '*']
		user.send_navigation_string_keyboard("#list_study_item_selection", options=user.temp_study_items_string_list, markdown_options=markdown_options,
			end_btn="End selection", back_btn="Go back")
		user.set_state(fsm.next_state[(fsm.LIST, fsm.GET_STUDY_ITEM)][operation])
