import os
import telebot

def get_file_extension(filename):
	path, extension = os.path.splitext(filename)
	return extension 

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
			print(c)
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
	pass	

def turn_off():
	"""
		Safely turns of LingoBot. Makes a backup of the data (future)
	"""
	pass
