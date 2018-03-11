import fsm
from utilities.bot_utils import get_id
from random import shuffle
from utilities import utils
import logging

def handle_topic_review(bot, user_manager, debug_mode):

	#=====================TOPIC REVIEW=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['review'])
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
		user.set_state(fsm.next_state[fsm.IDLE]['review'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.GET_SUBJECT),
					content_types=['text'])
	def review1(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, subject, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_SUBJECT)]['error'])
			return

		user.temp_subject = subject
		known_topics = user.get_topics(subject)
		topics = []
		for topic in known_topics:
			topics.append(topic[0])
		topics.sort()

		user.send_selection_inline_keyboard("#review_select_topics", topics,
			empty_keyboard_text="#review_select_topics_empty", no_empty_flag=True)
		user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_SUBJECT)]['done'])


	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.REVIEW, fsm.GET_TOPICS))

	def callback_select_words(call):

		user_id = get_id(call.message)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		done, btn_set, btn = user.parse_keyboard_ans(call)

		if done == True:
			user.cards_to_review = []
			for i in btn_set:
				user.cards_to_review.extend(user.get_cards_on_topic(user.temp_subject, btn[i][0]))

			options = ['5', '10', '15', '20', '25']
			user.send_string_keyboard("#review_card_number", options)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_TOPICS)]['done'])
		else:
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_TOPICS)]['continue'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.GET_NUMBER),
					content_types=['text'])
	def review2(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		valid, number, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_NUMBER)]['error'])
			return

		user.counter = int(number)
		user.pos = 0
		user.review_card_number = 1
		
		shuffle(user.cards_to_review)
		user.send_card_query(user.cards_to_review[0], "Review", user.review_card_number)
		user.temp_card = user.cards_to_review[0]
		user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_NUMBER)]['done'])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.WAITING_CARD_ANS), 
					content_types = ['text'])
	def answer_card(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		card = user.temp_card
		
		correctness = card.answer_comparison(msg.text)
		if correctness != "":
			user.send_message(correctness)

		user.send_card_answer(card)
		study_item_deck = user.get_study_item_deck(card.get_study_item_id())
		user.send_all_cards(study_item_deck, except_type=card.get_question_type())
		
		user.counter -= 1
		user.review_card_number += 1
		user.pos += 1

		if user.pos == len(user.cards_to_review):
			shuffle(user.cards_to_review)
			user.pos = 0

		if user.counter > 0:
			user.send_card_query(user.cards_to_review[user.pos], "Review", user.review_card_number)
			user.temp_card = user.cards_to_review[user.pos]
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.WAITING_CARD_ANS)]['continue'])
		else:
			user.send_message("#review_done")
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.WAITING_CARD_ANS)]['done'])
			
