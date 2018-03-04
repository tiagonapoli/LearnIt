

native_languages = {'English': 0,
					'Português': 1}

native_languages_map = {0: 'English',
						1: 'Português'}

poll_text = ("*5* - _perfect response, without any hesitation_\n" +
			 "*4* - _correct response after a hesitation_\n" +
			 "*3* - _correct response recalled with difficulty_\n" + 
			 "*2* - _incorrect response; where the correct one seemed easy to recall_\n" + 
			 "*1* - _incorrect response; the correct one was remembered_\n" +
			 "*0* - _complete blackout._")

poll_text_pt = ("*5* - _resposta perfeita, sem qualquer hesitação_\n" +
				 "*4* - _resposta correta, mas com certa hesitação_\n" +
				 "*3* - _resposta correta, lembrada com dificuldade_\n" + 
				 "*2* - _resposta incorreta; a resposta certa era fácil de lembrar_\n" + 
				 "*1* - _resposta incorreta; a resposta certa foi lembrada agora_\n" +
				 "*0* - _total esquecimento._")


help_msg = ("Use the command /add\_language to add the languages you are interested in learning and then use the command /add\_word to add words you are interested in memorizing, " + 
			"or just use the command /copy\_words to copy words from other users. " +
			"During any process you can use /cancel to cancel the ongoing events, if you made a mistake, for example.\n" +
		   "If you have questions or want to support the project, please contact one of the developers:" +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")

help_msg_pt = ("Use o comando /add\_language para adicionar línguas ou matérias nas quais você está interessado em aprender, e depois use o comando /add\_word para adicionar palavras para aprender e memorizar, " +
			"ou use /copy\_words para copiar cards prontos de outros usuários. Durante qualquer processo, use /cancel para cancelar qualquer evento, se você cometeu algum erro, por exemplo" +
		   "Se você tiver dúvidas, sugestões ou quiser apoiar o projeto, contate um dos desenvolvedores:" +
		   "\n*Tiago Napoli*\nTelegram: t.me/tiagonapoli\nEmail: napoli.tiago@hotmail.com\n" + 
		   "\n*Gabriel Camargo*\nTelegram: t.me/gabriel\_camargo\nEmail: gacamargo1.000@gmail.com\n")


welcome = ("Use the command /add\_language to add the languages you are interested in learning and then use the command /add\_word to add words you are interested in memorizing, " +
			"or just use the command /copy\_words to copy words from other users. During any process you can use /cancel to cancel the ongoing events, if you made a mistake, for example.")

welcome_pt = ("Use o comando /add\_language para adicionar línguas ou matérias nas quais você está interessado em aprender, e depois use o comando /add\_word para adicionar palavras para aprender e memorizar, " +
			"ou use /copy\_words para copiar cards prontos de outros usuários. Durante qualquer processo, use /cancel para cancelar qualquer evento, se você cometeu algum erro, por exemplo")


message = { "*Text me the language you want to add*": 
				{0: "*Text me the language you want to add*",
				 1: "*Me envie a linguagem que quer adicionar*"},
			
			"_Please, add a language first._": 
				{0: "_Please, add a language first._",
				 1: "_Por favor, adicione uma linguagem primeiro_"},
			
			"Please, don't exceed 45 characters. You digited {} characters. Send the language again:": 
				{0: "Please, don't exceed 45 characters. You digited {} characters. Send the language again:",
				 1: "Por favor, não exceda 45 caracteres. Você digitou {} caracteres. Me envie a linguagem novamente:"},
			
			"Please, don't user / or \ or _ or *. Send the language again:": 
				{0: "Please, don't use / or \ or _ or *. Send the language again:",
				 1: "Por favor, não use / ou \ ou _ ou *. Me envie a linguagem novamente:"},
			
			"{} added successfully to your languages": 
				{0: "{} added successfully to your languages",
				 1: "{} foi adicionado com sucesso às suas linguagens"},	

			"{} already exists": 
				{0: "{} already exists",
				 1: "{} já existe"},	

			"_Use_ @pic _<image_\__name> or_ @bing _<image_\__name> to select an image_": 
				{0: "_Use_ @pic _<image_\__name> or_ @bing _<image_\__name> to select an image_",
				 1: "_Use_ @pic _<termos_\__para_\__pesquisa> ou_ @bing _<termos_\__para_\__pesquisa> para selecionar uma imagem_"},	

			"_Hint: You can download pronunciations on forvo.com and then send them to me. This process is way easier on PC (Telegram Desktop)_": 
				{0: "_Hint: You can download pronunciations on forvo.com and then send them to me. This process is way easier on PC (Telegram Desktop)_",
				 1: "_Dica: Você pode baixar pronúncias do site forvo.com e então mandá-las para mim. Esse processo é muito mais fácil no PC (Telegram Desktop)_"},	

			"_Successfully done!_": 
				{0: "_Successfully done!_",
				 1: "_Sucesso!_"},	

			"_Hint: The process to add a word is way easier on Telegram Desktop_": 
				{0: "_Hint: The process to add a word is way easier on Telegram Desktop_",
				 1: "_Dica: O processo para adicionar palavra é muito mais fácil e rápido no Telegram Desktop_"},	


			"*Please select the word's language:*": 
				{0: "*Please select the word's language:*",
				 1: "*Por favor, selecione a linguagem da palavra:*"},	


			"Please choose from keyboard": 
				{0: "Please choose from keyboard",
				 1: "Por favor, selecione do teclado fornecido"},	  
					
			"*Send the word's topic*. You can send a *new topic* or *select from existing*": 
				{0: "*Send the word's topic*. You can send a *new topic* or *select from existing*",
				 1: "*Envie-me o tópico da palavra*. Você pode mandar um *novo tópico* ou *selecionar dos existentes*"},	

			"_Topics registered:_": 
				{0: "_Topics registered:_",
				 1: "_Tópicos registrados:_"},	

			"_There are no topics registered in this language yet, so please_ *send a new topic*": 
				{0: "_There are no topics registered in this language yet, so please_ *send a new topic*",
				 1: "_Não há tópicos registrados nessa linguagem ainda. Por favor,_ *envie-me um novo tópico*"},	

			"Please, don't exceed 45 characters. You digited {} characters. Send the topic again:": 
				{0: "Please, don't exceed 45 characters. You digited {} characters. Send the topic again:",
				 1: "Por favor, não exceda 45 caracteres. Você digitou {} caracteres. Me mande o tópico novamente:"},	

			"Please, don't user / or \ or _ or *. Send the topic again:": 
				{0: "Please, don't use / or \ or _ or *. Send the topic again:",
				 1: "Por favor, não use / ou \ ou _ ou *. Me envie o tópico novamente:"},	


			"Word's topic: *{}*": 
				{0: "Word's topic: *{}*",
				 1: "Tópico da palavra: *{}*"},	


			"*Send word to add* (in _{}_)": 
				{0: "*Send word to add* (in _{}_)",
				 1: "*Me envie a palavra a adicionar* (em _{}_)"},	

			"Please, don't exceed 190 characters. You digited {} characters. Send the word again:": 
				{0: "Please, don't exceed 190 characters. You digited {} characters. Send the word again:",
				 1: "Por favor, não exceda 190 caracteres. Você digitou {} caracteres. Me envie a palavra novamente:"},	

			"Please, don't user / or \ or _ or *. Send the word again:": 
				{0: "Please, don't use / or \ or _ or *. Send the word again:",
				 1: "Por favor, não use / ou \ ou _ ou *. Me envie a palavra novamente:"},	

			"_Please,_ *send an image* _to use instead of a word:_": 
				{0: "_Please,_ *send an image* _to use instead of a word:_",
				 1: "_Por favor,_ *me envie uma imagem* _ para ser usada ao invés de uma palavra:_"},	

			"This word is already registered, if you want to add it anyway, please, erase it first. The process will be canceled": 
				{0: "This word is already registered, if you want to add it anyway, please, erase it first. The process will be canceled",
				 1: "Essa palavra já está registrada. Se você quer adicioná-la mesmo assim, por favor, delete-a primeiro. O processo atual será cancelado"},	

			'Send image': 
				{0: 'Send image',
				 1: 'Enviar imagem'},	

			'Send audio': 
				{0: 'Send audio',
				 1: 'Enviar audio'},	

			'Send text': 
				{0: 'Send text',
				 1: 'Enviar texto'},	

			'End selection': 
				{0: 'End selection',
				 1: 'Terminar seleção'},	

			"_Select the ways you want to relate to the word (one or more):_": 
				{0: "_Select the ways you want to relate to the word (one or more):_",
				 1: "_Selecione os meios com que você quer relacionar a palavra (um ou mais)_"},	

			"Please, select *at least one way* to relate to the word: ": 
				{0: "Please, select *at least one way* to relate to the word: ",
				 1: "Por favor, selecione *pelo menos um meio* com o qual relacione sua palavra:"},	

			"_OK!_": 
				{0: "_OK!_",
				 1: "_OK!_"},	

			"Audio received successfuly": 
				{0: "Audio received successfuly",
				 1: "Audio recebido com sucesso"},	

			'Yes': 
				{0: 'Yes',
				 1: 'Sim'},

			'No': 
				{0: 'No',
				 1: 'Não'},

			"_Would you like to add more words in_ *{}*_, in topic_ *{}*_?_\n": 
				{0: "_Would you like to add more words in_ *{}*_, in topic_ *{}*_?_\n",
				 1: "_Você gostaria de adicionar mais palavras em_ *{}*_, no tópico_ *{}*_?_\n"},

			"Image received successfuly": 
				{0: "Image received successfuly",
				 1: "Imagem recebida com sucesso"},

			"Please, don't exceed 290 characters. You digited {} characters. Send the text again:": 
				{0: "Please, don't exceed 290 characters. You digited {} characters. Send the text again:",
				 1: "Por favor, não exceda 290 caracteres. Você digitou {} caracteres. Me envie o texto novamente:"},

			"Text received successfuly": 
				{0: "Text received successfuly",
				 1: "Texto recebido com sucesso"},

			"canceled...": 
				{0: "canceled...",
				 1: "cancelado..."},

			"Your answer was correct!": 
				{0: "Your answer was correct!",
				 1: "Sua resposta está correta!"},

			"There was a mistake in your answer :(": 
				{0: "There was a mistake in your answer :(",
				 1: "Houve um erro em sua resposta :("},

			"_Please grade your performance to answer the card_\n": 
				{0: "_Please grade your performance to answer the card_\n",
				 1: "_Por favor, dê uma nota à sua performance para responder o cartão_\n"},

			'Please, send the Telegram username of the user you want to copy some words from, in the format @username (or just username)': 
				{0: 'Please, send the Telegram username of the user you want to copy some words from',
				 1: 'Por favor, envie o nome de usuário Telegram da pessoa que você quer copiar palavras'},

			"Invalid username. Please, if you still want to copy from a user, send /copy_words again.": 
				{0: "Invalid username. Please, if you still want to copy from a user, send /copy_words again.",
				 1: "Usuário inválido. Se você ainda quer copiar de algum usuário, me envie /copy_words novamente."},

			"You can't copy from yourself! Please, if you still want to copy from a user, send /copy_words again.": 
				{0: "You can't copy from yourself! Please, if you still want to copy from a user, send /copy_words again.",
				 1: "Você não pode copiar de si mesmo! Se você ainda quer copiar de algum usuário, me envie /copy_words novamente."},

			"This user is not public. Please, if you still want to copy from a user, send /copy_words again.": 
				{0: "This user is not public. Please, if you still want to copy from a user, send /copy_words again.",
				 1: "Esse usuário não é público. Se você ainda quer copiar de algum usuário, me envie /copy_words novamente."},

			"The user _{}_ does not have any language": 
				{0: "The user _{}_ does not have any language",
				 1: "O usuário _{}_ não tem nenhuma língua registrada"},

			"*Please select the language:*": 
				{0: "*Please select the language:*",
				 1: "*Selecione a linguagem:*"},

			"Select the topics you want to copy:": 
				{0: "Select the topics you want to copy:",
				 1: "Selecione os tópicos que você deseja copiar:"},

			"_There are no topics registered in this language yet._": 
				{0: "_There are no topics registered in this language yet._",
				 1: "_Não há tópicos registrados nessa linguagem ainda_"},

			"In case some words to be copied already exist in your words, *should we overwrite?* If you already copied from this user and topic maybe you don't want to overwrite _(If we overwrite you lose all learning data about that word)_": 
				{0: "In case some words to be copied already exist in your words, *should we overwrite?* If you already copied from this user and topic maybe you don't want to overwrite _(If we overwrite you lose all learning data about that word)_",
				 1: "Em caso alguma palavra a ser copiada já exista na sua lista, eu *deveria sobrescrever?* Se você já copiou desse usuário e tópico talvez você não queira sobrescrever_(Se sobrescrever você perde todos os dados de aprendizado daquela palavra)_"},

			'*Overwritten words:*': 
				{0: '*Overwritten words:*',
				 1: '*Palavras sobrescritas:*'},

			'*Topic: ': 
				{0: '*Topic: ',
				 1: '*Tópico: '},

			'There were no overwritten words!': 
				{0: 'There were no overwritten words!',
				 1: 'Não houve palavras sobrescritas!'},

			"_Select languages to erase:_": 
				{0: "_Select languages to erase:_",
				 1: "_Selecione as linguagens a apagar:_"},

			"_Erased languages:_": 
				{0: "_Erased languages:_",
				 1: "_Linguagens apagadas:_"},

			"Select languages to erase:": 
				{0: "Select languages to erase:",
				 1: "Selecione as linguagens a apagar:"},

			"*Please select the language:*": 
				{0: "*Please select the language:*",
				 1: "*Selecione a linguagem:*"},

			"*Select the word's topic:*": 
				{0: "*Select the word's topic:*",
				 1: "*Selecione o tópico da palavra:*"},

			"_Please choose from options._": 
				{0: "_Please choose from options._",
				 1: "_Por favor, selecione das opções fornecidas._"},

			"_Select words to erase:_": 
				{0: "_Select words to erase:_",
				 1: "_Selecione as palavras a apagar:_"},

			"_Erased words:_": 
				{0: "_Erased words:_",
				 1: "_Palavras apagadas:_"},

			"LearnIt is under development, so sometimes we have to do some experiments and reset some things, maybe because of this, your user isn't in our database. To fix this, please send a /start.": 
				{0: "LearnIt is under development, so sometimes we have to do some experiments and reset some things, maybe because of this, your user isn't in our database. To fix this, please send a /start",
				 1: "LearnIt está em desenvolvimento, por isso algumas vezes nós fazemos alguns experimentos e reiniciamos certas coisas, talvez por isso seu usuário não esteja em nosso banco de dados. Para consertar, envie-me /start"},

			"help_msg": 
				{0: help_msg,
				 1: help_msg_pt},

			"_Languages:_": 
				{0: "_Languages:_",
				 1: "_Linguages:_"},

			"_No languages registered yet..._": 
				{0: "_No languages registered yet..._",
				 1: "_Não há linguagens registradas ainda..._"},

			"*Select the word's topic.*": 
				{0: "*Select the word's topic.*",
				 1: "*Selecione o tópico da palavra.*"},

			"*Please choose from options.*": 
				{0: "*Please choose from options.*",
				 1: "*Por favor, selecione das opções fornecidas.*"},

			"*Select the word you want to see the related media* _(to exit this menu, select_ /{}_)_:": 
				{0: "*Select the word you want to see the related media* _(to exit this menu, select_ /{}_)_:",
				 1: "*Selecione a palvra que deseja ver com detalhe* _(para sair desse menu, selecione_ /{}_)_:"},

			"OK!": 
				{0: "OK!",
				 1: "OK!"},

			"*Word:* _{}_": 
				{0: "*Word:* _{}_",
				 1: "*Palavra:* _{}_"},

			"Oops, didn't understand your message": 
				{0: "Oops, didn't understand your message",
				 1: "Oops, não entendi sua mensagem"},

			'Cards per hour': 
				{0: 'Cards per hour',
				 1: 'Cartões por hora'},

			'Set profile public': 
				{0: 'Set profile public',
				 1: 'Tornar perfil público'},

			'Set profile private': 
				{0: 'Set profile private',
				 1: 'Tornar perfil privado'},

			"*Which settings do you want to change?*": 
				{0: "*Which settings do you want to change?*",
				 1: "*Qual configuração você deseja mudar?*"},

			"*How many cards you want to receive per hour?*": 
				{0: "*How many cards you want to receive per hour?*",
				 1: "*Quantos cartões deseja receber por hora?*"},

			'Your profile is now public': 
				{0: 'Your profile is now public',
				 1: 'Seu perfil é agora público'},

			'Your profile is now private': 
				{0: 'Your profile is now private',
				 1: 'Seu perfil é agora privado'},

			"_Cards per hour set successfuly!_": 
				{0: "_Cards per hour set successfuly!_",
				 1: "_Cartões por hora mudados com sucesso!_"},

			"Please, create your Telegram Username first. You just have to go to Settings->Info->Username to create it. After you create one, type /start again.": 
				{0: "Please, create your Telegram Username first. You just have to go to Settings->Info->Username to create it. After you create one, type /start again.",
				 1: "Por favor, crie seu nome de usuário de Telegram primeiro. Você só tem quer ir em Configurações do Telegram -> Informações -> Nome de usuário. Depois de criar um, digite /start novamente."},

			"Welcome back to LearnIt!": 
				{0: "*Welcome back to LearnIt!*",
				 1: "*Bem-vindo de volta ao LearnIt!*"},

			"welcome_msg": 
				{0: welcome,
				 1: welcome_pt},

			"Welcome to LearnIt!": 
				{0: "*Welcome to LearnIt!*",
				 1: "*Bem vindo ao LearnIt!*"},

			"You will *not* receive any card until you use the command /start again": 
				{0: "You will *not* receive any card until you use the command /start again",
				 1: "Você *não* receberá nenhum cartão até que use o comando /start novamente"},

			"_Select the topics that you want to review:_": 
				{0: "_Select the topics that you want to review:_",
				 1: "_Selecione os tópicos que deseja revisar:_"},

			"Please, select *at least one* topic to review:": 
				{0: "Please, select *at least one* topic to review:",
				 1: "Por favor, selecione *pelo menos um* tópico que deseja revisar:"},

			"*Please select the number of review cards that you want to receive:*": 
				{0: "*Please select the number of review cards that you want to receive:*",
				 1: "*Por favor, selecione o número de cartões de revisão que deseja receber:*"},

			"That was correct!": 
				{0: "That was correct!",
				 1: "Correto!"},

			"There was a mistake :(": 
				{0: "There was a mistake :(",
				 1: "Houve um erro :("},

			"*Review session done!*": 
				{0: "*Review session done!*",
				 1: "*Revisão terminada!*"},

			"*Answer:* ": 
				{0: "*Answer:* ",
				 1: "*Resposta:* "},

			"Image answer:": 
				{0: "Image answer:",
				 1: "Imagem de resposta:"},

			"Audio answer:": 
				{0: "Audio answer:",
				 1: "Audio de resposta:"},

			"Text answer:": 
				{0: "Text answer:",
				 1: "Texto de resposta:"},

			"*Review card{}!*": 
				{0: "*Review card{}!*",
				 1: "*Cartão de Revisão{}!*"},

			'*Learning card{}!*': 
				{0: "*Learning card{}!*",
				 1: "*Cartão de Aprendizado{}!*"},

			"Try to relate the next message to something you know in *{}/{}*. When you remeber or when you are ready, *send me any message*": 
				{0: "Try to relate the next message to something you know in *{}/{}*. When you remeber or when you are ready, *send me any message*",
				 1: "Tente relacionar a próxima mensagem com algo que você aprendeu em *{}/{}*. Quando você lembrar ou estiver pronto, *envie-me qualquer mensagem*"},

			"Transcribe the audio in _{}_, topic _{}_": 
				{0: "Transcribe the audio in _{}_, topic _{}_",
				 1: "Transcreva o áudio em _{}_, tópico _{}_"},

			"Relate the text to a word in _{}_, topic _{}_": 
				{0: "Relate the text to a word in _{}_, topic _{}_",
				 1: "Relacione o texto a alguma palavra em _{}_, tópico _{}_"},

			'Relate the image to a word in _{}_, topic _{}_':
				{0: 'Relate the image to a word in _{}_, topic _{}_',
				 1: "Relacione a imagem a uma palavra em _{}_, tópico _{}_"},

			'Change bot language': 
				{0: 'Change bot language',
				 1: 'Mudar o idioma do bot'},

			'an image': 
				{0: 'an image',
				 1: 'uma imagem'},

			'an audio': 
				{0: 'an audio',
				 1: 'um áudio'},

			'a text': 
				{0: 'a text',
				 1: 'um texto'},

			"Send *{}*:": 
				{0: "Send *{}*:",
				 1: "Envie *{}*:"},

			"poll_text": 
				{0: poll_text,
				 1: poll_text_pt},

			"Select words to erase:":
				{0: "Select words to erase:",
				 1: "Selecione as palavras para apagar:"}

	

}

def translate(msg, user):
	language = user.get_native_language()
	return message[msg][language]




