import telebot
import fsm
import message_handlers.add_word
from utilities import utils
from utilities import bot_utils
from flashcard import Word, Card
from utilities.bot_utils import get_id
import logging

def handle_add_word_audio(bot, rtd, debug_mode):

	@bot.message_handler(func = lambda msg: rtd.get_user(get_id(msg)).get_state() == (fsm.ADD_WORD, fsm.SEND_AUDIO),
						 content_types=['audio', 'voice'])
	def add_audio(msg):
		"""
			ADD_WORD, SEND_AUDIO
		"""
		user = rtd.get_user(get_id(msg))
		user_id = user.get_id()
		user.set_state(fsm.LOCKED)
		logger = logging.getLogger(str(user_id))

		word = user.temp_word
		card_id = user.get_highest_card_id() + 1 + len(word.cards)
		
		card = Card(word.user_id, word.word_id, word.language, word.topic, word.foreign_word,
					card_id, 'audio')
		
		filename = card_id
		data_path = "../data/{}/{}/".format(user_id, word.get_word_id())
		if debug_mode:
			data_path = "../data_debug/{}/{}/".format(user_id, word.get_word_id())

		path = ""
		if msg.audio != None:
			path = utils.save_audio(msg,
								data_path, 
								"{}".format(filename), 
								bot)
		elif msg.voice != None:
			path = utils.save_voice(msg,
								data_path, 
								"{}".format(filename), 
								bot)

		print(path)
		card.add_archive(path)
		word.set_card(card)
		print(str(user.temp_word))
		bot.send_message(user_id, "Audio received successfuly")

		if user.receive_queue.empty():
			
			message_handlers.add_word.save_word(bot, user)
			
			language = user.temp_word.get_language() 
			topic = user.temp_word.get_topic()
			
			options = ['Yes', 'No']
			user.keyboard_options = options
			markup = bot_utils.create_keyboard(options, 2)
			text = "_Would you like to add more words in_ *{}*_, in topic_ *{}*_?_\n".format(
						utils.treat_msg_to_send(language, "*"), utils.treat_msg_to_send(topic, "*")) + bot_utils.create_string_keyboard(options)
			bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")		
			
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)]['done'])
		else:
			content_type = user.receive_queue.get()
			message_handlers.add_word.prepare_to_receive(bot, user, content_type)
			user.set_state(fsm.next_state[(fsm.ADD_WORD, fsm.SEND_AUDIO)][content_type])
