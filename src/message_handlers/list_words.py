import telebot
import fsm
from flashcard import Word, Card
from utilities.bot_utils import get_id
from utilities import utils
from utilities import bot_utils


def handle_list_words(bot, rtd):	

	#=====================LIST WORDS=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['list_words'])
	def erase_words(msg):
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		known_languages = user.get_languages()

		if len(known_languages) == 0:
			bot.send_message(user_id, "_Please, add a language first._", parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)
		text = "*Please select the language:*\n" + bot_utils.create_string_keyboard(known_languages)
		user.keyboard_options = known_languages

		bot.send_message(user_id, text,	reply_markup=markup, parse_mode="Markdown")	
		user.set_state(fsm.next_state[fsm.IDLE]['list_words'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.LIST_WORDS, fsm.GET_LANGUAGE),
					content_types=['text'])
	def erase_words1(msg):
		"""
			Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "*Select the word's topic.*",
						reply_markup=markup, parse_mode="Markdown")
		topics = user.get_all_topics(language)
		topics.sort()

		if len(topics) > 0:

			btn = list(topics)
			markup = bot_utils.create_keyboard(btn)
			keyboard = "_Topics registered:_\n" + bot_utils.create_string_keyboard(btn) 

			bot.send_message(user_id, keyboard, reply_markup=markup, parse_mode="Markdown")
			user.temp_word = Word(user_id, None)
			user.temp_word.language = language
			user.keyboard_options = btn
			user.set_state(fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['done'])
		else: 
			bot.send_message(user_id, "_There are no topics registered in this language yet._", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['no topics'])



	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.LIST_WORDS, fsm.GET_TOPIC), 
					content_types=['text'])
	def list_words2(msg):
		"""
			Get topic
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		language = user.temp_word.get_language()
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		if valid == False:
			bot.reply_to(msg, "*Please choose from options.*", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['error'])
			return	
		
		words = user.get_words_on_topic(language, topic)
		text = "_Language:_ *{}*\n_Topic:_ *{}*\n_Words:_\n".format(utils.treat_msg_to_send(language, "*"),utils.treat_msg_to_send(topic, "*"))
		for word in words:
			string_lst = word.get_word().split()
			if string_lst[0] == '&img':
				text += "*." + utils.treat_msg_to_send(word.cards['text'].get_question(), "*") + "*\n"
			else:
				text += "*." + utils.treat_msg_to_send(word.get_word(), "*") + "*\n"

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['done'])

