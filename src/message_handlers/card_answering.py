import telebot
import fsm
from flashcard import Word, Card
from utilities.bot_utils import get_id
from utilities import bot_utils
from utilities import utils

def handle_card_answer(bot, rtd):

	#=====================ANSWER CARD=====================
	@bot.message_handler(func = lambda msg:
					(rtd.get_user(get_id(msg)).get_state() == fsm.WAITING_ANS and
					rtd.get_user(get_id(msg)).get_active() == 1), 
					content_types = ['text'])
	def answer_card(msg):
		"""
			Get user answer to card sequence
		"""

		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		card_id = user.get_card_waiting()
		print("CARD_ID WAITING {}".format(card_id))

		card = user.get_card(card_id)
		res = utils.treat_special_chars(msg.text.lower())

		user.temp_card = card
		if res == card.foreign_word.lower():
			bot.send_message(user_id, "Your answer was correct!")
		else:
			bot.send_message(user_id, "There was a mistake in your answer :(")
		bot.send_message(user_id, "*Answer:* " + card.foreign_word, parse_mode="Markdown")

		cards = user.get_cards_on_word(card.get_word_id())
		for ans in cards:
			utils.send_ans_card(bot, ans, card.get_type())
		
		text = utils.poll_text

		options = ['0', '1', '2', '3', '4', '5']
		markup = bot_utils.create_keyboard(options, 6)
		user.keyboard_options = options
		bot.send_message(user_id,"_Please grade your performance to answer the card_\n" + text,
						reply_markup=markup, parse_mode="Markdown")

		user.set_state(fsm.next_state[fsm.WAITING_ANS])




	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.WAITING_POLL_ANS,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		card = user.temp_card

		valid, grade = bot_utils.parse_string_keyboard_ans(msg.text, user.keyboard_options)

		if valid == False:
			bot.reply_to(msg, "Please choose from keyboard")
			user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
			
		grade = int(grade)

		user.set_grade_waiting(grade)

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id,"_OK!_", reply_markup=markup, parse_mode="Markdown")
		user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['done'])



