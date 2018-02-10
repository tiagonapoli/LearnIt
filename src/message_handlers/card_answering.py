import telebot
import fsm
from flashcard import Word, Card
from bot_utils import get_id, create_key_button

def handle_card_answer(bot, rtd):

	#=====================ANSWER CARD=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.WAITING_ANS, 
					content_types = ['text'])
	def answer_card(msg):
		"""
			Get user answer to card sequence
		"""

		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		card_id = user.get_card_waiting()
		card = user.get_card(card_id)
		res = utils.treat_special_chars(msg.text.lower())
		
		user.temp_card = card
		if res == card.foreign_word.lower():
			bot.send_message(user_id, "That was correct!")
		else:
			bot.send_message(user_id, "There was a mistake :(")
		bot.send_message(user_id, "Answer: " + card.foreign_word)
		btn = ["1", "2", "3", "4", "5"]
		markup = bot_utils.create_keyboard(btn,5)

		bot.send_message(user_id,"Please grade your performance to answer the card",
						reply_markup=markup)
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
		try:
			grade = int(msg.text)
		except:
			bot.send_message(user_id, "Please use the custom keyboard")
			user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
		
		if not (grade <= 5 and grade >= 0):
			bot.send_message(user_id, "Please use the custom keyboard")
			user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
		
		card.calc_next_date(grade)
		user.set_supermemo_data(card)
		print(card.get_next_date())
		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id,"OK!", reply_markup=markup)
		user.set_state(fsm.next_state[fsm.WAITING_POLL_ANS]['done'])




	#=====================REMEMBER CARD=====================

	@bot.message_handler(func = lambda msg:
					rtd.get_user(get_id(msg)).get_state() == fsm.WAITING_POLL_REMEMBER,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		card_id = user.get_card_waiting()
		card = user.get_card(card_id)
		try:
			grade = int(msg.text)
		except:
			bot.send_message(user_id, "Please use the custom keyboard")
			user.set_state(fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
			return
		
		if not (grade <= 5 and grade >= 1):
			bot.send_message(user_id, "Please use the custom keyboard")
			user.set_state(fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
			return
		
		card.calc_next_date(grade)
		user.set_supermemo_data(card)
		print(card.get_next_date())
		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id,"OK!", reply_markup=markup)
		user.set_state(fsm.next_state[fsm.WAITING_POLL_REMEMBER]['done'])
