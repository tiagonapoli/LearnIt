import telebot
import utils
import sys

def get_id(msg):
	"""
		Gets message user ID
		Return:
			User ID: integer
	"""
	return msg.chat.id

def create_key_button(text):
	"""
		Creates a key button to add to a telegram custom keyboard.
		
		Args:
			text: Text of the button
	"""
	return telebot.types.KeyboardButton(text)
