import telebot
import translation
import logging
import signal
import time
from utilities import string_treating

class SendTimeoutException(Exception):   # custom exception
    def __str__(self):
    	return "Sending Timeout Exception"

def timeout_handler(signum, frame):   # raises exception when signal sent
    raise SendTimeoutException

signal.signal(signal.SIGALRM, timeout_handler)






def create_inline_key_button(text, data):
	return telebot.types.InlineKeyboardButton(text, callback_data=data)

def create_key_button(text):
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

def create_string_keyboard(keys, modifier=None):
	if modifier == None:
		modifier = [""] * len(keys)

	text = ""
	cnt = 1
	for key in keys:
		if type(key) is tuple:
			text += string_treating.treat_msg_markdown("/{}. ".format(cnt) + modifier[cnt-1] + "%s" + modifier[cnt-1] + "\n", (key[0],))
		else:
			text += string_treating.treat_msg_markdown("/{}. ".format(cnt) + modifier[cnt-1] + "%s" + modifier[cnt-1] + "\n", (key,))
		cnt += 1
	return text

def create_selection_inline_keyboard(selected, keys, width, done_button):
	keys_aux = list(keys)
	for i in selected:
		keys_aux[i] = (">>" + keys_aux[i][0] + "<<", keys_aux[i][1])
	return create_inline_keyboard(keys_aux,width,done_button)

def create_inline_keyboard(keys, width = 3, done_button = None):
	markup = telebot.types.InlineKeyboardMarkup(row_width=width)
	keyboard = []
	for i in range(0, len(keys)):
		keyboard.append(create_inline_key_button(keys[i][0], keys[i][1]))
	
	markup.add(*keyboard)

	if done_button != None:
		markup.row(create_inline_key_button(done_button[0], done_button[1]))			
	return markup

def create_keyboard(keys, width = 3, done_button = None):
	markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=width)
	keyboard = []
	for i in range(0, len(keys)):
		if type(keys[i]) is tuple:
			keyboard.append(create_key_button(keys[i][0]))
		else:
			keyboard.append(create_key_button(keys[i]))

	markup.add(*keyboard)

	if done_button != None:
		if type(done_button) is tuple:
			markup.row(create_key_button(done_button[0]))
		else:
			markup.row(create_key_button(done_button))
	return markup


