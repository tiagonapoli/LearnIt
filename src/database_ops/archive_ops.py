import os
import logging
from utilities import logging_utils

class ArchiveOps():

	def __init__(self, conn, cursor, debug_mode):
		self.logger = logging.getLogger('db_api')
		self.debug_mode = debug_mode
		self.conn = conn
		self.cursor = cursor

	def erase_archive(self, user_id, card_id, counter):
		self.cursor.execute("SELECT type,content_path FROM archives WHERE user_id=%s AND user_card_id=%s AND counter=%s",
							(user_id, card_id, counter))
		archives = self.cursor.fetchall()
		if len(archives) == 0:
			self.logger.warning("Archive {}, {}, {} is not in {} archives".format(user_id, card_id, counter, user_id))
			return 

		for archive in archives:
			if (archive[0] == 'image' or archive[0] == 'audio') and os.path.exists(archive[1]):
				try:
					os.remove(archive[1])
					self.logger.info("Erased file {}".format(archive[1]))
				except Exception as e:
					self.logger.error("Error erasing Archive {}".format(archive[1]), exc_info=True)

		self.cursor.execute("DELETE FROM archives WHERE user_id=%s AND user_card_id=%s AND counter=%s",
							(user_id, card_id, counter))
		self.conn.commit()

		self.logger.info("{} - Archive successfuly removed".format(user_id))
		return 

