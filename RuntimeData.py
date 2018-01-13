import os

class RuntimeData: 
	loop = None
	temp_user = None
	knownUsers = None
	userState = None
	contador_user = None
	db = None

	def __init__(self):
		db = Database()
		self.loop = {}
		self.temp_user = {}
		self.knownUsers = db.get_knownUsers()
		self.userState = {}
		for user in knownUsers:
			userState[user] = '0'
		self.contador_user = {}

	def add_user(ID):
		return db.add_user(ID)
	
	def add_word(ID):
		try:
			return db.add_word(ID,temp_user[ID])
		except:
			print("There is no temp_user data for {}.\n".format(ID))
			return 'Error'
	
	def erase_word(ID, idiom, foreign_word):
		return db.erase_word(ID,idiom,foreign_word)

	def get_state(self, user):
		try:
			ret = self.userState[user]
			print("id:{}  state:{}".format(user,ret))
			return ret
		except:
			print("User {} doesn't exist".format(user))
			return 'Error'

	def set_state(self, user, new_state):
			self.userState[user] = new_state;










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
	print("YESSSSS")