class BotMessageSender():

	def __init__(self, token, user_id, language):
		self.token = token
		self.user_id = user_id
		self.bot = None
		self.tries = 20
		self.sleep = 0.5
		self.language = language
		self.logger = logging.getLogger('BotMessageSender.log') 

		self.keyboard_options = None
		self.keyboard_type = None
		self.keyboard_back_btn = None

		self.keyboard_id = None
		self.keyboard_text = None
		self.markdown_options = None
		self.keyboard_width = None
		self.empty_keyboard_text = None
		self.no_empty_flag = None
		self.btn_set = None


	#ok
	def set_bot(self):		
		ini = time.time()
		if self.bot != None:
			return

		if self.bot != None:
			del self.bot
		self.bot = telebot.TeleBot(self.token)
		fim = time.time()
		print(fim-ini)

	def translate_options(self, lst):
		ret = []
		for opt in lst:
			ret.append(translation.translate(opt, self.language))
		return ret

	#ok
	def parse_string_keyboard_ans(self, ans):
		ans = ans.strip()
		if ans[0] != '/':
			ans = string_treating.treat_special_chars(ans)
			cnt = 0
			for key in self.keyboard_options:
				if type(key) is tuple:
					if ans == key[0]:
						return True, key[0], cnt
				else:
					if ans == key:
						return True, key, cnt
				cnt += 1
			return False, ans, -1
			 
		ans = ans[1:]
		try:
			number = int(ans)
			number -= 1
			if number >= 0 and number < len(self.keyboard_options):
				return True, self.keyboard_options[number], number
			else:
				return False, string_treating.treat_special_chars(ans), -1
		except ValueError:
			return False, string_treating.treat_special_chars(ans), -1

	#ok
	def parse_navigation_string_keyboard_ans(self, ans):
		ans = ans.strip()
		if ans[0] != '/':
			ans = string_treating.treat_special_chars(ans)
			cnt = 0
			for key in self.keyboard_options:
				if type(key) is tuple:
					if ans == key[0]:
						return 'Next', key[0], cnt
				else:
					if ans == key:
						return 'Next', key, cnt
				cnt += 1
			return 'Erro', ans, -1
			 
		ans = ans[1:]
		try:
			number = int(ans)
			number -= 1
			
			if number == len(self.keyboard_options)-1:
				return 'End', self.keyboard_options[number], number

			if number == len(self.keyboard_options)-2 and self.keyboard_back_btn == True:
				return 'Back', self.keyboard_options[number], number

			if number >= 0 and number < len(self.keyboard_options):
				return 'Next', self.keyboard_options[number], number
			else:
				return 'Error', string_treating.treat_special_chars(ans), -1
		except ValueError:
			return 'Error', string_treating.treat_special_chars(ans), -1

	#ok
	def parse_selection_inline_keyboard_ans(self, callback_data):
		try:
			btn_number = int(callback_data)
			if btn_number in self.btn_set:
				self.btn_set.remove(btn_number)
			else:
				self.btn_set.add(btn_number)
			return False
		except ValueError:
			#DONE
			return True


	#ok
	def parse_keyboard_ans(self, msg):
		if self.keyboard_type == 'selection_inline':
			callback_data = msg.data
			self.keyboard_id = msg.message.message_id
			done = self.parse_selection_inline_keyboard_ans(callback_data)
			if done:
				if self.no_empty_flag == True and len(self.btn_set) == 0:
					self.edit_selection_inline_keyboard(self.empty_keyboard_text)
					done = False
				else:
					self.delete_message(self.keyboard_id)
			else:
				self.edit_selection_inline_keyboard(self.keyboard_text)
			return done, self.btn_set, self.keyboard_options
		elif self.keyboard_type == 'string_keyboard':
			return self.parse_string_keyboard_ans(msg.text) + (len(self.keyboard_options), )
		elif self.keyboard_type == 'navigation_string_keyboard':
			return self.parse_navigation_string_keyboard_ans(msg.text) + (len(self.keyboard_options), )
		elif self.keyboard_type == 'simple_keyboard':
			return self.parse_simple_keyboard_ans(msg.text) + (len(self.keyboard_options), )



	#ok
	def send_string_keyboard(self, txt, options, txt_args=(), markdown_options=None, translate_options=False, add_default_keyboard=True, width=3, parse="Markdown"):
		if translate_options:
			options = self.translate_options(options)

		if add_default_keyboard == False:
			markup = keyboard_remove()
		else:
			markup = create_keyboard(options, width)

		self.keyboard_type = 'string_keyboard'
		self.keyboard_options = list(options)
		self.markdown_options = markdown_options

		tries = self.tries
		txt = translation.translate(txt, self.language)
		if parse == 'Markdown':
			txt = string_treating.treat_msg_markdown(txt, txt_args)
		else:
			txt = txt % txt_args
		txt += "\n" + create_string_keyboard(self.keyboard_options, self.markdown_options)
		while tries > 0:
			try:
				self.set_bot()
				self.bot.send_message(self.user_id, txt, reply_markup=markup, parse_mode=parse)
				return
			except:
				self.logger.error("Error in send string keyboard {}".format(self.user_id), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)

	#ok
	def send_navigation_string_keyboard(self, txt, options, end_btn, back_btn=None, markdown_options=None, txt_args=(), translate_options=False, parse="Markdown"):
		if translate_options:
			options = self.translate_options(options)

		markup = keyboard_remove()

		self.keyboard_type = 'navigation_string_keyboard'
		self.keyboard_options = list(options) 
		self.markdown_options = markdown_options
		if back_btn != None:
			self.keyboard_back_btn = True
			back_btn = translation.translate(back_btn, self.language)
			self.keyboard_options.append(back_btn)
		else:
			self.keyboard_back_btn = False

		end_btn = translation.translate(end_btn, self.language)
		self.keyboard_options.append(end_btn)
		

		tries = self.tries
		txt = translation.translate(txt, self.language)
		if parse == 'Markdown':
			txt = string_treating.treat_msg_markdown(txt, txt_args)
		else:
			txt = txt % txt_args
		txt += "\n" + create_string_keyboard(self.keyboard_options, self.markdown_options)
		while tries > 0:
			try:
				self.set_bot()
				self.bot.send_message(self.user_id, txt, reply_markup=markup, parse_mode=parse)
				return
			except:
				self.logger.error("Error in send string keyboard {}".format(self.user_id), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)


	#Ok
	def send_selection_inline_keyboard(self, txt, options, txt_args=(), translate_options=False, empty_keyboard_text=None, no_empty_flag=False, width=3, parse="Markdown"):
		if translate_options:
			options = self.translate_options(options)

		self.btn_set = set()
		self.empty_keyboard_text = empty_keyboard_text
		self.no_empty_flag = no_empty_flag
		self.keyboard_width = width
		self.keyboard_type = 'selection_inline'
		self.keyboard_options = create_inline_keys_sequential(options)

		markup = create_selection_inline_keyboard(self.btn_set, self.keyboard_options, width, (translation.translate("End selection", self.language), "DONE"))
		tries = self.tries
		self.keyboard_text = txt
		self.keyboard_text_args = txt_args

		self.send_message(self.keyboard_text, self.keyboard_text_args, markup=markup, parse=parse)


	#OK
	def edit_selection_inline_keyboard(self, txt, txt_args=(), translate_flag=True, parse="Markdown"):
		markup = create_selection_inline_keyboard(self.btn_set, self.keyboard_options, self.keyboard_width, (translation.translate("End selection", self.language), "DONE"))
		tries = self.tries
		if translate_flag:
			txt = translation.translate(txt, self.language)

		if parse == 'Markdown':
			txt = string_treating.treat_msg_markdown(txt, txt_args)
		else:
			txt = txt % txt_args

		while tries > 0:
			try:
				self.set_bot()
				self.bot.edit_message_text(chat_id=self.user_id, message_id=self.keyboard_id, text=txt,
				    		 reply_markup=markup, parse_mode=parse)
				return
			except:
				self.logger.error("Error in edit selection inline keyboard {}".format(self.user_id), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)

	#OK
	def delete_message(self, msg_id):
		tries = self.tries
		while tries > 0:
			try:
				self.set_bot()
				self.bot.delete_message(chat_id=self.user_id, message_id=msg_id)
				return True
			except:
				self.logger.error("Error in delete message {}".format(self.user_id), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)
		return False

	#ok
	def send_message(self, txt, txt_args=(), markup=keyboard_remove(), translate_flag=True, parse='Markdown', disable_web_preview=True):
		tries = self.tries

		if translate_flag:
			txt = translation.translate(txt, self.language)

		if parse == 'Markdown':
			txt = string_treating.treat_msg_markdown(txt, txt_args)
		else:
			txt = txt % txt_args
		while tries > 0:
			try:
				self.set_bot()
				self.bot.send_message(self.user_id, txt, reply_markup=markup, parse_mode=parse, disable_web_page_preview=disable_web_preview)
				return True
			except:
				self.logger.error("Error in send message {}".format(self.user_id), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)
		return False

	#ok
	def send_photo(self, path, markup=keyboard_remove()):
		tries = self.tries
		arq = open(path, 'rb')
		while tries > 0:
			try:
				signal.alarm(20)
				self.set_bot()
				self.bot.send_photo(self.user_id, arq, reply_markup=markup)
				arq.close()
				signal.alarm(0)
				return True
			except:
				self.logger.error("Error in send photo {} - {}".format(self.user_id, path), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)
		arq.close()
		return False


	#ok
	def send_voice(self, path, markup=keyboard_remove()):
		tries = self.tries
		arq = open(path, 'rb')
		while tries > 0:
			try:
				signal.alarm(20)
				self.set_bot()
				self.bot.send_voice(self.user_id, arq, reply_markup=markup)
				arq.close()
				signal.alarm(0)
				return True
			except:
				self.logger.error("Error in send photo {} - {}".format(self.user_id, path), exc_info=True)
			tries -= 1
			time.sleep(self.sleep)
		arq.close()
		return False





if __name__ == '__main__':

	message_sender = BotMessageSender('495750247:AAFVO7YqWCl2QKov6PselFnAlL_RRBtfWco', 359999978, 1)

	message_sender.send_message('*BotMessageSender testings*') 
	message_sender.send_message('*BotMessage %s Sender testings*', txt_args=("*Negrito!*", ), translate_flag=False)
	message_sender.send_message('*BotMessageSender testings*', parse='') 
	message_sender.send_photo('/home/tiago/Pictures/Trees_JeroenVanNieuwenhoveFlickr.jpg')
	message_sender.send_voice('/home/tiago/Music/sound-9.mp3')
	message_sender.send_selection_inline_keyboard("%s already exists", ['Yes', 'No'], txt_args=('_Nao italico_',))
	message_sender.send_selection_inline_keyboard('Send image', ['Yes', 'No'], translate_options=True)
	message_sender.send_string_keyboard("Word's topic: *%s*", ['Yes', 'No'], txt_args=('Neg_*_rito',))
	message_sender.send_string_keyboard('Image received successfuly', ['Yes', 'No'], translate_options=True)

