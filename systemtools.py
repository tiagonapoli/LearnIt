from subprocess import call

def set_new_at_job_card(min_from_now,IDuser,IDcard,tried=0):
	command = 'echo "./sender.py {} {} {}" | at now + {} min'.format(IDuser,IDcard,tried,min_from_now)
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


