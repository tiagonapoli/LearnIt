from subprocess import call
import datetime

def set_new_at_job_card(min_from_now,user_id,card_id,tried=0):
	"""
		Creates a new 'at' card job, i.e, schedules a card to be sent to an user.

		Args:
			min_from_now: the job will be schedulet at 'min_from_now' minutes
			user_id: user id
			card_id: card id
			tried: number of unsuccessfull tries to send this card to this user
	"""
	
	command = 'echo "./sender.py {} {} {}" | at now + {} min'.format(user_id,card_id,tried,min_from_now)

	print(command)
	call(command,shell=True)

def schedule_daily_setup():
	"""
		Creates a new 'at' job to execute daily setup tomorrow, 8 AM.
	"""
	
	day = "tomorrow"
	now = datetime.datetime.now()
	
	if now.hour < 8:
		day = ""

	command = 'echo "./dailysetup.py" | at 8:01 ' + day
	print(command)
	call(command, shell=True)

def schedule_setup_now():
	"""
		Creates a new 'at' job to execute daily setup 1 minute from now.
	"""
	
	command = 'echo "./dailysetup.py" | at now + 3 min'
	print(command)
	call(command, shell=True)


def main():
	pass

if __name__ == '__main__':
	main()
