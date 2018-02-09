import telebot
import fsm
import utils
import bot_utils
import message_handlers.add_word
from flashcard import Word, Card
from bot_utils import get_id

def handle_add_word_audio(bot, rtd):

	@bot.message_handler(func = lambda msg: rtd.get_state(get_id(msg)) == (fsm.ADD_WORD, fsm.SEND_AUDIO),
						 content_types=['audio', 'voice'])
	def add_audio(msg):
		"""
			ADD_WORD, SEND_AUDIO
		"""
		user_id = get_id(msg)
		rtd.set_state(user_id, fsm.LOCKED)

		word = rtd.temp_user[user_id][0]
		card_id = rtd.get_highest_card_id(user_id) + 1 + len(word.cards)
		
		card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
					card_id, 'audio')
		
		filename = card_id
		path = ""
		if msg.audio != None:
			path = utils.save_audio(msg,
								"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
								"{}".format(filename), 
								bot)
		elif msg.voice != None:
			path = utils.save_voice(msg,
								"../data/{}/{}/".format(user_id, rtd.temp_user[user_id][0].get_word_id()), 
								"{}".format(filename), 
								bot)

		print(path)
		card.add_archive(path)
		word.set_card(card)
		print(str(rtd.temp_user[user_id][0]))
		bot.send_message(user_id, "Audio received successfuly")

		if rtd.receive_queue[user_id].empty():
			message_handlers.add_word.save_word(bot, rtd, user_id)
			rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)]['done'])
		else:
			content_type = rtd.receive_queue[user_id].get()
			message_handlers.add_word.prepare_to_receive(bot, user_id, content_type)
			rtd.set_state(user_id, fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)][content_type])