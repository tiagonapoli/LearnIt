import fsm
from utilities.bot_utils import get_id
import bot_language


def handle_user_dont_exist(bot, rtd, debug_mode):

	#=====================USER DOESN'T EXIST - MSG=====================
	@bot.message_handler(func = lambda msg:	rtd.check_user_existence(get_id(msg)) == False, content_types=['text','photo','audio','voice'])
	def user_existence(msg):
		user_id = get_id(msg)
		user = rtd.get_user(get_id(msg))
		error_msg = bot_language.translate("LearnIt is under development, so sometimes we have to do some experiments and reset some things, maybe because of this, your user isn't in our database. To fix this, please send a /start.", user)
		bot.send_message(user_id, error_msg)

	#=====================USER DOESN'T EXIST - CALLBACK=====================
	@bot.callback_query_handler(func = lambda call:	rtd.check_user_existence(get_id(call.message)) == False)
	def callback_user_existence(call):
		user_id = get_id(call.message)
		user = rtd.get_user(get_id(msg))
		error_msg = bot_language.translate("LearnIt is under development, so sometimes we have to do some experiments and reset some things, maybe because of this, your user isn't in our database. To fix this, please send a /start.", user)
		bot.send_message(user_id, error_msg)



		