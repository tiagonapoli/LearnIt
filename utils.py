import os
import telebot
import time
import scrape_images
import psycopg2

loop = {}
temp_user = {}
knownUsers = set()
userState = {}
contador_user = {}
step_id = {'0': 'IDLE',
		   '1': 'get_word_info->WAITING VOCABULARY',
		   '2': 'get_word_info->IMAGE_SOURCE',
		   '3': 'get_word_info->Receiving images', 
		   '4': 'get_word_info->Send image loop',
		   '5': 'get_word_info->Google image selection loop'
		   }

def get_user_state(ID):
	print("id:{}  state:{}".format(ID, userState[ID]))
	return userState[ID]

def save_image(image_msg, path):
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
	with open(path + "." + tipo, 'wb') as new_file:
		new_file.write(downloaded_file)

def turn_off():
	conn.close()
	cursor.close()
	print("YESSSSS")