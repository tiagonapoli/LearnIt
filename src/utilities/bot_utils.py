import telebot
from utilities import utils
import sys


def get_id(msg):
	"""
		Gets message user ID
		Return:
			User ID: integer
	"""
	return msg.chat.id

def get_username(msg):
	return msg.from_user.username













