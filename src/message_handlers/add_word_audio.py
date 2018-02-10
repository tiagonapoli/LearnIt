import telebot
import fsm
import utils
import bot_utils
import message_handlers.add_word
from flashcard import Word, Card
from bot_utils import get_id

def handle_add_word_audio(bot, rtd):

	@bot.message_handler(func = lambda msg: rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.SEND_AUDIO),
						 content_types=['audio', 'voice'])
	def add_audio(msg):
		"""
			ADD_WORD, SEND_AUDIO
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)

		word = user.temp_word
		card_id = user.get_highest_card_id() + 1 + len(word.cards)
		
		card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
					card_id, 'audio')
		
		filename = card_id
		path = ""
		if msg.audio != None:
			path = utils.save_audio(msg,
								"../data/{}/{}/".format(user_id, word.get_word_id()), 
								"{}".format(filename), 
								bot)
		elif msg.voice != None:
			path = utils.save_voice(msg,
								"../data/{}/{}/".format(user_id, word.get_word_id()), 
								"{}".format(filename), 
								bot)

		print(path)
		card.add_archive(path)
		word.set_card(card)
		print(str(user.temp_word))
		bot.send_message(user_id, "Audio received successfuly")

		if user.receive_queue.empty():
			message_handlers.add_word.save_word(bot, user)
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)]['done'])
		else:
			content_type = user.receive_queue.get()
			message_handlers.add_word.prepare_to_receive(bot, user, content_type)
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)][content_type])