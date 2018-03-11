import fsm
from utilities.bot_utils import get_id
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

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		card_id = user.get_card_waiting()
		card = user.get_card(card_id)
		user.temp_card = card

		correctness = card.answer_comparison(msg.text)
		if correctness != "":
			user.send_message(correctness)

		user.send_card_answer(card)
		study_item_deck = user.get_study_item_deck(card.get_study_item_id())
		user.send_all_cards(study_item_deck, except_type=card.get_question_type())
		
		options = ['0', '1', '2', '3', '4', '5']
		user.send_message("#grade_your_performance")
		user.send_string_keyboard("#poll_text", options, first_option_value=0)
		user.set_state(fsm.next_state[fsm.WAITING_ANS])


	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == fsm.WAITING_POLL_ANS,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		card = user.temp_card

		valid, grade, keyboard_option, keyboard_len = user.parse_keyboard_ans(msg)

		if valid == False:
			user.send_message("#choose_from_keyboard", markup=None)
			user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
			
		grade = int(grade)
		user.set_grade_waiting(grade)
		user.send_message("#ok")
		user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['done'])



