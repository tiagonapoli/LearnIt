import telebot
import fsm
import message_handlers.add_word_audio
import message_handlers.add_word_translation
import message_handlers.add_word_images
from utilities import utils
from utilities import bot_utils
from flashcard import Word, Card
from utilities.bot_utils import get_id
from queue import Queue


def handle_copy_words_from_user(bot, rtd):

	#=====================ADD WORD=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 rtd.get_user(get_id(msg)).get_active() == 1), 
					commands = ['copy_words'])
	def copy_words(msg):
		"""
			Copy words from user
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		bot.send_message(user_id, 'Please, send the Telegram username of the user you want to copy some words from, in the formar @username')
		user.set_state(fsm.next_state[fsm.IDLE]['copy_words'])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.COPY_WORDS, fsm.GET_USER),
					content_types=['text'])
	def get_user(msg):
		"""
			Copy words from user: Get user
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		username = utils.treat_username_str(msg.text)
		valid, user2 = rtd.get_user_by_username(username)
		user.temp_user = user2

		if valid == False:
			bot.reply_to(msg, "Invalid username")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['error'])
			return

		public = user2.get_public()

		if public == False:
			bot.reply_to(msg, "This user is not public")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['error'])
			return

		known_languages = user2.get_languages()
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "The user _{}_ does not have any language".format(user2.get_username()), parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return

		markup = bot_utils.create_keyboard(known_languages, 2)

		text = "*Please select the language:*\n" + bot_utils.create_string_keyboard(known_languages)
		bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		user.keyboard_options = known_languages
		user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['done'])


	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == (fsm.COPY_WORDS, fsm.GET_LANGUAGE), 
					content_types=['text'])
	def get_languages(msg):
		"""
			Copy words from user: Get languages
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, language = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_LANGUAGE)]['error'])
			return

<<<<<<< HEAD
		user.temp_language = language
=======
>>>>>>> e01c431300833e0fd3de1c309dc05b51e9e2af11
		markup = bot_utils.keyboard_remove()

		topics = user.temp_user.get_all_topics(language)
		topics.sort()

		if len(topics) > 0:
			bot.send_message(user_id, "*Warning: duplicate words will be overwritten. You can use /cancel if you don't want to continue*",
							reply_markup=markup, parse_mode="Markdown")
			btn = bot_utils.create_inline_keys_sequential(topics)
			btn_set = set()
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))

			user.btn_set = btn_set
			user.keyboard_options = btn
			bot.send_message(user_id, "Select the topics you want to copy:",
							reply_markup=markup, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_LANGUAGE)]['done'])
		else: 
			bot.send_message(user_id, "_There are no topics registered in this language yet._", reply_markup=markup, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_LANGUAGE)]['no topics'])
	


	@bot.callback_query_handler(func=lambda call:
							rtd.get_user(get_id(call.message)).get_state() == (fsm.COPY_WORDS, fsm.SELECT_TOPICS))

	def callback_select_words(call):
		user = rtd.get_user(get_id(call.message))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))

		btn_set = user.btn_set
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = user.keyboard_options
		
		if done == True:
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			topics = btn
			selected_topics = []
			for i in btn_set:
				selected_topics.append(topics[i][0])

			text = 'Overwritten words:\n'
			count = 0
			for topic in selected_topics:
				overwritten_words = rtd.copy_topic(user, user.temp_user, user.temp_language, topic)

				if len(overwritten_words) > 0:
				 	text += '*' + topic + ':*\n'
				 	count += 1
				 	for word in overwritten_words:
				 		text += '_.' + word + '_\n'

			if count > 0:
				bot.send_message(user_id, text, parse_mode="Markdown")
			else:
				bot.send_message(user_id, 'There were no overwritten words!')

			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.SELECT_TOPICS)]['done'])
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select the topics you want to copy:", reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.SELECT_TOPICS)]['continue'])