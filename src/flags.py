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
SEND_IMAGE_LOOP = 10
SEND_AUDIO = 11
SEND_AUDIO_LOOP = 12
SEND_TRANSLATION = 13
SEND_TRANSLATION_LOOP = 14


previous_state{
	



}

next_state = {	IDLE:   {'card_query': WAITING_ANS,
			      			   'add_word': ADD_WORD,
			      			   'add_language': ADD_LANGUAGE}
				WAITING_ANS: WAITING_POLL_ANS,
				WAITING_POLL_ANS: IDLE,
				ADD_WORD: (ADD_WORD, GET_LANGUAGE),
				(ADD_WORD, GET_LANGUAGE): (ADD_WORD, GET_TOPIC),
				(ADD_WORD, GET_TOPIC): (ADD_WORD, GET_WORD),
				(ADD_WORD, GET_WORD) : {'send_image': (ADD_WORD, SEND_IMAGE),
						  						    'send_audio': (ADD_WORD, SEND_AUDIO),
						  						    'send_translation': (ADD_WORD, SEND_TRANSLATION)},
				(ADD_WORD, SEND_IMAGE) : (ADD_WORD, SEND_IMAGE_LOOP), # vai mandar imagem
				(ADD_WORD, SEND_IMAGE): {'Done': IDLE,
		 	   			   						     'else': (ADD_WORD, SEND_IMAGE_LOOP)},
				(ADD_WORD, SEND_AUDIO): (ADD_WORD, SEND_AUDIO_LOOP),  # vai mandar audio
				(ADD_WORD, SEND_AUDIO_LOOP): {'Done': IDLE,
							   							  'else': (ADD_WORD, SEND_AUDIO_LOOP)},
				(ADD_WORD, SEND_TRANSLATION): (ADD_WORD, SEND_TRANSLATION_LOOP),	  # vai mandar translation
				(ADD_WORD, SEND_TRANSLATION_LOOP): {'Done': IDLE,
							   		      					    'else': (ADD_WORD, SEND_TRANSLATION_LOOP)},
				ADD_LANGUAGE: IDLE
}
