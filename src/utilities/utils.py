import os
import telebot
import datetime
from utilities import bot_utils
import signal
import time

class SendTimeoutException(Exception):   # custom exception
    
    def __str__(self):
    	return "TimeoutException do Teagao"

    pass

def timeout_handler(signum, frame):   # raises exception when signal sent
    raise SendTimeoutException

# Makes it so that when SIGALRM signal sent, it calls the function timeout_handler, which raises your exception
signal.signal(signal.SIGALRM, timeout_handler)

def treat_msg_to_send(text, inside=""):
	if inside == "" or inside == '_':
		text = text.replace('_', inside + '\_' + inside)
	if inside == "" or inside == '*':
		text = text.replace('*', inside + '\*' + inside)
	if inside == "" or inside == '`':
		text = text.replace('`', inside + '\`' + inside)	
	
	if inside == "" or inside == '[':
		text = text.replace('[', inside + '\[' + inside)	
	if inside == "" or inside == ']':
		text = text.replace(']', inside + '\]' + inside)	
	
	return text


def check_special_word(word_text):
	string_lst = word_text.split()
	if string_lst[0] == '&img':
		return True
	return False

def open_bot(logger):
	arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot_aux = telebot.TeleBot(TOKEN)
	logger.info("Bot initialized successfully")
	return bot_aux

def get_file_extension(filename):
	path, extension = os.path.splitext(filename)
	return extension 


def create_dir_card_archive(user_id, word_id, debug_mode):
	if debug_mode:
		if not os.path.exists('../data_debug/{}/{}'.format(user_id, word_id)):
			os.makedirs('../data_debug/{}/{}'.format(user_id, word_id))
	else:
		if not os.path.exists('../data/{}/{}'.format(user_id, word_id)):	
					os.makedirs('../data/{}/{}'.format(user_id, word_id))

def treat_username_str(username):
	if username[0] == '@':
		return username[1:]
	return username

def get_foreign_word(word):
	string_lst = word.get_word().split()
	print(word.get_word())
	if string_lst[0] == '&img':
		return word.cards['text'].get_question()
	return word.get_word()

def words_to_string_list(words):
	ret = []
	for word in words:
		ret.append(get_foreign_word(word))
	return ret


def send_foreign_word_ans(bot, card):
	user_id = card.get_user()
	string_lst = card.foreign_word.split()
	if string_lst[0] == '&img':
		bot.send_message(user_id, "*Answer:* ", parse_mode="Markdown")
		try:
			question = open(string_lst[1],'rb')
			bot.send_photo(user_id, question)
			question.close()
		except:
			pass
	else:
		bot.send_message(user_id, "*Answer:* " + '_' + treat_msg_to_send(card.foreign_word, "_") + '_', parse_mode="Markdown")


def send_all_cards(bot, word, ans_mark="*", logger=None):
	for content, card in word.cards.items():
		send_ans_card(bot, card, None, ans_mark, logger)

