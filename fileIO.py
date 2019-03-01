"""
	This file has some file input and output functions.
"""

from divideSegments import ECGDataSegment
from constant import SEGMENTS_BASE_PATH, SEGMENTS_NUMBER_TRAIN, SEGMENTS_NUMBER_TEST
from common import my_random_func


def write_txt_file(list_info, write_file_path):
	"""
	Write list object to TXT file.
	:param list list_info: List object you want to write.
	:param string write_file_path: TXT file path.
	:return: None
	"""
	with open(write_file_path, "w") as f:
		for info in list_info:
			f.write(str(info) + "\n")


def read_txt_file(read_file_path):
	"""
	Read TXT file to list object.
	:param string read_file_path: TXT file path.
	:return list: list object
	"""
	with open(read_file_path) as f:
		list_t = []
		lines = f.readlines()
		for line in lines:
			float_list = []
			str_t = line.replace("[", "").replace("]", "").replace("\n", "").split(",")
			for str_s in str_t:
				if str_s != "":
					float_list.append(float(str_s))
				else:
					print(read_file_path)
			list_t.append(float_list)
	
	return list_t


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
			# read_wavelet_decomposition(eds)
			
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


def get_some_ecg_segments(number):
	"""
	Return some ecg samples for debug.
	:param int number: the number of segments you want to sample from all ecg segments.
	:return list: ecg segments.
	"""
	
	random_list = my_random_func(number, 0, SEGMENTS_NUMBER_TRAIN)
	
	sample_segments = []
	for value in random_list:
		print("read %s" % value)
		eds = ECGDataSegment()
		eds.global_id = value
		eds.read_ecg_segment("train")
		sample_segments.append(eds)
	return sample_segments




		
if __name__ == '__main__':
	print("test statement")
	# train_set = get_database(["apnea-ecg", "train"], True)	 # read train set of apnea-ecg database
	# test_set = get_database(["apnea-ecg", "test"], True)		# read test set of apnea-ecg database
	# read train set and test set of apnea-ecg database simultaneously
	train_set, test_set = get_database(["apnea-ecg", "all"], True)
