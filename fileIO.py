"""
	This file has some file input and output functions.
"""

from divideSegments import ECGDataSegment
from constant import SEGMENTS_BASE_PATH, SEGMENTS_NUMBER_TRAIN, SEGMENTS_NUMBER_TEST


def get_database(database_name, is_debug=False):
	"""
	Return the database you want to obtain.
	:param list database_name: name of database
	:param bool is_debug: whether is debug mode.
	:return list: database
	"""
	
	def get_ecg_segments(read_path, segments_number):
		"""
		Read ecg segments from specific path.
		:param string read_path: ecg segments path.
		:param int segments_number: the number of segments you want to read.
		:return list: ecg segments.
		"""
		
		database = []
		# read ecg segment
		for segment_number in range(segments_number):
			if is_debug:
				print("now read file: " + str(segment_number))
			eds = ECGDataSegment()
			eds.global_id = segment_number
			eds.read_ecg_segment(read_path)
			# if len(eds.data) == 6000:
			database.append(eds)
		if is_debug:
			print("length of database: %s" % len(database))
		return database
	
	if database_name[0] == "apnea-ecg":
		if database_name[1] == "train":
			path = SEGMENTS_BASE_PATH + "train/"
			train_set = get_ecg_segments(path, SEGMENTS_NUMBER_TRAIN)
			return train_set
		elif database_name[1] == "test":
			path = SEGMENTS_BASE_PATH + "test/"
			test_set = get_ecg_segments(path, SEGMENTS_NUMBER_TEST)
			return test_set
		elif database_name[1] == "all":
			path = SEGMENTS_BASE_PATH + "train/"
			train_set = get_ecg_segments(path, SEGMENTS_NUMBER_TRAIN)
			path = SEGMENTS_BASE_PATH + "test/"
			test_set = get_ecg_segments(path, SEGMENTS_NUMBER_TEST)
			return train_set, test_set
		
		
if __name__ == '__main__':
	print("test statement")
	# train_set = get_database(["apnea-ecg", "train"], True)	 # read train set of apnea-ecg database
	# test_set = get_database(["apnea-ecg", "test"], True)		# read test set of apnea-ecg database
	# read train set and test set of apnea-ecg database simultaneously
	train_set, test_set = get_database(["apnea-ecg", "all"], True)
