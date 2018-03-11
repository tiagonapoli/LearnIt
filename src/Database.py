import psycopg2
import os
import logging

import database_ops.study_item_ops
import database_ops.user_ops
import database_ops.topic_ops
import database_ops.subject_ops
import database_ops.card_ops


class Database():

	def __init__(self, debug_mode):
		#try:
		arq = None
		if debug_mode:
			arq = open("../credentials/connect_str_debug.txt", "r")
		else:
			arq = open("../credentials/connect_str.txt", "r")
		connect_str = arq.read()
		arq.close()
		self.DB_NAME = connect_str.split()[0][7:]
		self.DB_USER_NAME = connect_str.split()[1][5:]
		self.logger = logging.getLogger('db_api')

		#print("DB_NAME: {}".format(self.DB_NAME))
		#print("DB_USER_NAME: {}".format(self.DB_USER_NAME))
		self.conn = psycopg2.connect(connect_str)
		self.cursor = self.conn.cursor()
		
		self.study_item_ops = database_ops.study_item_ops.StudyItemOps(self.conn, self.cursor, debug_mode)
		self.user_ops = database_ops.user_ops.UserOps(self.conn, self.cursor, debug_mode)
		self.topic_ops = database_ops.topic_ops.TopicOps(self.conn, self.cursor, debug_mode)
		self.subject_ops = database_ops.subject_ops.SubjectOps(self.conn, self.cursor, debug_mode)
		self.card_ops = database_ops.card_ops.CardOps(self.conn, self.cursor, debug_mode)


	def __del__(self):
		self.conn.close()
		self.cursor.close()


	#==================StudyItem ops==================
	def get_highest_study_item_id(self, user_id):
		return self.study_item_ops.get_highest_study_item_id(user_id)

	def add_study_item_deck(self, deck):
		return self.study_item_ops.add_study_item_deck(deck)

	def erase_study_item(self, user_id, study_item_id):
		return self.study_item_ops.erase_study_item(user_id, study_item_id)

	def get_study_item_deck(self, user_id, study_item_id):
		return self.study_item_ops.get_study_item_deck(user_id, study_item_id)

	def get_study_items_on_topic(self, user_id, subject, topic):
		return self.study_item_ops.get_study_items_on_topic(user_id, subject, topic)

	def get_active_study_items(self, user_id, subject, topic):
		return self.study_item_ops.get_active_study_items(user_id, subject, topic)

	def is_study_item_active(self, user_id, study_item_id):
		return self.study_item_ops.is_study_item_active(user_id, study_item_id)

	def set_study_item_active(self, user_id, study_item_id, active):
		return self.study_item_ops.set_study_item_active(user_id, study_item_id, active)
		
	def check_study_item_existence(self, user_id, subject, topic, study_item):
		return self.study_item_ops.check_study_item_existence(user_id, subject, topic, study_item)

	#==================USER ops==================
	def get_state(self, user_id):
		return self.user_ops.get_state(user_id)

	def set_state(self, user_id, state1, state2):
		return self.user_ops.set_state(user_id, state1, state2)
	
	def add_user(self, user_id, username):
		return self.user_ops.add_user(user_id, username)

	def get_known_users(self):
		return self.user_ops.get_known_users()

	def get_learning_words_limit(self, user_id):
		return self.user_ops.get_learning_words_limit(user_id)

	def get_grade_waiting(self, user_id):
		return self.user_ops.get_grade_waiting(user_id)

	def set_grade_waiting(self, user_id, grade):
		return self.user_ops.set_grade_waiting(user_id, grade)

	def set_card_waiting(self, user_id, card_id):
		return self.user_ops.set_card_waiting(user_id, card_id)

	def get_card_waiting(self, user_id):
		return self.user_ops.get_card_waiting(user_id)

	def get_card_waiting_type(self, user_id):
		return self.user_ops.get_card_waiting_type(user_id)

	def set_card_waiting_type(self, user_id, card_waiting_type):
		return self.user_ops.set_card_waiting_type(user_id, card_waiting_type)

	def get_cards_per_hour(self, user_id):
		return self.user_ops.get_cards_per_hour(user_id)

	def set_cards_per_hour(self, user_id, cards_per_hour):
		return self.user_ops.set_cards_per_hour(user_id, cards_per_hour)

	def get_active(self, user_id):
		return self.user_ops.get_active(user_id)

	def set_active(self, user_id, active):
		return self.user_ops.set_active(user_id, active)

	def get_id_by_username(self, username):
		return self.user_ops.get_id_by_username(username)	

	def get_public(self, user_id):
		return self.user_ops.get_public(user_id)

	def set_public(self, user_id, public):
		return self.user_ops.set_public(user_id, public)

	def get_username(self, user_id):
		return self.user_ops.get_username(user_id)

	def get_native_language(self, user_id):
		return self.user_ops.get_native_language(user_id)

	def set_native_language(self, user_id, language):
		return self.user_ops.set_native_language(user_id, language)

	#==================TOPIC ops==================

	def erase_topic(self, user_id, subject, topic):
		return self.topic_ops.erase_topic(user_id, subject, topic)

	def get_topics(self, user_id, subject):
		return self.topic_ops.get_topics(user_id, subject)

	def get_active_topics(self, user_id, subject):
		return self.topic_ops.get_active_topics(user_id, subject)

	def is_topic_active(self, user_id, subject, topic):
		return self.topic_ops.is_topic_active(user_id, subject, topic)

	def set_topic_active(self, user_id, subject, topic, active):
		return self.topic_ops.set_topic_active(user_id, subject, topic, active)

	#=================CARD ops===================

	def get_highest_card_id(self, user_id):
		return self.card_ops.get_highest_card_id(user_id)

	def add_card(self, card):
		return self.card_ops.add_card(card)

	def get_card(self, user_id, card_id):
		return self.card_ops.get_card(user_id, card_id)

	def get_cards_on_topic(self, user_id, subject, topic):
		return self.card_ops.get_cards_on_topic(user_id, subject, topic)

	def get_all_active_cards(self, user_id):
		return self.card_ops.get_all_active_cards(user_id)

	def erase_card(self, user_id, card_id):
		return self.card_ops.erase_card(user_id, card_id)

	def set_supermemo_data(self, card):
		return self.card_ops.set_supermemo_data(card)

	def check_card_existence(self, user_id, card_id):
		return self.card_ops.check_card_existence(user_id, card_id)

	def is_card_active(self, user_id, card_id):
		return self.card_ops.is_card_active(user_id, card_id)

	def set_card_active(self, user_id, card_id, active):
		return self.card_ops.set_card_active(user_id, card_id, active)

	#==================Subject ops==================
	def erase_subject(self, user_id, subject):
		return self.subject_ops.erase_subject(user_id, subject)

	def get_subjects(self, user_id):
		return self.subject_ops.get_subjects(user_id)

	def get_active_subjects(self, user_id):
		return self.subject_ops.get_active_subjects(user_id)

	def is_subject_active(self, user_id, subject):
		return self.subject_ops.is_subject_active(user_id,subject)

	def set_subject_active(self, user_id, subject, active):
		return self.subject_ops.set_subject_active(user_id, subject, active)




	def backup(self, PATH):
		try:
			if not os.path.exists(PATH):
				os.mkdir(PATH)
			if not os.path.exists(PATH + "/tables/"):
				os.mkdir(PATH + "/tables/")
			aux_path = PATH + "/tables"
			os.system("psql -U {} -d {} -c \"Copy (Select * From users) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/users.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From cards) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/cards.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From subjects) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/subjects.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From topics) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/topics.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			os.system("psql -U {} -d {} -c \"Copy (Select * From study_items) To STDOUT With CSV HEADER DELIMITER ',';\" > {}/study_items.csv".format(self.DB_USER_NAME, self.DB_NAME, aux_path))
			return "Backup made successfully"
		except Exception as e:
			print(e);
			return "Backup failed"

