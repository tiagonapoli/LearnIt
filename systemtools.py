from subprocess import call

def set_new_at_job_VocabQuery(chat_id,min_from_now,text):
	time = "now + {} min".format(min_from_now)
	text = text.split(' ')
	if len(text) == 2 and len(text[1]) >= 1:
		command = 'echo "./sender.py {} \'{} {}\'" | at {}'.format(chat_id,text[0],text[1],time)
	else: 
		command = 'echo "./sender.py {} \'{} 0\'" | at {}'.format(chat_id,text[0],time)

	print(command)
	call(command,shell=True)


def test_set_at():
	command = 'echo "echo \\\"wololo 123123\\\"" | at now + 1 min'
	print(command)
	call(command, shell=True)

def main():
	set_new_at_job_VocabQuery(359999978,1,"query1")
	print("Done")


if __name__ == "__main__":
	main()
