import os
import telebot
from utilities import bot_utils

def get_file_extension(filename):
	path, extension = os.path.splitext(filename)
	return extension 



def words_to_string_list(words):
	ret = []
	for word in words:
		ret.append(word.get_word())
	return ret



def send_ans_card(bot, card, query_type):
	user_id = card.get_user()
	question = card.get_question()
	content = card.get_type()
	if content == query_type or content == 'default':
		return

	markup = bot_utils.keyboard_remove()
	if content == 'image':
		bot.send_message(user_id, "*Image answer:*",reply_markup = markup, parse_mode="Markdown")
		question = open(question,'rb')
		bot.send_photo(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'audio':
		bot.send_message(user_id, "*Audio answer:*",reply_markup = markup, parse_mode="Markdown")
		question = open(question,'rb')
		bot.send_voice(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'translation':
		bot.send_message(user_id, "*Translation:*",reply_markup = markup, parse_mode="Markdown")
		bot.send_message(user_id, question, reply_markup = markup)
	

poll_text = ("*5* - _perfect response_\n" +
			 "*4* - _correct response after a hesitation_\n" +
			 "*3* - _correct response recalled with difficulty_\n" + 
			 "*2* - _incorrect response; where the correct one seemed easy to recall_\n" + 
			 "*1* - _incorrect response; the correct one was remembered_\n" +
			 "*0* - _complete blackout._")


def send_review_card(bot, card, user, card_type = 'Review', number = None):
		
		if number == None:
			number = ""
		else:
			number = " #" + str(number)

		language = card.get_language()
		user_id = user.get_id()

		markup = bot_utils.keyboard_remove()
		bot.send_message(user_id, "*{} card{}!*".format(card_type, number), parse_mode="Markdown", reply_markup=markup)
		
		user.set_card_waiting(card.card_id)
		markup = telebot.types.ForceReply(selective = False)
		question = card.get_question()
		content = card.get_type()
		if content == 'image':
			bot.send_message(user_id, "Relate the image to a word in _{}_".format(language), parse_mode="Markdown")
			question = open(question,'rb')
			bot.send_photo(user_id, question, reply_markup = markup)
			question.close()
		elif content == 'audio':
			bot.send_message(user_id, "Transcribe the audio in _{}_".format(language), parse_mode="Markdown")
			question = open(question,'rb')
			bot.send_voice(user_id, question, reply_markup = markup)
			question.close()
		elif content == 'translation':
			bot.send_message(user_id, "Translate the word to _{}_".format(language), parse_mode="Markdown")
			bot.send_message(user_id, question, reply_markup = markup)
		elif content == 'default':
			bot.send_message(user_id, "Just remember the _usage_ and _meaning_ of the next word.".format(language), parse_mode="Markdown")
			bot.send_message(user_id, question, reply_markup= markup)
			text = poll_text
			options = ['0', '1', '2', '3', '4', '5']
			markup = bot_utils.create_keyboard(options, 6)
			user.keyboard_options = options
			bot.send_message(user_id,"_Please grade how difficult this word is for now_\n" + text,
							reply_markup=markup, parse_mode="Markdown")



def treat_special_chars(text):
	ant = text 
	text = text.strip()
	text = text.replace('_', ' ')
	text = text.replace('/', '')
	text = text.replace('\\', '')
	text = text.strip()
	text = text.replace('\n', '')
	print("{} -> treated -> {}".format(ant,text))
	return text

def save_image(image_msg, path, image_name, bot):
	"""
		Saves image received from user on Telegram
	
		Args:
			image_msg: message object that carries an image
			path: path to save the archive
			image_name: savename of the file
			bot: Telebot object
	"""
	try: 
		f = image_msg.photo[-1].file_id
		arq = bot.get_file(f)
		downloaded_file = bot.download_file(arq.file_path)
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
		print("Exception in utils.save_image")
		print(e)
		return None

def save_audio(audio_msg, path, audio_name, bot):
	"""
		Saves audio received from user on Telegram
	
		Args:
			audio_msg: message object that carries an audio
			path: path to save the archive
			audio_name: savename of the file
			bot: Telebot object
	"""
	try: 
		f = audio_msg.audio.file_id
		arq = bot.get_file(f)
		downloaded_file = bot.download_file(arq.file_path)
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
		print("Exception in utils.save_audio")
		print(e)
		return None	

def save_voice(voice_msg, path, voice_name, bot):
	"""
		Saves audio received from user on Telegram
	
		Args:
			audio_msg: message object that carries an audio
			path: path to save the archive
			audio_name: savename of the file
			bot: Telebot object
	"""
	try: 
		f = voice_msg.voice.file_id
		arq = bot.get_file(f)
		downloaded_file = bot.download_file(arq.file_path)
		tipo = "mp3"
		if not os.path.exists(path):
			os.makedirs(path)
		with open(path + voice_name + "." + tipo, 'wb') as new_file:
			new_file.write(downloaded_file)
		return path + voice_name + "." + tipo
	except Exception as e:
		print("Exception in utils.save_voice")
		print(e)
		return None	

def backup_data():
	try:
		if not os.path.exists("../backup/"):
			os.mkdir("../backup/")
		os.system("cp -TRv ../data/ ../backup/data")
		return "Data backup was successfull"
	except Exception as e:
		print(e);
		return "Data backup failed"



def turn_off(db):
	"""
		Safely turns of LingoBot. Makes a backup of the data (future)
	"""
	print(backup_data())
	print(db.backup())
	pass
