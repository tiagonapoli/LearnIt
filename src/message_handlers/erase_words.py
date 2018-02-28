import telebot
import fsm
from utilities import bot_utils
from utilities import utils
from flashcard import Word, Card
from utilities.bot_utils import get_id
import logging


def handle_erase_words(bot, rtd, debug_mode):	

	#=====================ERASE WORDS=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['erase_words'])
	def erase_words(msg):
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		known_languages = user.get_languages()

		if len(known_languages) == 0:
			bot.send_message(user_id, "_Please, add a language first._", parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)
		text = "*Please select the language:*\n" + bot_utils.create_string_keyboard(known_languages)
		user.keyboard_options = known_languages

		bot.send_message(user_id, text,	reply_markup=markup, parse_mode="Markdown")	
		user.set_state(fsm.next_state[fsm.IDLE]['erase_words'])


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ERASE_WORDS, fsm.GET_LANGUAGE),
					content_types=['text'])
	def erase_words1(msg):
		"""
			Get word's language
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['error'])
			return

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "*Select the word's topic:*",
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
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['done'])
		else: 
			bot.send_message(user_id, "_There are no topics registered in this language yet._", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['no topics'])



	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.ERASE_WORDS, fsm.GET_TOPIC), 
					content_types=['text'])
	def erase_words2(msg):
		"""
			Get topic
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		language = user.temp_word.get_language()
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)
		if valid == False:
			bot.reply_to(msg, "_Please choose from options._", parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_TOPIC)]['error'])
			return			

		words = user.get_words_on_topic(language, topic)
		words_string = utils.words_to_string_list(words)
		btn = bot_utils.create_inline_keys_sequential(words_string)
		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "...", reply_markup=markup)
		btn_set = set()
		markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))

		user.btn_set = btn_set
		user.keyboard_options = btn
		user.temp_words_list = words
		bot.send_message(user_id, "_Select words to erase:_", reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_TOPIC)]['done'])


	@bot.callback_query_handler(func=lambda call:
							rtd.get_user(get_id(call.message)).get_state() == (fsm.ERASE_WORDS, fsm.SELECT_WORDS))

	def callback_select_words(call):
		user = rtd.get_user(get_id(call.message))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))
		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))

		btn_set = user.btn_set
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = user.keyboard_options
		
		if done == True:
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			words = user.temp_words_list
			text = "_Erased words:_\n"
			for i in btn_set:
				print(user.erase_word(words[i].get_word_id()))
				text += "*." + utils.treat_msg_to_send(utils.get_foreign_word(words[i]), "*") + "*\n"
			bot.send_message(user_id, text, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.SELECT_WORDS)]['done'])		
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select words to erase:", reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.ERASE_WORDS, fsm.SELECT_WORDS)]['continue'])
