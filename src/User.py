import time
import fsm
from utilities import logging_utils
from random import shuffle
import logging
import translation
import BotMessageSender

class User:

	def __init__(self, user_id, database_reference, bot_controller_factory):
		logging_utils.setup_user_logger(user_id)
		self.logger = logging.getLogger('{}'.format(user_id))

		self.last_op_time = time.time()
		self.db = database_reference
		self.user_id = user_id
		self.username = self.db.get_username(self.user_id)
		self.native = self.db.get_native_language(self.user_id)

		self.bot_controller_factory = bot_controller_factory
		self.bot_controller = bot_controller_factory.get_bot_controller(user_id, self.native)



		self.temp_study_item = None
		self.temp_card = None
		self.temp_study_items_string_list = None
		self.temp_study_item_list = None
		self.temp_topics_list = None
		self.receive_queue = None
		self.cards_to_review = None
		self.temp_subject = None
		self.temp_user = None
		self.counter = None
		self.review_card_number = None
		self.pos = None

	def get_username(self):
		return self.username

	def get_native_language(self):
		return self.native

	def set_last_op_time(self):
		self.last_op_time = time.time()		

	def get_last_op_time(self):
		return self.last_op_time

	def set_native_language(self, language):
		if type(language) is str:
			language = translation.native_languages[language]
		self.native = language
		del self.bot_controller
		self.bot_controller = self.bot_controller_factory.get_bot_controller(self.user_id, self.native)
		return self.db.set_native_language(self.user_id, self.native)

	def get_state(self):
		st = self.db.get_state(self.user_id)
		ret = (st[0],)
		for i in range(1,2):
			if(st[i] == -1):
				break
			ret = ret + (st[i],)

		if len(ret) == 1:
			ret = ret[0]

		return ret


	def set_state(self, state):
		if not(type(state) is tuple):
			state = (state, -1)
		else:
			while len(state) < 2:
				state = state + (-1,)

		self.db.set_state(self.user_id, state[0], state[1])
		#print("{} NEW STATE {} {} {}   {}".format(self.user_id, state[0], state[1], state[2], time.time()))
		self.set_last_op_time()

	def not_locked(self):
		return self.get_state() != fsm.LOCKED

	def get_id(self):
		return self.user_id

	def get_cards_expired(self, now):
		cards = self.get_all_active_cards()
		ret = []
		for card in cards:
			if card.get_next_date() <= now.date():
				ret.append(card)
		shuffle(ret)
		ret.sort()
		return ret

	def reset_state_exception(self):
		self.logger.error("Exception! Had to restart {}".format(self.user_id))
		try:
			bot.send_message(self.user_id, "An error in the server ocurred, the operation was canceled")
		except Exception as e:
			self.logger.error("Can't send message")
		self.set_state(fsm.IDLE)
		self.set_card_waiting(0)


	'''
	========================================================
						  DB DELEGATION
	========================================================
	'''
	def get_highest_study_item_id(self):
		return self.db.get_highest_study_item_id(self.user_id)

	def add_study_item_deck(self, deck):
		return self.db.add_study_item_deck(deck)

	def erase_study_item(self, study_item_id):
		return self.db.erase_study_item(self.user_id, study_item_id)

	def get_study_item_deck(self, study_item_id):
		return self.db.get_study_item_deck(self.user_id, study_item_id)

	def get_study_items_on_topic(self, subject, topic):
		return self.db.get_study_items_on_topic(self.user_id, subject, topic)

	def get_active_study_items(self, subject, topic):
		return self.db.get_active_study_items(self.user_id, subject, topic)

	def is_study_item_active(self, study_item_id):
		return self.db.is_study_item_active(self.user_id, study_item_id)

	def set_study_item_active(self, study_item_id, active):
		return self.db.set_study_item_active(self.user_id, study_item_id, active)
		
	def check_study_item_existence(self, subject, topic, study_item):
		return self.db.check_study_item_existence(self.user_id, subject, topic, study_item)

	#==================USER ops==================
	def get_learning_words_limit(self):
		return self.db.get_learning_words_limit(self.user_id)

	def get_grade_waiting(self):
		return self.db.get_grade_waiting(self.user_id)

	def set_grade_waiting(self, grade):
		return self.db.set_grade_waiting(self.user_id, grade)

	def set_card_waiting(self, card_id):
		return self.db.set_card_waiting(self.user_id, card_id)

	def get_card_waiting(self):
		return self.db.get_card_waiting(self.user_id)

	def get_card_waiting_type(self):
		return self.db.get_card_waiting_type(self.user_id)

	def set_card_waiting_type(self, card_waiting_type):
		return self.db.set_card_waiting_type(self.user_id, card_waiting_type)

	def get_cards_per_hour(self):
		return self.db.get_cards_per_hour(self.user_id)

	def set_cards_per_hour(self, cards_per_hour):
		return self.db.set_cards_per_hour(self.user_id, cards_per_hour)

	def get_active(self):
		return self.db.get_active(self.user_id)

	def set_active(self, active):
		return self.db.set_active(self.user_id, active)

	def get_public(self):
		return self.db.get_public(self.user_id)

	def set_public(self, public):
		return self.db.set_public(self.user_id, public)

	#==================TOPIC ops==================

	def erase_topic(self, subject, topic):
		return self.db.erase_topic(self.user_id, subject, topic)

	def get_topics(self, subject):
		return self.db.get_topics(self.user_id, subject)

	def get_only_topics(self, subject):
		ret = []
		topics = self.get_topics(subject)
		for topic in topics:
			ret.append(topic[0])
		return ret

	def get_active_topics(self, subject):
		return self.db.get_active_topics(self.user_id, subject)

	def is_topic_active(self, subject, topic):
		return self.db.is_topic_active(self.user_id, subject, topic)

	def set_topic_active(self, subject, topic, active):
		return self.db.set_topic_active(self.user_id, subject, topic, active)

	#=================CARD ops===================

	def get_highest_card_id(self):
		return self.db.get_highest_card_id(self.user_id)

	def add_card(self, card):
		return self.db.add_card(card)

	def get_card(self, card_id):
		return self.db.get_card(self.user_id, card_id)

	def get_cards_on_topic(self, subject, topic):
		return self.db.get_cards_on_topic(self.user_id, subject, topic)

	def get_all_active_cards(self):
		return self.db.get_all_active_cards(self.user_id)

	def erase_card(self, card_id):
		return self.db.erase_card(self.user_id, card_id)

	def set_supermemo_data(self, card):
		return self.db.set_supermemo_data(card)

	def check_card_existence(self, card_id):
		return self.db.check_card_existence(self.user_id, card_id)

	def is_card_active(self, card_id):
		return self.db.is_card_active(self.user_id, card_id)

	def set_card_active(self, card_id, active):
		return self.db.set_card_active(self.user_id, card_id, active)

	#==================Subject ops==================
	def erase_subject(self, subject):
		return self.db.erase_subject(self.user_id, subject)

	def get_subjects(self):
		return self.db.get_subjects(self.user_id)

	def get_only_subjects(self):
		ret = []
		subjects = self.get_subjects()
		for subject in subjects:
			ret.append(subject[0])
		return ret

	def get_active_subjects(self):
		return self.db.get_active_subjects(self.user_id)

	def is_subject_active(self, subject):
		return self.db.is_subject_active(self.user_id,subject)

	def set_subject_active(self, subject, active):
		return self.db.set_subject_active(self.user_id, subject, active)
	
	'''
	========================================================
				  	BOT CONTROLLER DELEGATION
	========================================================
	'''

	def save_image(self, image_msg, path, image_name):
		return self.bot_controller.save_image(image_msg, path, image_name)

	def save_audio(self, audio_msg, path, audio_name):
		return self.bot_controller.save_audio(audio_msg, path, audio_name)

	def save_voice(self, voice_msg, path, voice_name):
		return self.bot_controller.save_voice(voice_msg, path, voice_name)	

	def send_card_answer(self, card):
		return self.bot_controller.send_card_answer(card)		

	def send_card_question(self, card):
		return self.bot_controller.send_card_question(card)

	def send_card_query(self, card, card_type = 'Review', number = None):
		return self.bot_controller.send_card_query(card, card_type, number)		

	def parse_string_keyboard_ans(ans):
		return self.bot_controller.parse_string_keyboard_ans(ans)	
	
	def parse_selection_inline_keyboard_ans(callback_data):
		return self.bot_controller.parse_selection_inline_keyboard_ans(callback_data)
	
	def parse_keyboard_ans(self, msg):
		return self.bot_controller.parse_keyboard_ans(msg)
	
	def send_string_keyboard(self, txt, options, txt_args=(), markdown_options=None, translate_options=False, add_default_keyboard=True, first_option_value=1, width=3, parse="Markdown"):
		return self.bot_controller.send_string_keyboard(txt, options, txt_args, markdown_options, translate_options, add_default_keyboard, first_option_value, width, parse)

	def send_selection_inline_keyboard(self, txt, options, txt_args=(), translate_options=False, empty_keyboard_text=None, no_empty_flag=False, btn_set=None, width=3, parse="Markdown"):
		if btn_set == None:
			btn_set = set()
		return self.bot_controller.send_selection_inline_keyboard(txt, options, txt_args, translate_options, empty_keyboard_text, no_empty_flag, btn_set, width, parse)
	
	def edit_selection_inline_keyboard(self, txt, parse="Markdown"):		
		return self.bot_controller.edit_selection_inline_keyboard(txt, parse)
	
	def send_message(self, txt, txt_args=(), markup=BotMessageSender.keyboard_remove(), translate_flag=True, parse='Markdown', disable_web_preview=True):
		return self.bot_controller.send_message(txt, txt_args, markup, translate_flag, parse, disable_web_preview)

	def send_photo(self, path, markup=BotMessageSender.keyboard_remove()):
		return self.bot_controller.send_photo(path, markup)	
	
	def send_voice(self, path, markup=BotMessageSender.keyboard_remove()):
		return self.bot_controller.send_voice(path, markup)

	def send_navigation_string_keyboard(self, txt, options, end_btn, back_btn=None, markdown_options=None, txt_args=(), translate_options=False, first_option_value=1, parse="Markdown"):
		return self.bot_controller.send_navigation_string_keyboard(txt, options, end_btn, back_btn, markdown_options, txt_args, translate_options, first_option_value, parse)


	def send_all_cards(self, study_item_deck, except_type=""):
		return self.bot_controller.send_all_cards(study_item_deck, except_type)