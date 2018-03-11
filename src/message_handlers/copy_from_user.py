import fsm
from utilities.bot_utils import get_id
from utilities import string_treating
import translation
import logging


def handle_copy_from_user(bot, user_manager, debug_mode):

	#=====================ADD WORD=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['copy_from_user'])
	def copy_from_user(msg):
		"""
			Copy words from user
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		user.send_message("#copy_get_telegram_username") 
		user.set_state(fsm.next_state[fsm.IDLE]['copy_from_user'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.COPY_FROM_USER, fsm.GET_USER),
					content_types=['text'])
	def get_user(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		username = string_treating.treat_username_str(msg.text)
		valid, user2 = user_manager.get_user_by_username(username)
		user.temp_user = user2

		if valid == False:
			user.send_message("#invalid_username")
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_USER)]['error'])
			return

		if user.get_id() == user2.get_id():
			user.send_message("#invalid_yourself_username")
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_USER)]['error'])
			return

		public = user2.get_public()

		if public == False:
			user.send_message("#invalid_private_username")
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_USER)]['error'])
			return

		options = user2.get_only_subjects()
		
		if len(options) == 0:
			user.send_message("#copy_no_subjects", (user2.get_username(), ))
			user.set_state(fsm.IDLE)
			return

		user.send_string_keyboard("#subject_selection", options)
		user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_USER)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.COPY_FROM_USER, fsm.GET_SUBJECT), 
					content_types=['text'])
	def get_languages(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_SUBJECT)]['error'])
			return

		user.temp_subject = subject

		topics = user.temp_user.get_only_topics(subject)
		topics.sort()

		user.send_selection_inline_keyboard("#copy_select_topics", topics)
		user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_SUBJECT)]['done'])
	


	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.COPY_FROM_USER, fsm.SELECT_TOPICS))

	def callback_select_words(call):
		
		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)
		
		if done == True:
			user.btn_set = btn_set
			user.temp_topics_list = []
			for i in btn_set:
				user.temp_topics_list.append(btn[i][0])

			options = ['Yes', 'No']
			user.send_string_keyboard("#ask_overwrite", options, translate_options=True)
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.SELECT_TOPICS)]['done'])
		else:
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.SELECT_TOPICS)]['continue'])



	@bot.message_handler(func = lambda msg:
			user_manager.get_user(get_id(msg)).get_state() == (fsm.COPY_FROM_USER, fsm.GET_OVERWRITE), 
			content_types=['text'])
	def overwrite_check(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, overwrite, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_OVERWRITE)]['error'])
			return

		if keyboard_option == 0:
			overwrite = True
		else:
			overwrite = False
		
		selected_topics = user.temp_topics_list
		text = translation.translate('#copy_results', user.get_native_language()) + "\n"
		user.send_message(text, translate_flag=False)

		count = 0
		for topic in selected_topics:
			txt_args = ()
			text = ""
			copied, overwritten_items = user_manager.copy_topic(user, user.temp_user, user.temp_subject, topic, overwrite)
			text += translation.translate('#topic', user.get_native_language()) + "\n"
			txt_args += (topic, ) 
			if len(overwritten_items) > 0:
				text += translation.translate('#overwritten_items', user.get_native_language()) + "\n"
				count += 1
				for item in overwritten_items:
					text += '_.%s_\n'
					txt_args += (item, )

			if len(copied) > 0:
				text += translation.translate('#copied_items', user.get_native_language()) + "\n"
				count += 1
				for item in copied:
					text += '_.%s_\n'
					txt_args += (item, )
			
			print(text)
			user.send_message(text, txt_args, translate_flag=False)


		user.set_state(fsm.next_state[(fsm.COPY_FROM_USER, fsm.GET_OVERWRITE)]['done'])