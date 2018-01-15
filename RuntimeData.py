from db_api import Database
from datetime import datetime
from FlashCard import Word

class RuntimeData: 
	loop = {}
	temp_user = {}
	knownUsers = None
	mapState = {0 : '0',
				1 : 'WAITING_ANS',
				2 : 'WAITING_POLL_ANS',
				3 : '1_0',
				4 : '1_1',
				5 : '1_2',
				6 : '1_3',
				7 : '1_3-opt1',
				8 : '1_3-opt1_0',
				9 : '1_3-opt2_0'}
	mapStateInv = {}
	contador_user = {}
	db = None

	def __init__(self):
		self.db = Database()
		self.knownUsers = self.db.get_known_users()
		for key,val in self.mapState.items():
			self.mapStateInv[val] = key
		# for user in self.knownUsers:
		# 	self.userState[user] = 

	def add_user(self,ID):
		m = self.db.add_user(ID)
		self.knownUsers.add(ID)
		return m
	
	def add_word(self,ID):
		# try:
			lista = self.temp_user[ID]
			print("lista[{}] = ".format(ID) + str(lista))
			return self.db.add_word(ID,lista)
		# except:
		#  	print("There is no temp_user data for {}.".format(ID))
		#  	return 'Error'
	
	def get_user_languages(self, ID):
		return self.db.get_user_languages(ID)
	
	def add_language(self, ID, language):
		return self.db.add_language(ID,language)

	def erase_word(self,ID, idiom, foreign_word):
		return self.db.erase_word(ID,idiom,foreign_word)

	def get_state(self, user):
		# try:
			st1,st2 = self.db.get_state(user)
			st1 = self.mapState[st1]
			print("id:{}  state:{}".format(user,st1))
			return st1
		# except:
		# 	print("User {} doesn't exist".format(user))
		# 	return 'Error'

	def get_state2(self, user):
		# try:
			st1,st2 = self.db.get_state(user)
			return st2
		# except:
		# 	print("User {} doesn't exist".format(user))
		# 	return 'Error'

	def set_state(self, user, new_state, new_state2=0):
		self.db.set_state(user, self.mapStateInv[new_state], new_state2)

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
		self.db.set_supermemo_data(word)
		# return Word(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], datetime.combine(row[8], datetime.min.time()))

	def reset_all_states(self):
		for user in self.knownUsers:
			self.set_state(user, '0')