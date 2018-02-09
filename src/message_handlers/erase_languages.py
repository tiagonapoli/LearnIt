import telebot
import fsm
from flashcard import Word, Card
from bot_utils import get_id, create_key_button, create_inline_key_button


def handle_erase_languages(bot, rtd):

	#=====================ERASE LANGUAGES=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.IDLE, 
					commands = ['erase_languages'])
	def erase_languages(msg):
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		known_languages = rtd.get_user_languages(user_id)

		if len(known_languages) == 0:
			bot.send_message(user_id, "Please, add a language first.")
			rtd.set_state(user_id, fsm.IDLE)
			return 	
		
		btn = []
		aux_counter = 0
		for language in known_languages:
			text = language
			btn.append(create_inline_key_button(text, str(aux_counter)))
			aux_counter += 1

		markup = telebot.types.InlineKeyboardMarkup()

		for i in range(0, len(btn)//2):
			markup.row(btn[2*i], btn[2*i+1])

		if len(btn) % 2 == 1:
			markup.row(btn[len(btn)-1])

		markup.row(create_inline_key_button("End selection", "DONE"))

		rtd.temp_user[user_id] = []
		rtd.temp_user[user_id].append(set())
		rtd.temp_user[user_id].append(known_languages)
		bot.send_message(user_id, "Select languages to erase:", reply_markup=markup, parse_mode="Markdown")
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['erase_languages'])
		

	@bot.callback_query_handler(func=lambda call:
							rtd.get_state(get_id(call.message)) == (fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES))
	def callback_select_words(call):
		user_id = get_id(call.message)
		print("CALLBACK TEXT: {}   DATA: {}".format(call.message.text,call.data))
		btn_number = call.data

		set_btn = rtd.temp_user[user_id][0]
		languages = rtd.temp_user[user_id][1]
		try:
			btn_number = int(btn_number)
			markup = telebot.types.InlineKeyboardMarkup()
			btn = []	
			if btn_number in set_btn:
				set_btn.remove(btn_number)
			else:
				set_btn.add(btn_number)

			for i in range(0, len(languages)):
				if i in set_btn:
					btn.append(create_inline_key_button(">>" + languages[i] + "<<", str(i)))
				else:
					btn.append(create_inline_key_button(languages[i], str(i)))

			markup = telebot.types.InlineKeyboardMarkup()

			for i in range(0, len(btn)//2):
				markup.row(btn[2*i], btn[2*i+1])

			if len(btn) % 2 == 1:
				markup.row(btn[len(btn)-1])

			markup.row(create_inline_key_button("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select languages to erase:", reply_markup=markup)
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['continue'])

		except ValueError:
			#DONE
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			text = "_Erased languages:_\n"
			for i in set_btn:
				print(rtd.erase_language(user_id, languages[i]))
				text += "*." + languages[i] + "*\n"
			bot.send_message(user_id, text, parse_mode="Markdown")
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['done'])