def send_ans_card(bot, card, query_type, ans_mark="*", logger=None):
	user_id = card.get_user()
	question = card.get_question()
	content = card.get_type()
	if content == query_type:
		return

	signal.alarm(20)
	markup = bot_utils.keyboard_remove()
	if content == 'image':
		bot.send_message(user_id, ans_mark + "Image answer:" + ans_mark,reply_markup = markup, parse_mode="Markdown")
		question = open(question,'rb')
		bot.send_photo(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'audio':
		bot.send_message(user_id, ans_mark + "Audio answer:" + ans_mark,reply_markup = markup, parse_mode="Markdown")
		question = open(question,'rb')
		bot.send_voice(user_id, question, reply_markup = markup)
		question.close()
	elif content == 'text':
		bot.send_message(user_id, ans_mark + "Text answer:" + ans_mark,reply_markup = markup, parse_mode="Markdown")
		bot.send_message(user_id, question, reply_markup = markup)
	signal.alarm(0)
	

poll_text = ("*5* - _perfect response, without any hesitation_\n" +
			 "*4* - _correct response after a hesitation_\n" +
			 "*3* - _correct response recalled with difficulty_\n" + 
			 "*2* - _incorrect response; where the correct one seemed easy to recall_\n" + 
			 "*1* - _incorrect response; the correct one was remembered_\n" +
			 "*0* - _complete blackout._")


def send_review_card(bot, card, user, card_type = 'Review', number = None, logger=None, set_card_db = True):
		
		if number == None:
			number = ""
		else:
			number = " #" + str(number)


		
		# Start the timer. Once 20 seconds are over, a SIGALRM signal is sent.
		signal.alarm(20)
		try:
			if logger:
				logger.info("Send Review Card - Utils - {} {}".format(card.get_card_id(), card.get_question()))

			language = card.get_language()
			topic = card.get_topic()
			user_id = user.get_id()

			markup = bot_utils.keyboard_remove()
			bot.send_message(user_id, "*{} card{}!*".format(card_type, number), parse_mode="Markdown", reply_markup=markup)
			
			if set_card_db == True:
				user.set_card_waiting(card.get_card_id())
				
			if logger:
				logger.debug("Send Review Card -> Set card waiting {}".format(card.get_card_id()))
			markup = telebot.types.ForceReply(selective = False)
			question = card.get_question()
			content = card.get_type()

			special_word = False
			string_lst = card.foreign_word.split()
			if string_lst[0] == '&img':
				special_word = True

			if special_word == True:
				bot.send_message(user_id, "Try to relate the next message to something you know in *{}/{}*. When you remeber or when you are ready, *send me any message*"
									.format(treat_msg_to_send(language, "*"), treat_msg_to_send(topic, "*")), parse_mode="Markdown")
			if content == 'image':
				if special_word == False:
					bot.send_message(user_id, "Relate the image to a word in _{}_, topic _{}_".format(treat_msg_to_send(language, "_"), treat_msg_to_send(topic, "_")), parse_mode="Markdown")
				question = open(question,'rb')
				print("Send photo {}".format(card.get_question()))
				bot.send_photo(user_id, question, reply_markup = markup)
				question.close()
			elif content == 'audio':
				if special_word == False:
					bot.send_message(user_id, "Transcribe the audio in _{}_, topic _{}_".format(treat_msg_to_send(language, "_"), treat_msg_to_send(topic, "_")), parse_mode="Markdown")
				question = open(question,'rb')
				print("Send voice {}".format(card.get_question()))
				bot.send_voice(user_id, question, reply_markup = markup)
				question.close()
			elif content == 'text':
				if special_word == False:
					bot.send_message(user_id, "Relate the text to a word in _{}_, topic _{}_".format(treat_msg_to_send(language, "_"), treat_msg_to_send(topic, "_")), parse_mode="Markdown")
				print("Send text {}".format(card.get_question()))
				bot.send_message(user_id, question, reply_markup = markup)
			
			signal.alarm(0)
			return True
		except Exception as e:
			if logger:
				logger.error("EXCEPTION ON SEND REVIEW CARD", exc_info=True)
			user.set_card_waiting(0)
			bot.send_message(359999978,"send_review_card crashed {}".format(str(e.__class__.__name__)))
			signal.alarm(0)
			return False



def treat_special_chars(text):
	ant = text 
	text = text.strip()
	#text = text.replace('/', '')
	text = text.replace('[', '')
	text = text.replace(']', '')
	#text = text.replace('\\', '')
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

def backup(db, debug_mode):
	if debug_mode:
		PATH =  "../debug_backup/" + datetime.datetime.now().strftime("%d-%m-%Y.%H-%M") + "/"
	else:
		PATH =  "../backup/" + datetime.datetime.now().strftime("%d-%m-%Y.%H-%M") + "/"
	if not os.path.exists(PATH):
		os.makedirs(PATH)
	print("BACKUP PATH= " + PATH)
	try:
		print(db.backup(PATH))
		if debug_mode:
			os.system("cp -TRv ../data_debug/ {}data".format(PATH))
		else:
			os.system("cp -TRv ../data/ {}data".format(PATH))
		return "Data backup was successfull"
	except Exception as e:
		print(e);
		return "Data backup failed"



def turn_off(rtd, bot, debug_mode):
	"""
		Safely turns of LingoBot. Makes a backup of the data (future)
	"""

	rtd.reset_all_states_turn_off(bot)
	print(backup(rtd, debug_mode))
	
	pass