if __name__ == '__main__':
	
	from Flashcard import StudyItemDeck, Card, StudyItemInfo

	test = Database(1)

	#create files to debug
	try:
		os.makedirs('../data_debug/')
	except:
		pass
	file = open('../data_debug/fogao.jpg', 'w')
	file.write('olar')
	file.close()

	file = open('../data_debug/wardrobe.mp3', 'w')
	file.write('olar2')
	file.close()

	file = open('../data_debug/wardrobe.jpg', 'w')
	file.write('olar3')
	file.close()

	test.add_user(1, 'tiago')
	test.add_user(2, 'camargo')

	'''
	Card(user_id=, study_item_id=, active=, 
		 subject=, topic=, study_item=, study_item_type=,
		 card_id=, 
		 question=None, question_type=None)
	'''

	card1 =  Card(user_id=1, study_item_id=1, active=1, 
				  subject='Portugues', topic='Kitchen', study_item='Fogão', study_item_type=0,
				  card_id= 1, 
				  question='Where you cook food', question_type='text')

	card2 =  Card(user_id=1, study_item_id=1, active=1, 
			  subject='Portugues', topic='Kitchen', study_item='Fogão', study_item_type=0,
			  card_id= 2, 
			  question='../data_debug/fogao.jpg', question_type='image')

	deck1 = StudyItemDeck.from_cards([card1, card2])
	test.add_study_item_deck(deck1)

	card1 =  Card(user_id=1, study_item_id=2, active=1, 
				  subject='Portugues', topic='Bedroom', study_item='../data_debug/wardrobe.jpg', study_item_type=1,
				  card_id= 3, 
				  question='Where you keep your clothes', question_type='text')

	card2 =  Card(user_id=1, study_item_id=2, active=1, 
			  subject='Portugues', topic='Bedroom', study_item='../data_debug/wardrobe.jpg', study_item_type=1,
			  card_id= 4, 
			  question='../data_debug/wardrobe.mp3', question_type='audio')

	deck2 = StudyItemDeck.from_cards([card1, card2])
	test.add_study_item_deck(deck2)


	print("======= Get study item deck =======")
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_study_item_deck(user_id=1, study_item_id=1))


	print("======= Get active study item deck COM STUDY_ITEM 2 =======")
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom')[0])
	print("======= Get active study item deck SEM STUDY_ITEM 2 =======")
	test.set_study_item_active(user_id=1, study_item_id=2, active=0)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))


	print("======= Get active topics SEM KITCHEN =======")
	test.set_topic_active(user_id=1, subject='Portugues', topic='Kitchen', active=0)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_topics(user_id=1, subject='Portugues'))

	print("======= Get active subjects SEM Portuges =======")
	test.set_subject_active(user_id=1, subject='Portugues', active=0)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_subjects(user_id=1))
	print(test.get_active_topics(user_id=1, subject='Portugues'))
	print(test.get_all_active_cards(user_id=1))


	print("======= Get active subjects com Portuges =======")
	test.set_subject_active(user_id=1, subject='Portugues', active=1)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_subjects(user_id=1))
	print(test.get_active_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))
	print(test.get_all_active_cards(user_id=1))

	print("======= Get active subjects com Kitchen =======")
	test.set_topic_active(user_id=1, subject='Portugues', topic='Kitchen', active=1)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_subjects(user_id=1))
	print(test.get_active_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))
	print(test.get_all_active_cards(user_id=1))


	print("======= Erase Deck 1 - SEM KITCHEN =======")
	test.erase_study_item(user_id=1, study_item_id=1)
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))
	print(test.get_all_active_cards(user_id=1))

	print("======= Erase Topic Bedroom 1 - SEM NADA =======")
	test.erase_topic(user_id=1,subject='Portugues', topic='Bedroom')
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))
	print(test.get_all_active_cards(user_id=1))


	file = open('../data_debug/wardrobe.mp3', 'w')
	file.write('olar2')
	file.close()

	file = open('../data_debug/wardrobe.jpg', 'w')
	file.write('olar3')
	file.close()


	card1 =  Card(user_id=1, study_item_id=2, active=1, 
				  subject='Portugues', topic='Bedroom', study_item='../data_debug/wardrobe.jpg', study_item_type=1,
				  card_id= 3, 
				  question='Where you keep your clothes', question_type='text')

	card2 =  Card(user_id=1, study_item_id=2, active=1, 
			  subject='Portugues', topic='Bedroom', study_item='../data_debug/wardrobe.jpg', study_item_type=1,
			  card_id= 4, 
			  question='../data_debug/wardrobe.mp3', question_type='audio')

	deck2 = StudyItemDeck.from_cards([card1, card2])
	test.add_study_item_deck(deck2)

	print("======= Erase subject Portuges - SEM NADA =======")
	test.erase_subject(user_id=1,subject='Portugues')
	print(test.get_subjects(user_id=1))
	print(test.get_topics(user_id=1, subject='Portugues'))
	print(test.get_active_study_items(user_id=1, subject='Portugues', topic='Bedroom'))
	print(test.get_all_active_cards(user_id=1))


