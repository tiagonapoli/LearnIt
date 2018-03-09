import fsm
import message_handlers.add_item
from utilities.bot_utils import get_id
from Flashcard import StudyItemDeck, Card

def handle_add_item_image(bot, user_manager, debug_mode):

	@bot.message_handler(func = lambda msg:
					user_manager.get_user(get_id(msg)).get_state() == (fsm.ADD_ITEM, fsm.SEND_IMAGE), 
					content_types=['photo'])
	def add_image(msg):

		user_id = get_id(msg)
		user = user_manager.get_user(user_id)
		user.set_state(fsm.LOCKED)
		logger = user.logger

		study_item = user.temp_study_item
		card_id = user.get_highest_card_id() + 1 + len(study_item.cards)
	
		filename = card_id
		data_path = "../data/{}/{}/".format(user_id, study_item.get_study_item_id())
		if debug_mode:
			data_path = "../data_debug/{}/{}/".format(user_id, study_item.get_study_item_id())

		path = user.save_image(msg,
							   data_path, 
							   "{}".format(filename))
		
		#print(path)
		card = Card.from_study_info(study_item, card_id, path, 'image')
		user.temp_study_item.set_card(card)
		#print(str(user.temp_study_item))
		user.send_message("#image_received")

		if user.receive_queue.empty():
			
			message_handlers.add_item.save_word(user)

			subject = user.temp_study_item.get_subject() 
			topic = user.temp_study_item.get_topic()
			
			options = ['Yes', 'No']
			user.send_string_keyboard("#add_item_ask_more_items", options, (subject, topic))
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.SEND_IMAGE)]['done'])
		else:
			content_type = user.receive_queue.get()
			message_handlers.add_item.prepare_to_receive(user, content_type)
			user.set_state(fsm.next_state[(fsm.ADD_ITEM, fsm.SEND_IMAGE)][content_type])
