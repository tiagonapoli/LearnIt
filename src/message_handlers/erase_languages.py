import telebot
import fsm
import bot_utils
from flashcard import Word, Card
from bot_utils import get_id


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
		
		btn = bot_utils.create_inline_keys_sequential(known_languages)
		set_btn = set()
		markup = bot_utils.create_selection_inline_keyboard(set_btn, btn, 3, ("End selection", "DONE"))

		rtd.temp_user[user_id] = []
		rtd.temp_user[user_id].append(set_btn)
		rtd.temp_user[user_id].append(btn)
		bot.send_message(user_id, "Select languages to erase:", reply_markup=markup, parse_mode="Markdown")
		rtd.set_state(user_id, fsm.next_state[fsm.IDLE]['erase_languages'])
		

	@bot.callback_query_handler(func=lambda call:
							rtd.get_state(get_id(call.message)) == (fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES))
	def callback_select_words(call):
		user_id = get_id(call.message)
	
		set_btn = rtd.temp_user[user_id][0]
		set_btn, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, set_btn)
		btn = rtd.temp_user[user_id][1]
		
		if done == True:
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			text = "_Erased languages:_\n"
			for i in set_btn:
				print(rtd.erase_language(user_id, btn[i][0]))
				text += "*." + btn[i][0] + "*\n"
			bot.send_message(user_id, text, parse_mode="Markdown")
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['done'])
		
		else:
			markup = bot_utils.create_selection_inline_keyboard(set_btn, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="Select languages to erase:", reply_markup=markup)
			rtd.set_state(user_id, fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['continue'])
