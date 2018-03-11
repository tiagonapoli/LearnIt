'''Finite State Machine'''


'''States'''
LOCKED = 999
IDLE = 0   
WAITING_ANS = 1
ADD_ITEM = 2
WAITING_POLL_ANS = 3
GET_SUBJECT = 4
GET_TOPIC = 5
GET_STUDY_ITEM = 6
SEND_IMAGE = 7
SEND_AUDIO = 8
SEND_TEXT = 9
RELATE_MENU = 10
LIST = 11
ERASE_SUBJECTS = 12
SELECT_SUBJECTS = 13
REVIEW = 14
GET_TOPICS = 15
GET_NUMBER = 16
WAITING_CARD_ANS = 17
SETTINGS = 18
GET_OPTION = 19
CARDS_PER_HOUR = 20
COPY_FROM_USER = 21
GET_USER = 22
SELECT_TOPICS = 23
GET_IMAGE = 24
GET_OVERWRITE = 25
GET_CONTINUE = 26
SETUP_USER = 27
GET_LANGUAGE = 28
ERASE = 29
SUBJECT_ERASE = 30
TOPIC_ERASE = 31
ITEM_ERASE = 32
SELECT = 33
SELECT_TRAINING = 34


'''FSM'''

#=====================IDLE MENU=====================
next_state = {	
	IDLE:   {'setup user': (SETUP_USER, GET_LANGUAGE),
			 'card_query': WAITING_ANS,
      		 'add_item': (ADD_ITEM, GET_SUBJECT),
      		 'list': (LIST, GET_SUBJECT),
      		 'erase': (ERASE, GET_OPTION),
      		 'review' : (REVIEW, GET_SUBJECT),
      		 'settings' : (SETTINGS, GET_OPTION),
      		 'copy_from_user': (COPY_FROM_USER, GET_USER),
      		 'select_training': (SELECT_TRAINING, GET_SUBJECT)}
}


#=====================CARD ANSWERING=====================
next_state.update({
	WAITING_ANS: WAITING_POLL_ANS,
	WAITING_POLL_ANS: {'done': IDLE,
					   'error': WAITING_POLL_ANS},
})


#=====================ADD STUDY_ITEM=====================
next_state.update({
	(ADD_ITEM, GET_SUBJECT): {'done': (ADD_ITEM, GET_TOPIC),
							  'error': (ADD_ITEM, GET_SUBJECT)},
	(ADD_ITEM, GET_TOPIC): {'done': (ADD_ITEM, GET_STUDY_ITEM),
							'error': (ADD_ITEM, GET_TOPIC)},
	(ADD_ITEM, GET_STUDY_ITEM): {'done': (ADD_ITEM, RELATE_MENU),
						   'error_idle': IDLE,
						   'study item 1': (ADD_ITEM, GET_IMAGE),
						   'error': (ADD_ITEM, GET_STUDY_ITEM)},
	(ADD_ITEM, GET_IMAGE): {'done': (ADD_ITEM, RELATE_MENU)},
	(ADD_ITEM, RELATE_MENU): {'2': (ADD_ITEM, SEND_AUDIO),
							  '1': (ADD_ITEM, SEND_IMAGE),
							  '0': (ADD_ITEM, SEND_TEXT),
			  				  'continue': (ADD_ITEM, RELATE_MENU),
			  				  'done': (ADD_ITEM, GET_CONTINUE)},
	(ADD_ITEM, SEND_IMAGE): { 'error': (ADD_ITEM, SEND_IMAGE),
							  '2': (ADD_ITEM, SEND_AUDIO),
							  '0': (ADD_ITEM, SEND_TEXT),
			  				  'done': (ADD_ITEM, GET_CONTINUE)},
	(ADD_ITEM, SEND_AUDIO): {'error': (ADD_ITEM, SEND_AUDIO),
							 '1': (ADD_ITEM, SEND_IMAGE),
							 '0': (ADD_ITEM, SEND_TEXT),
			  				 'done': (ADD_ITEM, GET_CONTINUE)},
	(ADD_ITEM, SEND_TEXT): {'error': (ADD_ITEM, SEND_TEXT),
							'1': (ADD_ITEM, SEND_IMAGE),
							'2': (ADD_ITEM, SEND_AUDIO),
			  				'done': (ADD_ITEM, GET_CONTINUE)},
	(ADD_ITEM, GET_CONTINUE): {'done': IDLE,
							   'error': (ADD_ITEM, GET_CONTINUE),
							   'continue': (ADD_ITEM, GET_STUDY_ITEM)}
})


