import telebot
import fsm
import utils
from flashcard import Word, Card
from bot_utils import get_id, create_key_button


def handle_list_words(bot, rtd):	

	#=====================LIST WORDS=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE, 
					commands = ['list_words'])
	def erase_words(msg):
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		known_languages = rtd.get_user_languages(user_id)

		btn = []
		for language in known_languages:
			btn.append(create_key_button(language))
		
		if len(btn) == 0:
			bot.send_message(user_id, "Please, add a language first.")
			rtd.set_state(user_id, fsm.IDLE)
			return 	

		markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

		for i in range(0,len(btn)//2):
			markup.row(btn[2*i], btn[2*i+1])

		if len(btn)%2 == 1:
			markup.row(btn[len(btn)-1])

		bot.send_message(user_id, "Please select the language.", 
						reply_markup=markup)	
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
		known_languages = rtd.get_user_languages(user_id)
		language = utils.treat_special_chars(msg.text)
		if not (language in known_languages):
			bot.reply_to(msg, "Please choose from keyboard")
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_LANGUAGE)]['error'])
			return

		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id, "Select the word's topic.",
						reply_markup=markup)
		topics = rtd.get_all_topics(user_id, language)
		topics.sort()

		if len(topics) > 0:

			btn = []
			for topic in topics:
				btn.append(create_key_button(topic))

			markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

			for i in range(0,len(btn)//3):
				markup.row(btn[3*i], btn[3*i+1], btn[3*i+2])

			if len(btn)%3 == 2:
				markup.row(btn[len(btn)-2],btn[len(btn)-1])

			if len(btn)%3 == 1:
				markup.row(btn[len(btn)-1])

			text = "Topics registered:\n"
			aux_cnt = 1
			for topic in topics:
				text += "/{}. ".format(aux_cnt) + topic + '\n'
				aux_cnt += 1
			bot.send_message(user_id, text, reply_markup=markup)
			rtd.temp_user[user_id] = []
			rtd.temp_user[user_id].append(Word(user_id, None))
			rtd.temp_user[user_id][0].language = language
			rtd.temp_user[user_id].append(topics)
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
		valid, topic = utils.parse_option(msg.text.strip(), rtd.temp_user[user_id][1])
		if valid == False:
			topic = utils.treat_special_chars(msg.text)

		known_topics = rtd.get_all_topics(user_id, language)
		if not (topic in known_topics):
			bot.reply_to(msg, "Please choose from options.")
			rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['error'])
			return
		words = rtd.get_words_on_topic(user_id, language, topic)
		str = "_Language:_ *{}*\n_Topic:_ *{}*\n_Words:_\n".format(language,topic)
		for word in words:
			str += "*." + word.get_word() + "*\n"

		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id, str, reply_markup=markup, parse_mode="Markdown")
		rtd.set_state(user_id, fsm.next_state[(fsm.LIST_WORDS, fsm.GET_TOPIC)]['done'])

