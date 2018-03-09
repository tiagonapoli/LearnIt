'''Finite State Machine'''


'''States'''
LOCKED = 999
IDLE = 0   
WAITING_ANS = 1
ADD_ITEM = 2
ADD_SUBJECT = 3
WAITING_POLL_ANS = 5
GET_SUBJECT = 6
GET_TOPIC = 7
GET_STUDY_ITEM = 8
SEND_IMAGE = 9
SEND_AUDIO = 11
SEND_TEXT = 13
RELATE_MENU = 15
LIST = 17
ERASE_STUDY_ITEMS = 18
SELECT_STUDY_ITEMS = 19
ERASE_SUBJECTS = 20
SELECT_SUBJECTS = 21
REVIEW = 22	
GET_TOPICS = 23
GET_NUMBER = 24
WAITING_CARD_ANS = 25
SETTINGS = 26
GET_OPTION = 27
CARDS_PER_HOUR = 28
COPY_STUDY_ITEMS = 29
GET_USER = 30
SELECT_TOPICS = 31
GET_IMAGE = 32
GET_OVERWRITE = 33
GET_CONTINUE = 34
SETUP_USER = 35
GET_LANGUAGE = 36


'''FSM'''

#=====================IDLE MENU=====================
next_state = {	
	IDLE:   {'setup user': (SETUP_USER, GET_LANGUAGE),
			 'card_query': WAITING_ANS,
      		 'add_item': (ADD_ITEM, GET_SUBJECT),
      		 'list': (LIST, GET_SUBJECT),
      		 'erase_words': (ERASE_STUDY_ITEMS, GET_SUBJECT),
      		 'erase_languages': (ERASE_SUBJECTS, SELECT_SUBJECTS),
      		 'review' : (REVIEW, GET_SUBJECT),
      		 'settings' : (SETTINGS, GET_OPTION),
      		 'copy_words': (COPY_STUDY_ITEMS, GET_USER)}
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
	(LIST, GET_STUDY_ITEM): {'Done' : IDLE,
							 'Back' : (LIST, GET_TOPIC),
							 'Error': (LIST, GET_STUDY_ITEM),
							 'Next' : (LIST, GET_STUDY_ITEM)}
})


#=====================ERASE STUDY_ITEMS=====================
next_state.update({
	(ERASE_STUDY_ITEMS, GET_SUBJECT): {'done': (ERASE_STUDY_ITEMS, GET_TOPIC),
								 'no topics': IDLE,
								 'error': (ERASE_STUDY_ITEMS, GET_SUBJECT)},
	(ERASE_STUDY_ITEMS, GET_TOPIC): {'done': (ERASE_STUDY_ITEMS, SELECT_STUDY_ITEMS),
							  'error': (ERASE_STUDY_ITEMS, GET_TOPIC)},
	(ERASE_STUDY_ITEMS, SELECT_STUDY_ITEMS): {'continue': (ERASE_STUDY_ITEMS, SELECT_STUDY_ITEMS),
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
	(COPY_STUDY_ITEMS, GET_USER): {'done': (COPY_STUDY_ITEMS, GET_SUBJECT),
							 'error': IDLE},
	(COPY_STUDY_ITEMS, GET_SUBJECT): {'done': (COPY_STUDY_ITEMS, SELECT_TOPICS),
							   	 'error': (COPY_STUDY_ITEMS, GET_SUBJECT),
							   	 'no topics': IDLE},
	(COPY_STUDY_ITEMS, SELECT_TOPICS): {'done': (COPY_STUDY_ITEMS, GET_OVERWRITE),
						   		  'continue': (COPY_STUDY_ITEMS, SELECT_TOPICS)},
	(COPY_STUDY_ITEMS, GET_OVERWRITE): {'done': IDLE,
						   		  'error': (COPY_STUDY_ITEMS, GET_OVERWRITE)}	
})

#=====================SETUP USER=====================
next_state.update({
	(SETUP_USER, GET_LANGUAGE): {'error': (SETUP_USER, GET_LANGUAGE),
								 'done': IDLE}
})
