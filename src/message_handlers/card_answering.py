import fsm
from utilities.bot_utils import get_id
from utilities import bot_utils
from utilities import utils
import logging



def handle_card_answer(bot, user_manager, debug_mode):

	#=====================ANSWER CARD=====================
	@bot.message_handler(func = lambda msg:
					(user_manager.get_user(get_id(msg)).get_state() == fsm.WAITING_ANS and
					user_manager.get_user(get_id(msg)).get_active() == 1), 
					content_types = ['text'])
	def answer_card(msg):
		"""
			Get user answer to card sequence
		"""

		user = user_manager.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))

		card_id = user.get_card_waiting()
		#print("CARD_ID WAITING {}".format(card_id))

		card = user.get_card(card_id)
		res = utils.treat_special_chars(msg.text.lower())

		user.temp_card = card

		string_lst = card.get_word().split()
		if string_lst[0] != '&img':
			if res == card.foreign_word.lower():
				bot.send_message(user_id, 
					bot_language.translate("Your answer was correct!", user))
			else:
				bot.send_message(user_id, 
					bot_language.translate("There was a mistake in your answer :(", user))

		utils.send_foreign_word_ans(bot, card, user)

		cards = user.get_cards_on_word(card.get_word_id())
		for ans in cards:
			utils.send_ans_card(bot, ans, card.get_type(), user)
		
		text = bot_language.translate("poll_text", user)

		options = ['0', '1', '2', '3', '4', '5']
		markup = bot_utils.create_keyboard(options, 6)
		user.keyboard_options = options
		bot.send_message(user_id,
			bot_language.translate("_Please grade your performance to answer the card_\n", user) + text,
			reply_markup=markup, 
			parse_mode="Markdown")

		user.set_state(fsm.next_state[fsm.WAITING_ANS])




	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == fsm.WAITING_POLL_ANS,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		user = user_manager.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger('{}'.format(user_id))

		card = user.temp_card

		valid, grade = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, 
				bot_language.translate("Please choose from keyboard", user))
			user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
			
		grade = int(grade)

		user.set_grade_waiting(grade)

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id,
			bot_language.translate("_OK!_", user), 
			reply_markup=markup, 
			parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['done'])



