import telebot
import fsm
import utils
import bot_utils
from flashcard import Word, Card
from bot_utils import get_id


def handle_list_words(bot, rtd):	

	#=====================LIST WORDS=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE, 
					commands = ['list_words'])
	def erase_words(msg):
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		known_languages = rtd.get_user_languages(user_id)

		if len(known_languages) == 0:
			bot.send_message(user_id, "Please, add a language first.")
			rtd.set_state(user_id, fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)
		text = "Please select the language:\n" + bot_utils.create_string_keyboard(known_languages)
		rtd.temp_user[user_id] = known_languages

		bot.send_message(user_id, text,	reply_markup=markup)	
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['list_words'])




	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == (fsm.LIST_WORDS, fsm.GET_LANGUAGE),
					content_types=['text'])
	def erase_words1(msg):
		"""
			Get word's language
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		known_languages = rtd.temp_user[user_id]
		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, known_languages)
		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "Select the word's topic.",
						reply_markup=markup)
		topics = rtd.get_all_topics(user_id, language)
		topics.sort()

		if len(topics) > 0:

			btn = list(topics)
			markup = bot_utils.create_keyboard(btn)
			keyboard = "Topics registered:\n" + bot_utils.create_string_keyboard(btn) 

			bot.send_message(user_id, keyboard, reply_markup=markup)
			rtd.temp_user[user_id] = []
			rtd.temp_user[user_id].append(Word(user_id, None))
			rtd.temp_user[user_id][0].language = language
			rtd.temp_user[user_id].append(btn)
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['done'])
		else: 
			bot.send_message(user_id, "There are no topics registered in this language yet.")
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['no topics'])



	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == (fsm.LIST_WORDS, fsm.GET_TOPIC), 
					content_types=['text'])
	def list_words2(msg):
		"""
			Get topic
		"""
		
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		language = rtd.temp_user[user_id][0].get_language()
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, rtd.temp_user[user_id][1])
		if valid == False:
			bot.reply_to(msg, "Please choose from options.")
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['error'])
			return	
		
		words = rtd.get_words_on_topic(user_id, language, topic)
		text = "_Language:_ *{}*\n_Topic:_ *{}*\n_Words:_\n".format(language,topic)
		for word in words:
			text += "*." + word.get_word() + "*\n"

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['done'])

