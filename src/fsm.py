'''Finite State Machine'''


'''States'''
LOCKED = 999
IDLE = 0   
WAITING_ANS = 1
ADD_WORD = 2
ADD_LANGUAGE = 3
WAITING_ANS = 4
WAITING_POLL_ANS = 5
GET_LANGUAGE = 6
GET_TOPIC = 7
GET_WORD = 8
SEND_IMAGE = 9
SEND_AUDIO = 11
SEND_TRANSLATION = 13
RELATE_MENU = 15
WAITING_POLL_REMEMBER = 16
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




'''FSM'''

#=====================IDLE MENU=====================
next_state = {	
	IDLE:   {'card_query': WAITING_ANS,
      		 'add_word': (ADD_WORD, GET_LANGUAGE),
      		 'add_language': ADD_LANGUAGE,
      		 'card_remember': WAITING_POLL_REMEMBER,
      		 'list_words': (LIST_WORDS, GET_LANGUAGE),
      		 'list_languages': IDLE,
      		 'erase_words': (ERASE_WORDS, GET_LANGUAGE),
      		 'erase_languages': (ERASE_LANGUAGES, SELECT_LANGUAGES),
      		 'review' : (REVIEW, GET_LANGUAGE),
      		 'settings' : (SETTINGS, GET_OPTION)}
}


#=====================CARD ANSWERING=====================
next_state.update({
	WAITING_ANS: WAITING_POLL_ANS,
	WAITING_POLL_ANS: {'done': IDLE,
					   'error': WAITING_POLL_ANS},
	WAITING_POLL_REMEMBER: {'error': WAITING_POLL_REMEMBER,
							'done': IDLE}
})


#=====================ADD WORD=====================
next_state.update({
	(ADD_WORD, GET_LANGUAGE): {'done': (ADD_WORD, GET_TOPIC),
							   'error': (ADD_WORD, GET_LANGUAGE)},
	(ADD_WORD, GET_TOPIC): (ADD_WORD, GET_WORD),
	(ADD_WORD, GET_WORD): (ADD_WORD, RELATE_MENU),
	(ADD_WORD, RELATE_MENU): {'Send audio': (ADD_WORD, SEND_AUDIO),
							  'Send image': (ADD_WORD, SEND_IMAGE),
							  'Send translation': (ADD_WORD, SEND_TRANSLATION),
			  				  'continue': (ADD_WORD, RELATE_MENU),
			  				  'done': IDLE},
	(ADD_WORD, SEND_IMAGE): {'Send audio': (ADD_WORD, SEND_AUDIO),
							  'Send translation': (ADD_WORD, SEND_TRANSLATION),
			  				  'done': IDLE},
	(ADD_WORD, SEND_AUDIO): {'Send image': (ADD_WORD, SEND_IMAGE),
							 'Send translation': (ADD_WORD, SEND_TRANSLATION),
			  				 'done': IDLE},
	(ADD_WORD, SEND_TRANSLATION): {'Send image': (ADD_WORD, SEND_IMAGE),
							  	   'Send audio': (ADD_WORD, SEND_AUDIO),
			  				  	   'done': IDLE}
})


#=====================ADD LANGUAGE=====================
next_state.update({
	ADD_LANGUAGE: IDLE
})


#=====================LIST WORDS=====================
next_state.update({
	(LIST_WORDS, GET_LANGUAGE): {'done': (LIST_WORDS, GET_TOPIC),
								 'no topics': IDLE,
								 'error': (LIST_WORDS, GET_LANGUAGE)},
	(LIST_WORDS, GET_TOPIC): {'done': IDLE,
							  'error': (LIST_WORDS, GET_TOPIC)}
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
							  'cards per hour' : (SETTINGS, CARDS_PER_HOUR)},
	(SETTINGS, CARDS_PER_HOUR) : {'error' : (SETTINGS, CARDS_PER_HOUR),
								  'done' : IDLE}
})