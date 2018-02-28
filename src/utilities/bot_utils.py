import telebot
from utilities import utils
import sys


def open_bot(debug_mode, logger = None):
	arq = None
	if debug_mode:
		arq = open("../credentials/bot_debug_token.txt", "r")
	else:
		arq = open("../credentials/bot_token.txt", "r")
	TOKEN = (arq.read().splitlines())[0]
	arq.close()
	bot_aux = telebot.TeleBot(TOKEN)
	if logger:
		logger.info("Bot initialized successfully")
	return bot_aux

def get_id(msg):
	"""
		Gets message user ID
		Return:
			User ID: integer
	"""
	return msg.chat.id

def get_username(msg):
	return msg.from_user.username

def create_key_button(text):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text: Text of the button
	"""
	return telebot.types.KeyboardButton(text)

def keyboard_remove():
	return telebot.types.ReplyKeyboardRemove()

def create_inline_keys_sequential(keys):
	ret = []
	cnt = 0
	for key in keys:
		ret.append((key,str(cnt)))
		cnt += 1
	return ret

def create_string_keyboard(keys):
	text = ""
	cnt = 1
	for key in keys:
		if type(key) == "tuple":
			text += "/{}. ".format(cnt) + utils.treat_msg_to_send(key[0]) + "\n"
		else:
			text += "/{}. ".format(cnt) + utils.treat_msg_to_send(key) + "\n"
		cnt += 1
	return text

def create_selection_inline_keyboard(selected, keys, width = 3, done_button = None):
	keys_aux = list(keys)
	for i in selected:
		keys_aux[i] = (">>" + keys_aux[i][0] + "<<", keys_aux[i][1])
	return create_inline_keyboard(keys_aux,width,done_button)

def parse_string_keyboard_ans(ans, keys):
	ans = ans.strip()
	if ans[0] != '/':
		ans = utils.treat_special_chars(ans)
		for key in keys:
			if type(key) == "tuple":
				if ans == key[0]:
					return True, key[0]
			else:
				if ans == key:
					return True, key
		return False, ans
		 
	ans = ans[1:]
	try:
		number = int(ans)
		print("PARSE OPTION NUMBER {}".format(number))
		number -= 1
		if number >= 0 and number < len(keys):
			if type(keys[number]) == "tuple":
				return True, keys[number][0]
			else:
				return True, keys[number]
		else:
			return False, utils.treat_special_chars(ans)
	except ValueError:
		return False, utils.treat_special_chars(ans)


def parse_string_keyboard_ans_number(ans, keys)
	ans = ans.strip()
	if ans[0] != '/':
		return False, ans
		 
	ans = ans[1:]
	try:
		number = int(ans)
		print("PARSE OPTION NUMBER {}".format(number))
		number -= 1
		if number >= 0 and number < len(keys):
			return True, number
		else:
			return False, utils.treat_special_chars(ans)
	except ValueError:
		return False, utils.treat_special_chars(ans)



def parse_selection_inline_keyboard_ans(callback_data,set_btn):
	'''
 		Altera o set_btn
 	'''
	print("CALLBACK DATA: {}".format(callback_data))
	done = False
	try:
		btn_number = int(callback_data)
		if btn_number in set_btn:
			set_btn.remove(btn_number)
		else:
			set_btn.add(btn_number)
		return set_btn, done 
	except ValueError:
		#DONE
		done = True
		return set_btn, done



def create_inline_key_button(text, data):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text: Text of the button
	"""
	return telebot.types.InlineKeyboardButton(text, callback_data=data)

def create_keyboard(keys, width = 3, done_button = None):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text:Text of the button
	"""
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=width)
	keyboard = []
	for i in range(0, len(keys)):
		if type(keys[i]) == "tuple":
			keyboard.append(create_key_button(keys[i][0]))
		else:
			keyboard.append(create_key_button(keys[i]))

	markup.add(*keyboard)

	if done_button != None:
		if type(done_button) == "tuple":
			markup.row(create_key_button(done_button[0]))
		else:
			markup.row(create_key_button(done_button))
		
	return markup


def create_inline_keyboard(keys, width = 3, done_button = None):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text:Text of the button
	"""
	markup = telebot.types.InlineKeyboardMarkup(row_width=width)
	keyboard = []
	for i in range(0, len(keys)):
		keyboard.append(create_inline_key_button(keys[i][0], keys[i][1]))
	
	markup.add(*keyboard)

	if done_button != None:
		markup.row(create_inline_key_button(done_button[0], done_button[1]))

	return markup
