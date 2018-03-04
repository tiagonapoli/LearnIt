'''Finite State Machine'''


'''States'''
LOCKED = 999
IDLE = 0   
WAITING_ANS = 1
ADD_WORD = 2
ADD_LANGUAGE = 3
WAITING_POLL_ANS = 5
GET_LANGUAGE = 6
GET_TOPIC = 7
GET_WORD = 8
SEND_IMAGE = 9
SEND_AUDIO = 11
SEND_TEXT = 13
RELATE_MENU = 15
LIST_WORDS = 17
ERASE_WORDS = 18
SELECT_WORDS = 19
ERASE_LANGUAGES = 20
SELECT_LANGUAGES = 21
REVIEW = 22	
GET_TOPICS = 23
GET_NUMBER = 24
WAITING_CARD_ANS = 25
SETTINGS = 26
GET_OPTION = 27
CARDS_PER_HOUR = 28
COPY_WORDS = 29
GET_USER = 30
SELECT_TOPICS = 31
GET_IMAGE = 32
GET_OVERWRITE = 33
GET_CONTINUE = 34
SETUP_USER = 35


'''FSM'''

#=====================IDLE MENU=====================
next_state = {	
	IDLE:   {'setup user': (SETUP_USER, GET_LANGUAGE),
			 'card_query': WAITING_ANS,
      		 'add_word': (ADD_WORD, GET_LANGUAGE),
      		 'add_language': ADD_LANGUAGE,
      		 'list_words': (LIST_WORDS, GET_LANGUAGE),
      		 'list_languages': IDLE,
      		 'erase_words': (ERASE_WORDS, GET_LANGUAGE),
      		 'erase_languages': (ERASE_LANGUAGES, SELECT_LANGUAGES),
      		 'review' : (REVIEW, GET_LANGUAGE),
      		 'settings' : (SETTINGS, GET_OPTION),
      		 'copy_words': (COPY_WORDS, GET_USER)}
}


#=====================CARD ANSWERING=====================
next_state.update({
	WAITING_ANS: WAITING_POLL_ANS,
	WAITING_POLL_ANS: {'done': IDLE,
					   'error': WAITING_POLL_ANS},
})


#=====================ADD WORD=====================
next_state.update({
	(ADD_WORD, GET_LANGUAGE): {'done': (ADD_WORD, GET_TOPIC),
							   'error': (ADD_WORD, GET_LANGUAGE)},
	(ADD_WORD, GET_TOPIC): {'done': (ADD_WORD, GET_WORD),
							'error': (ADD_WORD, GET_TOPIC)},
	(ADD_WORD, GET_WORD): {'done': (ADD_WORD, RELATE_MENU),
						   'error_idle': IDLE,
						   'word img': (ADD_WORD, GET_IMAGE),
						   'error': (ADD_WORD, GET_WORD)},
	(ADD_WORD, GET_IMAGE): {'done': (ADD_WORD, RELATE_MENU)},
	(ADD_WORD, RELATE_MENU): {'2': (ADD_WORD, SEND_AUDIO),
							  '1': (ADD_WORD, SEND_IMAGE),
							  '0': (ADD_WORD, SEND_TEXT),
			  				  'continue': (ADD_WORD, RELATE_MENU),
			  				  'done': (ADD_WORD, GET_CONTINUE)},
	(ADD_WORD, SEND_IMAGE): { 'error': (ADD_WORD, SEND_IMAGE),
							  '2': (ADD_WORD, SEND_AUDIO),
							  '0': (ADD_WORD, SEND_TEXT),
			  				  'done': (ADD_WORD, GET_CONTINUE)},
	(ADD_WORD, SEND_AUDIO): {'error': (ADD_WORD, SEND_AUDIO),
							 '1': (ADD_WORD, SEND_IMAGE),
							 '0': (ADD_WORD, SEND_TEXT),
			  				 'done': (ADD_WORD, GET_CONTINUE)},
	(ADD_WORD, SEND_TEXT): {'error': (ADD_WORD, SEND_TEXT),
							'1': (ADD_WORD, SEND_IMAGE),
							'2': (ADD_WORD, SEND_AUDIO),
			  				'done': (ADD_WORD, GET_CONTINUE)},
	(ADD_WORD, GET_CONTINUE): {'done': IDLE,
							   'error': (ADD_WORD, GET_CONTINUE),
							   'continue': (ADD_WORD, GET_WORD)}
})


#=====================ADD LANGUAGE=====================
next_state.update({
	ADD_LANGUAGE: {'done': IDLE,
				   'error': ADD_LANGUAGE}
})


#=====================LIST WORDS=====================
next_state.update({
	(LIST_WORDS, GET_LANGUAGE): {'done': (LIST_WORDS, GET_TOPIC),
								 'no topics': IDLE,
								 'error': (LIST_WORDS, GET_LANGUAGE)},
	(LIST_WORDS, GET_TOPIC): {'done': (LIST_WORDS, GET_WORD),
							  'error': (LIST_WORDS, GET_TOPIC)},
	(LIST_WORDS, GET_WORD): {'done' : IDLE,
							 'error': (LIST_WORDS, GET_WORD),
							 'continue' : (LIST_WORDS, GET_WORD)}
})


#=====================ERASE WORDS=====================
next_state.update({
	(ERASE_WORDS, GET_LANGUAGE): {'done': (ERASE_WORDS, GET_TOPIC),
								 'no topics': IDLE,
								 'error': (ERASE_WORDS, GET_LANGUAGE)},
	(ERASE_WORDS, GET_TOPIC): {'done': (ERASE_WORDS, SELECT_WORDS),
							  'error': (ERASE_WORDS, GET_TOPIC)},
	(ERASE_WORDS, SELECT_WORDS): {'continue': (ERASE_WORDS, SELECT_WORDS),
								  'done': IDLE}
})

#=====================ERASE LANGUAGES=====================
next_state.update({
	(ERASE_LANGUAGES, SELECT_LANGUAGES): {'continue': (ERASE_LANGUAGES, SELECT_LANGUAGES),
								  		  'done': IDLE}
})

#=====================TOPIC REVIEW=====================
next_state.update({
	(REVIEW, GET_LANGUAGE) : {'error' : (REVIEW, GET_LANGUAGE),
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

#=====================COPY WORDS=====================
next_state.update({
	(COPY_WORDS, GET_USER): {'done': (COPY_WORDS, GET_LANGUAGE),
							 'error': IDLE},
	(COPY_WORDS, GET_LANGUAGE): {'done': (COPY_WORDS, SELECT_TOPICS),
							   	 'error': (COPY_WORDS, GET_LANGUAGE),
							   	 'no topics': IDLE},
	(COPY_WORDS, SELECT_TOPICS): {'done': (COPY_WORDS, GET_OVERWRITE),
						   		  'continue': (COPY_WORDS, SELECT_TOPICS)},
	(COPY_WORDS, GET_OVERWRITE): {'done': IDLE,
						   		  'error': (COPY_WORDS, GET_OVERWRITE)}	
})

#=====================SETUP USER=====================
next_state.update({
	(SETUP_USER, GET_LANGUAGE): {'error': (SETUP_USER, GET_LANGUAGE),
								 'done': IDLE}
})
