import fsm
from utilities.bot_utils import get_id
from random import shuffle
import logging
import translation

def handle_select_training(bot, user_manager, debug_mode):

	#=====================SELECT_TRAINING=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['select_training'])
	def review(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		known_subjects = user.get_subjects()
		options = []
		for subject in known_subjects:
			options.append(subject[0])
		
		if len(options) == 0:
			user.send_message("#no_subjects")
			user.set_state(fsm.IDLE)
			return 	

		markdown_options = ["*"] * len(options)
		user.send_string_keyboard("#subject_selection", options, markdown_options=markdown_options)
		user.set_state(fsm.next_state[fsm.IDLE]['select_training'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.SELECT_TRAINING, fsm.GET_SUBJECT),
					content_types=['text'])
	def review1(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.SELECT_TRAINING, fsm.GET_SUBJECT)]['error'])
			return

		user.temp_subject = subject
		
		known_topics = user.get_topics(subject)
		topics = []
		for topic in known_topics:
			topics.append(topic[0])
		topics.sort()

		topic_pos = {}
		cnt = 0
		for topic in topics:
			topic_pos[topic] = cnt
			cnt += 1

		selected = set()
		active_topics = user.get_active_topics(subject)
		for topic in active_topics:
			selected.add(topic_pos[topic])

		user.send_selection_inline_keyboard("#select_training_select_topics", topics, btn_set=selected)
		user.set_state(fsm.next_state[(fsm.SELECT_TRAINING, fsm.GET_SUBJECT)]['done'])


	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.SELECT_TRAINING, fsm.GET_TOPICS))

	def callback_select_words(call):

		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)

		if done == True:
			subject = user.temp_subject
			user.set_subject_active(subject, 0)
			txt = translation.translate("#active_topics_listing", user.get_native_language()) + "\n"
			txt_args = (subject, )
			for i in btn_set:
				user.set_topic_active(subject, btn[i][0], 1)
				txt += "*.%s*"
				txt_args += (btn[i][0], )
			if len(txt_args) == 1:
				txt += translation.translate("#no_active_topics", user.get_native_language())
			user.send_message(txt, txt_args=txt_args, translate_flag=False)
			user.set_state(fsm.next_state[(fsm.SELECT_TRAINING, fsm.GET_TOPICS)]['done'])
		else:
			user.set_state(fsm.next_state[(fsm.SELECT_TRAINING, fsm.GET_TOPICS)]['continue'])

