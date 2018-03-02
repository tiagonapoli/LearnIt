#! /usr/bin/python3
import os

username = os.getlogin()

os.system('sudo apt-get update')

os.system('sudo apt-get install postgresql postgresql-contrib')
os.system('sudo apt-get install python3-pip')
os.system('sudo pip3 install --upgrade psycopg2')
os.system('sudo pip3 install --upgrade psycopg2-binary')
os.system('sudo pip3 install --upgrade requests')
os.system('sudo pip3 install --upgrade urllib3')
os.system('sudo pip3 install --upgrade pyTelegramBotAPI')


print("Creating psql user {} with password 'abcde'. You can change it later, if you want. But then you must change on ./credentials/connect_str.txt and ./credentials/connect_str_debug.txt too.".format(username))
os.system("sudo -u postgres psql -c \"CREATE USER {} WITH PASSWORD 'abcde';\"".format(username))
os.system("sudo -u postgres psql -c \"ALTER USER {} WITH SUPERUSER;\"".format(username))


f = open('./credentials/connect_str.txt', 'w')
f.write('dbname=learnit user={} host=localhost password=abcde'.format(username))
f.close()

f = open('./credentials/connect_str_debug.txt', 'w')
f.write('dbname=learnit_debug user={} host=localhost password=abcde'.format(username))
f.close()

os.system("sudo -u postgres psql -c 'CREATE DATABASE {};'".format(username))
os.system("sudo -u postgres psql < create_db.sql")

os.system("sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE learnit to {};'".format(username))
os.system("sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE learnit_debug to {};'".format(username))


print("Type the LearnIt bot token:")
token = input()
f = open('./credentials/bot_token.txt', 'w')
f.write(token)
f.close()


print("Type the LearnIt debug bot token:")
token = input()
f = open('./credentials/bot_debug_token.txt', 'w')
f.write(token)
f.close()


