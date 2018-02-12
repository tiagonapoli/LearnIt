import telebot
import fsm
import utils
import bot_utils
import message_handlers.add_word_audio
import message_handlers.add_word_translation
import message_handlers.add_word_images
from flashcard import Word, Card
from bot_utils import get_id
from random import shuffle

def handle_topic_review(bot, rtd):



	#=====================ADD WORD=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.IDLE, 
					commands = ['review'])
	def review(msg):
		"""
			Add word: Get word sequence
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		known_languages = user.get_languages()
		
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "_Please, add a language first._", parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)

		text = "*Please select the word's language:*\n" + bot_utils.create_string_keyboard(known_languages)

		bot.send_message(user_id, text, reply_markup=markup)
		user.keyboard_options = known_languages
		user.set_state(fsm.next_state[fsm.IDLE]['review'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.GET_LANGUAGE),
					content_types=['text'])
	def review1(msg):
		"""
			Add word: Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.GET_LANGUAGE)]['error'])
			return

		user.temp_language = language
		markup = bot_utils.keyboard_remove()
		topics = user.get_all_topics(language)
		topics.sort()

		if len(topics) > 0:
			options = topics
			btn = bot_utils.create_inline_keys_sequential(options)
			btn_set = set()
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ('End selection', 'DONE'))

			user.btn_set = btn_set
			user.keyboard_options = btn

			bot.send_message(user_id, "Select the topics that you want to review",
							reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_LANGUAGE)]['done'])

		else: 
			bot.send_message(user_id, "There are no topics registered in this language yet.")
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_LANGUAGE)]['no topics'])
			return


	@bot.callback_query_handler(func=lambda call:
							rtd.get_user(get_id(call.message)).get_state() == (fsm.REVIEW, fsm.GET_TOPICS))

	def callback_select_words(call):
		""" 
			Add word: Create relate menu 
		"""
		user = rtd.get_user(get_id(call.message))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))

		btn_set = user.btn_set
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = user.keyboard_options
		
		if done == True:

			user.cards_to_review = []
			for i in btn_set:
				user.cards_to_review.extend(user.get_cards_on_topic(user.temp_language, user.keyboard_options[i][0], False))

			if len(user.cards_to_review) == 0:
				markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
				try:
					bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
						text="Please, select *at least one* topic to review:", 
						reply_markup=markup, parse_mode="Markdown")
				except Exception as e:
					print("CANT EDIT MESSAGE")
				user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_TOPICS)]['continue'])
			else:
				bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
				options = ['5', '10', '15', '20', '25']
				markup = bot_utils.create_keyboard(options, 2)
				text = "*Please select the number of review cards that you want to receive:*\n" + bot_utils.create_string_keyboard(options)
				bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
				user.keyboard_options = options
				user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_TOPICS)]['done'])
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select the topics that you want to review:", reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_TOPICS)]['continue'])


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.GET_NUMBER),
					content_types=['text'])
	def review2(msg):
		"""
			Add word: Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, number = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_NUMBER)]['error'])
			return

		user.counter = int(number)
		user.pos = 0
		user.review_card_number = 1
		
		shuffle(user.cards_to_review)
		utils.send_review_card(bot, rtd, user.cards_to_review[0], user, user.review_card_number)
		user.set_state(fsm.next_state[(fsm.REVIEW, fsm.GET_NUMBER)]['done'])


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.REVIEW, fsm.WAITING_CARD_ANS), 
					content_types = ['text'])
	def answer_card(msg):
		"""
			Get user answer to card sequence
		"""

		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		card_id = user.get_card_waiting()
		card = user.get_card(card_id)
		res = utils.treat_special_chars(msg.text.lower())
		
		user.temp_card = card
		if res == card.foreign_word.lower():
			bot.send_message(user_id, "That was correct!")
		else:
			bot.send_message(user_id, "There was a mistake :(")
		bot.send_message(user_id, "*Answer:* " + "_" + card.foreign_word + "_", parse_mode="Markdown")
		
		user.counter -= 1
		user.review_card_number += 1
		user.pos += 1

		if user.pos == len(user.cards_to_review):
			shuffle(user.cards_to_review)
			user.pos = 0

		if user.counter > 0:
			utils.send_review_card(bot, rtd, user.cards_to_review[user.pos], user, user.review_card_number)
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.WAITING_CARD_ANS)]['continue'])
		else:
			bot.send_message(user_id, "*Review session done!*", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.REVIEW, fsm.WAITING_CARD_ANS)]['done'])
			