#=====================LIST=====================
next_state.update({
	(LIST, GET_SUBJECT): {'Next': (LIST, GET_TOPIC),
						  'no subjects': IDLE,
						  'End': IDLE,
						  'Error': (LIST, GET_SUBJECT)},
	(LIST, GET_TOPIC): {'Next': (LIST, GET_STUDY_ITEM),
						'Back': (LIST, GET_SUBJECT),
						'End': IDLE,
						'Error': (LIST, GET_TOPIC)},
	(LIST, GET_STUDY_ITEM): {'End' : IDLE,
							 'Back' : (LIST, GET_TOPIC),
							 'Error': (LIST, GET_STUDY_ITEM),
							 'Next' : (LIST, GET_STUDY_ITEM)}
})


#=====================ERASE STUDY_ITEMS=====================
next_state.update({
	(ERASE, GET_OPTION): {'error': (ERASE, GET_OPTION),
						  'subject': (SUBJECT_ERASE, SELECT),
						  'topic': (TOPIC_ERASE, GET_SUBJECT),
						  'study_item': (ITEM_ERASE, GET_SUBJECT)},
	(SUBJECT_ERASE, SELECT):  {'continue': (SUBJECT_ERASE, SELECT),
							   'done': IDLE},
	(TOPIC_ERASE, GET_SUBJECT): {'done': (TOPIC_ERASE, SELECT),
							  	  'error': (TOPIC_ERASE, GET_SUBJECT)},
	(TOPIC_ERASE, SELECT): {'continue': (TOPIC_ERASE, SELECT),
							'done': IDLE},
	(ITEM_ERASE, GET_SUBJECT): {'done': (ITEM_ERASE, GET_TOPIC),
							     'error': (ITEM_ERASE, GET_SUBJECT)},
	(ITEM_ERASE, GET_TOPIC): {'done': (ITEM_ERASE, SELECT),
							  'error': (ITEM_ERASE, GET_TOPIC)},	
	(ITEM_ERASE, SELECT): {'continue': (ITEM_ERASE, SELECT),
						   'done': IDLE}
})

#=====================ERASE SUBJECTS=====================
next_state.update({
	(ERASE_SUBJECTS, SELECT_SUBJECTS): {'continue': (ERASE_SUBJECTS, SELECT_SUBJECTS),
								  		  'done': IDLE}
})

#=====================TOPIC REVIEW=====================
next_state.update({
	(REVIEW, GET_SUBJECT) : {'error' : (REVIEW, GET_SUBJECT),
							  'no topics' : IDLE,
							  'done' : (REVIEW, GET_TOPICS)},
	(REVIEW, GET_TOPICS) : {'continue' : (REVIEW, GET_TOPICS),
							'done' : (REVIEW, GET_NUMBER)},
	(REVIEW, GET_NUMBER) : {'error' : (REVIEW, GET_NUMBER),
							'done' : (REVIEW, WAITING_CARD_ANS)},
	(REVIEW, WAITING_CARD_ANS) : {'continue' : (REVIEW, WAITING_CARD_ANS),
								  'done' : IDLE}
})

#=====================SELECT TRAINING=====================
next_state.update({
	(SELECT_TRAINING, GET_SUBJECT) : {'error' : (SELECT_TRAINING, GET_SUBJECT),
							  		  'no topics' : IDLE,
							  		  'done' : (SELECT_TRAINING, GET_TOPICS)},
	(SELECT_TRAINING, GET_TOPICS) : {'continue' : (SELECT_TRAINING, GET_TOPICS),
									 'done' : IDLE},
})


#=====================SETTINGS=====================
next_state.update({
	(SETTINGS, GET_OPTION) : {'error' : (SETTINGS, GET_OPTION),
							  'change language': (SETTINGS, GET_LANGUAGE),
							  'cards per hour' : (SETTINGS, CARDS_PER_HOUR)},
	(SETTINGS, CARDS_PER_HOUR) : {'error' : (SETTINGS, CARDS_PER_HOUR),
								  'done' : IDLE},
	(SETTINGS, GET_LANGUAGE): {'error': (SETTINGS, GET_LANGUAGE),
							  'done': IDLE}
})

#=====================COPY STUDY_ITEMS=====================
next_state.update({
	(COPY_FROM_USER, GET_USER): {'done': (COPY_FROM_USER, GET_SUBJECT),
							 'error': IDLE},
	(COPY_FROM_USER, GET_SUBJECT): {'done': (COPY_FROM_USER, SELECT_TOPICS),
							   	 'error': (COPY_FROM_USER, GET_SUBJECT),
							   	 'no topics': IDLE},
	(COPY_FROM_USER, SELECT_TOPICS): {'done': (COPY_FROM_USER, GET_OVERWRITE),
						   		  'continue': (COPY_FROM_USER, SELECT_TOPICS)},
	(COPY_FROM_USER, GET_OVERWRITE): {'done': IDLE,
						   		  'error': (COPY_FROM_USER, GET_OVERWRITE)}	
})

#=====================SETUP USER=====================
next_state.update({
	(SETUP_USER, GET_LANGUAGE): {'error': (SETUP_USER, GET_LANGUAGE),
								 'done': IDLE}
})
