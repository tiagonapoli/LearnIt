from subprocess import call

def set_new_at_job_card(chat_id,min_from_now,text):
	time = "now + {} min".format(min_from_now)
	text = text.split(' ')
	if len(text) == 2 and len(text[1]) >= 1:
		command = 'echo "./sender.py {} \'{} {}\'" | at {}'.format(chat_id,text[0],text[1],time)
	else: 
		command = 'echo "./sender.py {} \'{} 0\'" | at {}'.format(chat_id,text[0],time)

	print(command)
	call(command,shell=True)

def schedule_daily_setup(days_from_now):
	command = 'echo "./daily_setup.py" | at 8:00 tomorrow'.format(days_from_now)
	print(command)
	call(command, shell=True)

def schedule_setup_now():
	command = 'echo "./daily_setup.py" | at now + 1 min'.format(days_from_now)
	print(command)
	call(command, shell=True)


