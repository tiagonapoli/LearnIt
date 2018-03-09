import os
import translation
from BotMessageSender import BotMessageSender
from utilities import utils

class BotControllerFactory():

	def __init__(self, token):
		self.token = token

	def get_bot_controller(self, user_id, language):
		return BotController(self.token, user_id, language)


class BotController(BotMessageSender):

	def __init__(self, token, user_id, language):
		BotMessageSender.__init__(self, token, user_id, language)


	def save_image(self, image_msg, path, image_name):
		try: 
			self.set_bot()
			f = image_msg.photo[-1].file_id
			arq = self.bot.get_file(f)
			downloaded_file = self.bot.download_file(arq.file_path)
			tipo = []
			for c in arq.file_path[::-1]:
				if c == '.' :
					break
				tipo.append(c)
			tipo = "".join(tipo[::-1])
			if not os.path.exists(path):
				os.makedirs(path)
			with open(path + image_name + "." + tipo, 'wb') as new_file:
				new_file.write(downloaded_file)
			return path + image_name + "." + tipo
		except Exception as e:
			self.logger.error("Error in save image {}".format(self.user_id), exc_info=True)
			return None


	def save_audio(self, audio_msg, path, audio_name):
		try: 
			self.set_bot()
			f = audio_msg.audio.file_id
			arq = self.bot.get_file(f)
			downloaded_file = self.bot.download_file(arq.file_path)
			tipo = []
			for c in arq.file_path[::-1]:
				if c == '.' :
					break
				tipo.append(c)
			tipo = "".join(tipo[::-1])
			if not os.path.exists(path):
				os.makedirs(path)
			with open(path + audio_name + "." + tipo, 'wb') as new_file:
				new_file.write(downloaded_file)
			return path + audio_name + "." + tipo
		except Exception as e:
			self.logger.error("Error in save audio {}".format(self.user_id), exc_info=True)
			return None	


	def save_voice(self, voice_msg, path, voice_name):
		try: 
			self.set_bot()
			f = voice_msg.voice.file_id
			arq = self.bot.get_file(f)
			downloaded_file = self.bot.download_file(arq.file_path)
			tipo = "mp3"
			if not os.path.exists(path):
				os.makedirs(path)
			with open(path + voice_name + "." + tipo, 'wb') as new_file:
				new_file.write(downloaded_file)
			return path + voice_name + "." + tipo
		except Exception as e:
			self.logger.error("Error in save voice {}".format(self.user_id), exc_info=True)
			return None	

	def send_all_cards(self, study_item_deck):
		for card_type, card in study_item_deck.cards.items():
			self.send_card_question(card)

	def send_card_answer(self, card):
		item_type, study_item = card.get_study_item()
		if item_type == 1:
			self.send_message("*Answer:* ")
			return self.send_photo(study_item)
		else:
			return self.send_message("*Answer:* _%s_", txt_args=(study_item, ))

	def send_card_question(self, card):
		question_type, question = card.get_question()
		if question_type == 'image':
			self.send_message("*Image question:*")
			self.send_photo(question)
		elif question_type == 'audio':
			self.send_message("*Audio question:*")
			self.send_voice(question)
		elif question_type == 'text':
			self.send_message("*Text question:*", txt_args=(" " + question, ))
			self.send_message(question, translate_flag=False)

	def send_card_query(self, card, card_type = 'Review', number = None):
			
			if number == None:
				number = ""
			else:
				number = " #" + str(number)

			subject = card.get_subject()
			topic = card.get_topic()

			self.send_message("*%s card%s!*", txt_args=(card_type, number))
				
			study_item_type, study_item = card.get_study_item()
			question_type, question = card.get_question()

			if study_item_type == 1:
				self.send_message("Try to relate the next message to something you know in *%s/%s*. When you remeber or when you are ready, *send me any message*",
					txt_args=(subject, topic))
			elif question_type == 'image':
				self.send_message("Relate the image to something in _%s_, topic _%s_", txt_args=(subject, topic))
			elif question_type == 'audio':
				self.send_message("Transcribe the audio in _%s_, topic _%s_", txt_args=(subject, topic))
			elif question_type == 'text':
				self.send_message("Relate the text to something in _%s_, topic _%s_", txt_args=(subject, topic))

			if question_type == 'image':
				self.send_photo(question)
			elif question_type == 'audio':
				self.send_voice(question)
			elif question_type == 'text':
				self.send_message(question, translate_flag=False, parse='')




if __name__ == '__main__':

	from Flashcard import StudyItemDeck, Card

	sender_factory = BotController('495750247:AAFVO7YqWCl2QKov6PselFnAlL_RRBtfWco')

	message_sender = sender_factory.get_bot_controller(359999978, 0)

	deck_text = StudyItemDeck(42, 1, 1, 'Portugues', 'Comida', 'Carne*', 0)
	card = Card(42, 1, 1, 'Portugues', 'Comida', 'Car_ne', 0, 1, 'Meat', 'text') 
	deck_text.set_card(card)

	message_sender.send_card_query(deck_text.cards['text'])
	message_sender.send_card_answer(deck_text.cards['text'])
	message_sender.send_card_question(deck_text.cards['text'])

	deck_img = StudyItemDeck(42, 1, 1, 'Portugues', 'Comida', '/home/tiago/Pictures/Trees_JeroenVanNieuwenhoveFlickr.jpg', 1)
	deck_img = StudyItemDeck(42, 1, 1, 'Portugues', 'Comida', '/home/tiago/Pictures/Trees_JeroenVanNieuwenhoveFlickr.jpg', 1)
	card = Card(42, 1, 1, 'Portugues', 'Comida', '/home/tiago/Pictures/Trees_JeroenVanNieuwenhoveFlickr.jpg', 1, 2, 'Meat', 'text') 
	deck_img.set_card(card)

	message_sender.send_message("TESTE 2", translate_flag=False)
	message_sender.send_card_query(deck_img.cards['text'])
	message_sender.send_card_answer(deck_img.cards['text'])
	message_sender.send_card_question(deck_img.cards['text'])
