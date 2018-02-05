import os
import telebot

def get_file_extension(filename):
	path, extension = os.path.splitext(filename)
	return extension 

def parse_option(text, topics_array):
	if text[0] != '/':
		return False,""
	text = text[1:]
	try:
		number = int(text)
		print("PARSE OPTION NUMBER {}".format(number))
		number -= 1
		if number >= 0 and number < len(topics_array):
			return True,topics_array[number]
		else:
			return False,""
	except Exception as e:
		print(e)
		return False,""


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
		os.system("cp -r ../data/ ../backup/data")
		return "Data backup was successfull"
	except Exception as e:
		print(e);
		return "Data backup failed"

def erase_at_jobs():
	try:
		os.system("atrm $(atq | cut -f1)")
		return "Deleted at jobs"
	except Exception as e:
		print(e)
		return "Failed to delete at jobs"

def turn_off(db):
	"""
		Safely turns of LingoBot. Makes a backup of the data (future)
	"""
	print(backup_data())
	print(db.backup())
	print(erase_at_jobs())
	pass
