import os

def save_image(image_msg, path, image_name, bot):
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

def turn_off():
	print("YESSSSS")

