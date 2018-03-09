import fsm
from utilities import bot_utils, utils
from utilities.bot_utils import get_id
import logging



def handle_erase_languages(bot, user_manager, debug_mode):

	#=====================ERASE LANGUAGES=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.IDLE and
					 user_manager.get_user(get_id(msg)).get_active() == 1), 
					commands = ['erase_languages'])
	def erase_languages(msg):
		user = user_manager.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))

		known_languages = user.get_languages()

		if len(known_languages) == 0:
			bot.send_message(user_id, 
				bot_language.translate("_Please, add a language first._", user), 
				parse_mode="Markdown")
			user.set_state(fsm.IDLE)
			return 	
		
		btn = bot_utils.create_inline_keys_sequential(known_languages)
		btn_set = set()
		markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))

		
		user.btn_set = btn_set
		user.keyboard_options = btn
		bot.send_message(user_id, 
			bot_language.translate("_Select languages to erase:_", user), 
			reply_markup=markup, 
			parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.IDLE]['erase_languages'])
		

	@bot.callback_query_handler(func=lambda call:
							user_manager.get_user(get_id(call.message)).get_state() == (fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES))
	def callback_select_words(call):
		user = user_manager.get_user(get_id(call.message))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))
	
		btn_set = user.btn_set
		btn_set, done = bot_utils.parse_selection_inline_keyboard_ans(call.data, btn_set)
		btn = user.keyboard_options
		
		if done == True:
			bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
			text = bot_language.translate("_Erased languages:_", user) + "\n"
			for i in btn_set:
				user.erase_language(btn[i][0])
				text += "*." + utils.treat_msg_to_send(btn[i][0], "*") + "*\n"
			bot.send_message(user_id, text, parse_mode="Markdown")
			user.set_state(fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['done'])
		
		else:
			markup = bot_utils.create_selection_inline_keyboard(btn_set, btn, 3, ("End selection", "DONE"))
			bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
				text=bot_language.translate("Select languages to erase:", user), reply_markup=markup)
			user.set_state(fsm.next_state[(fsm.ERASE_LANGUAGES, fsm.SELECT_LANGUAGES)]['continue'])
