import psycopg2
import os
import time
import datetime
import abc
from flashcard import Word
from flashcard import Card
from database_ops.db_utils import treat_str_SQL


class UserOps():

	def __init__(self, conn, cursor):
		self.conn = conn
		self.cursor = cursor

	def get_state(self, user_id):
		"""Gets the current state information about the user

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A tuple containing two integers, the primary and secondary states of the user.
		"""
		tries = 5
		while tries > 0:
			tries -= 1
			try:
				self.cursor.execute("SELECT state1, state2, state3 FROM users WHERE id={}".format(user_id))
				row = self.cursor.fetchall()
				if len(row) == 0:
					return "User doesn't exist"
				return (row[0][0], row[0][1], row[0][2])
			except psycopg2.ProgrammingError:
				print("EXCECAO PROGRAMMING ERROR")
				log = open('get_state_log', 'w')
				log.write("GET STATE USER_OPS {}\n".format(user_id) + 
						  "EXCECAO PROGRAMMING ERROR\n" +
						  "SELECT state1, state2, state3 FROM users WHERE id={}\n\n".format(user_id))
		return []


	def set_state(self, user_id, state1, state2, state3):
			"""Updates on the database the state information about the user
				
			Args:
				user_id: An integer representing the user's id.
				state: An integer representing the user's primary state.
				state2: An integer representing the user's secondary state.
			"""
			self.cursor.execute("UPDATE users SET state1={}, state2={}, state3={} WHERE id={}".format(state1, state2, state3, user_id))
			self.conn.commit()



	def add_user(self, user_id):
		"""Adds a new user to the database.

		Args:
			user_id: An integer representing the user's id.

		Returns:
			A string containing a message to the user. This string can be:
			- "Welcome to LingBot", if the user was not registered.
			- "Welcome back to LingoBot", if the user was already registered.
		"""

		self.cursor.execute("SELECT id from users WHERE id={};".format(user_id))
		rows = self.cursor.fetchall()
		if(len(rows) > 0):
			return "Welcome back to LingoBot!"

		self.cursor.execute("INSERT INTO users VALUES ({}, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT);".format(user_id))
		self.conn.commit()
		return "Welcome to LingoBot!\n" + "Use the command /add_language to add the languages you are interested in learning and then use the command /add_word to add words you are interested in memorizing.\n"


	def get_known_users(self):
		"""Gets all the columns of all users in the database
		
		Returns:
			A list of tuples with the following information about the users:
			- An integer representing the user's id.
			- An integer representing the number of messages the user will receive per day.
			- An integer representing the current primary state of the user.
			- An integer representing the current secondary state of the user.
		"""

		known = set()
		self.cursor.execute("SELECT id FROM users;")
		rows = self.cursor.fetchall()
		for row in rows:
			known.add(row[0])

		return known
