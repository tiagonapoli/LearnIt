import telebot
import fsm
import utils
import bot_utils
from flashcard import Word, Card
from bot_utils import get_id


def handle_erase_words(bot, rtd):	

	#=====================ERASE WORDS=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE, 
					commands = ['erase_words'])
	def erase_words(msg):
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		known_languages = rtd.get_user_languages(user_id)

		if len(known_languages) == 0:
			bot.send_message(user_id, "Please, add a language first.")
			rtd.set_state(user_id, fsm.IDLE)
			return 	

		markup = bot_utils.create_keyboard(known_languages, 2)

		bot.send_message(user_id, "Please select the language.", 
						reply_markup=markup)	
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['erase_words'])


	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == (fsm.ERASE_WORDS, fsm.GET_LANGUAGE),
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
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['error'])
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
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['done'])
		else: 
			bot.send_message(user_id, "There are no topics registered in this language yet.")
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_LANGUAGE)]['no topics'])



	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == (fsm.ERASE_WORDS, fsm.GET_TOPIC), 
					content_types=['text'])
	def erase_words2(msg):
		"""
			Get topic
		"""
		
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		language = rtd.temp_user[user_id][0].get_language()
		valid, topic = bot_utils.parse_string_keyboard_ans(msg.text, rtd.temp_user[user_id][1])
		if valid == False:
			bot.reply_to(msg, "Please choose from options.")
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_TOPIC)]['error'])
			return			

		words = rtd.get_words_on_topic(user_id, language, topic)
		words_string = utils.words_to_string_list(words)
		btn = bot_utils.create_inline_keys_sequential(words_string)
		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "...", reply_markup=markup)
		markup = bot_utils.create_inline_keyboard(btn, 3, ("End selection", "DONE"))

		rtd.temp_user[user_id].append(set())
		rtd.temp_user[user_id].append(btn)
		rtd.temp_user[user_id].append(words)
		bot.send_message(user_id, "Select words to erase:", reply_markup=markup, parse_mode="Markdown")
		rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.GET_TOPIC)]['done'])


	@bot.callback_query_handler(func=lambda call:
							rtd.get_state(get_id(call.message)) == (fsm.ERASE_WORDS, fsm.SELECT_WORDS))

	def callback_select_words(call):
		user_id = get_id(call.message)
		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))
		btn_number = call.data

		set_btn = rtd.temp_user[user_id][2]
		btn = rtd.temp_user[user_id][3]
		try:
			btn_number = int(btn_number)

			if btn_number in set_btn:
				set_btn.remove(btn_number)
			else:
				set_btn.add(btn_number)

			markup = bot_utils.create_selection_inline_keyboard(set_btn, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select words to erase:", reply_markup=markup)
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.SELECT_WORDS)]['continue'])

		except ValueError:
			#DONE
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			words = rtd.temp_user[user_id][4]
			text = "_Erased words:_\n"
			for i in set_btn:
				print(rtd.erase_word(words[i].get_user(), words[i].get_word_id()))
				text += "*." + words[i].get_word() + "*\n"
			bot.send_message(user_id, text, parse_mode="Markdown")
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_WORDS, fsm.SELECT_WORDS)]['done'])
		