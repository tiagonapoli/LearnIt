from db_api import Database
from datetime import datetime
from FlashCard import Word

class RuntimeData: 
	loop = None
	temp_user = None
	knownUsers = None
	userState = None
	contador_user = None
	db = None

	def __init__(self):
		self.db = Database()
		self.loop = {}
		self.temp_user = {}
		self.knownUsers = self.db.get_known_users()
		self.userState = {}
		self.contador_user = {}
		for user in self.knownUsers:
			self.userState[user] = '0'

	def add_user(self,ID):
		m = self.db.add_user(ID)
		self.knownUsers.add(ID)
		self.set_state(ID,'0')
		return m
	
	def add_word(self,ID):
		#try:
		lista = self.temp_user[ID]
		print("lista[{}] = ".format(ID) + str(lista))
		return self.db.add_word(ID,lista)
		# except:
		# 	print("There is no temp_user data for {}.".format(ID))
		# 	return 'Error'
	
	def get_user_languages(self, ID):
		return self.db.get_user_languages(ID)
	
	def add_language(self, ID, language):
		return self.db.add_language(ID,language)

	def erase_word(self,ID, idiom, foreign_word):
		return self.db.erase_word(ID,idiom,foreign_word)

	def get_state(self, user):
		try:
			ret = self.db.get_state(user)
			ret = self.mapState[ret]
			print("id:{}  state:{}".format(user,ret))
			return ret
		except:
			print("User {} doesn't exist".format(user))
			return 'Error'

	def get_state2(self, user):
		try:
			ret = self.db.get_state2(user)
			print("id:{}  state:{}".format(user,ret))
			return ret
		except:
			print("User {} doesn't exist".format(user))
			return 'Error'

	def set_state(self, user, new_state):
		self.userState[user] = new_state;

	def get_word(self, user_id, word_id):
		info = self.db.get_word(user_id, word_id)
		word = Word(info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], datetime.combine(info[8], datetime.min.time()))
		return word

	def get_all_words_info(self, user_id):
		rows = self.db.get_all_words_info(user_id)
		words = []
		for row in rows:
			words.append(Word(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], datetime.combine(row[8], datetime.min.time())))
		return words

	def set_supermemo_data(self, word):
		row = self.db.set_supermemo_data(word)
		return Word(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], datetime.combine(row[8], datetime.min.time()))

	def set_state(self, state, state2):
		self.db.set_state(state, state2)

	def get_state(self, user_id):
		return self.db.get_state(user_id)
