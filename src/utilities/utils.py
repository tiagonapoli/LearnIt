import os
import datetime

def get_file_extension(filename):
	path, extension = os.path.splitext(filename)
	return extension 


def create_dir_card_archive(user_id, word_id, debug_mode):
	if debug_mode:
		if not os.path.exists('../data_debug/{}/{}'.format(user_id, word_id)):
			os.makedirs('../data_debug/{}/{}'.format(user_id, word_id))
	else:
		if not os.path.exists('../data/{}/{}'.format(user_id, word_id)):	
					os.makedirs('../data/{}/{}'.format(user_id, word_id))


def study_items_to_string_list(study_items):
	ret = []
	for item in study_items:
		ret.append(item.get_sendable_study_item())
	return ret


def backup(user_manager, debug_mode):
	if debug_mode:
		PATH =  "../backup_debug/" + datetime.datetime.now().strftime("%d-%m-%Y.%H-%M") + "/"
	else:
		PATH =  "../backup/" + datetime.datetime.now().strftime("%d-%m-%Y.%H-%M") + "/"
	if not os.path.exists(PATH):
		os.makedirs(PATH)
	print("BACKUP PATH= " + PATH)
	try:
		print(user_manager.backup(PATH))
		if debug_mode:
			os.system("cp -TRv ../data_debug/ {}data".format(PATH))
		else:
			os.system("cp -TRv ../data/ {}data".format(PATH))
		return "Data backup was successfull"
	except Exception as e:
		print(e);
		return "Data backup failed"

