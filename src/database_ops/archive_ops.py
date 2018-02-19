import psycopg2
import os

class ArchiveOps():

	def __init__(self, conn, cursor):
		self.conn = conn
		self.cursor = cursor

	def erase_archive(self, user_id, card_id, counter):
		self.cursor.execute("SELECT type,content_path FROM archives WHERE user_id={} AND user_card_id={} AND counter={}"
						.format(user_id, card_id, counter))
		archives = self.cursor.fetchall()
		if len(archives) == 0:
			print("ERROR in erase_archive, dbapi")
			print("Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter))
			return "Archive {}, {}, {} is not in yout archives".format(user_id, card_id, counter); 

		for archive in archives:
			if (archive[0] == 'image' or archive[0] == 'audio') and os.path.exists(archive[1]):
				try:
					os.remove(archive[1])
					print("Erased file {}".format(archive[1]))
				except Exception as e:
					print("ERROR in erase_language - Archive {}".format(archive[1]))
					print(e)

		self.cursor.execute("DELETE FROM archives WHERE user_id={} AND user_card_id={} AND counter={}"
						.format(user_id, card_id, counter))
		self.conn.commit()
		return "Archive successfuly removed"

