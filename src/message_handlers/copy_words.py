import telebot
import fsm
from utilities import utils
from utilities import bot_utils
from flashcard import Word, Card
from utilities.bot_utils import get_id
from queue import Queue


def handle_copy_words(bot, rtd):

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

		bot.send_message(user_id, 'Please, send the Telegram username of the user you want to copy some words from, in the format @username (or just username)')
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

		username = msg.text
		valid, user2 = rtd.get_user_by_username(username)
		user.temp_user = user2

		if valid == False:
			bot.reply_to(msg, "Invalid username. Please, if you still want to copy from a user, send /copy_words again.")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['error'])
			return

		if user.get_id() == user2.get_id():
			bot.reply_to(msg, "You can't copy from yourself! Please, if you still want to copy from a user, send /copy_words again.")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['error'])
			return

		public = user2.get_public()

		if public == False:
			bot.reply_to(msg, "This user is not public. Please, if you still want to copy from a user, send /copy_words again.")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_USER)]['error'])
			return

		known_languages = user2.get_languages()
		
		if len(known_languages) == 0:
			bot.send_message(user_id, "The user _{}_ does not have any language".format(utils.treat_msg_to_send(user2.get_username(), "_")), parse_mode="Markdown")
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


		user.temp_language = language

		markup = bot_utils.keyboard_remove()

		topics = user.temp_user.get_all_topics(language)
		topics.sort()

		if len(topics) > 0:
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
			user.btn_set = btn_set
			user.temp_topics_list = btn

			opt = ['Yes', 'No']
			markup = bot_utils.create_keyboard(opt, 2)

			text = ("In case some words to be copied already exist in your words, *should we overwrite?* If you already copied from this user and topic maybe you don't want to overwrite _(If we overwrite you lose all learning data about that word)_\n"
					 + bot_utils.create_string_keyboard(opt))
			user.keyboard_options = opt

			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.SELECT_TOPICS)]['done'])
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select the topics you want to copy:", reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.SELECT_TOPICS)]['continue'])



	@bot.message_handler(func = lambda msg:
			rtd.get_user(get_id(msg)).get_state() == (fsm.COPY_WORDS, fsm.GET_OVERWRITE), 
			content_types=['text'])
	def overwrite_check(msg):
		"""
			Copy words from user: Get languages
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		valid, overwrite = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_OVERWRITE)]['error'])
			return

		if overwrite == "Yes":
			overwrite = True
		else:
			overwrite = False
		

		btn_set = user.btn_set
		topics = user.temp_topics_list
		selected_topics = []
		for i in btn_set:
			selected_topics.append(topics[i][0])

		text = '*Overwritten words:*\n'
		count = 0
		for topic in selected_topics:
			overwritten_words = rtd.copy_topic(user, user.temp_user, user.temp_language, topic, overwrite)

			if len(overwritten_words) > 0:
			 	text += '*Topic: ' + utils.treat_msg_to_send(topic, "*") + '*\n'
			 	count += 1
			 	for word in overwritten_words:
			 		text += '_.' + utils.treat_msg_to_send(word, "_") + '_\n'

		markup = bot_utils.keyboard_remove()
		print(text)
		if count > 0:
			bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")
		else:
			bot.send_message(user_id, 'There were no overwritten words!', reply_markup=markup)

		user.set_state(fsm.next_state[(fsm.COPY_WORDS, fsm.GET_OVERWRITE)]['done'])