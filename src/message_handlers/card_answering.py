import telebot
import fsm
from flashcard import Word, Card
from bot_utils import get_id, create_key_button

def handle_card_answer(bot, rtd):

	#=====================ANSWER CARD=====================
	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.WAITING_ANS, 
					content_types = ['text'])
	def answer_card(msg):
		"""
			Get user answer to card sequence
		"""

		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		card_id = rtd.get_card_waiting(user_id)
		card = rtd.get_card(user_id, card_id)
		res = msg.text.strip().lower()
		rtd.temp_user[user_id] = []
		rtd.temp_user[user_id].append(card)
		if res == card.foreign_word.lower():
			bot.send_message(user_id, "That was correct!")
		else:
			bot.send_message(user_id, "There was a mistake :(")
		bot.send_message(user_id, "Answer: " + card.foreign_word)
		btn0 = create_key_button("0");
		btn1 = create_key_button("1");
		btn2 = create_key_button("2");
		btn3 = create_key_button("3");
		btn4 = create_key_button("4");
		btn5 = create_key_button("5");
		markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
		markup.row(btn0,btn1,btn2,btn3,btn4,btn5)

		bot.send_message(user_id,"Please grade your performance to answer the card",
						reply_markup=markup)
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_ANS])




	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.WAITING_POLL_ANS,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		card = rtd.temp_user[user_id][0]
		try:
			grade = int(msg.text)
		except:
			bot.send_message(user_id, "Please use the custom keyboard")
			rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
		
		if not (grade <= 5 and grade >= 0):
			bot.send_message(user_id, "Please use the custom keyboard")
			rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['error'])
			return
		
		card.calc_next_date(grade)
		rtd.set_supermemo_data(card)
		print(card.get_next_date())
		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id,"OK!", reply_markup=markup)
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_ANS]['done'])




	#=====================REMEMBER CARD=====================

	@bot.message_handler(func = lambda msg:
					rtd.get_state(get_id(msg)) == fsm.WAITING_POLL_REMEMBER,
					content_types=['text'])
	def poll_difficulty(msg):
		"""
			Get user performance grade
		"""
		
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)
		card_id = rtd.get_card_waiting(user_id)
		card = rtd.get_card(user_id, card_id)
		try:
			grade = int(msg.text)
		except:
			bot.send_message(user_id, "Please use the custom keyboard")
			rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
			return
		
		if not (grade <= 5 and grade >= 0):
			bot.send_message(user_id, "Please use the custom keyboard")
			rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['error'])
			return
		
		card.calc_next_date(grade)
		rtd.set_supermemo_data(card)
		print(card.get_next_date())
		markup = telebot.types.ReplyKeyboardRemove()
		bot.send_message(user_id,"OK!", reply_markup=markup)
		rtd.set_state(user_id, fsm.next_state[fsm.WAITING_POLL_REMEMBER]['done'])
