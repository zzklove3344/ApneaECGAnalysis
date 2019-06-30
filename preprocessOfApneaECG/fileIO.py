"""
	This file has some functions to read or write files.
"""

import random
from preprocessOfApneaECG.mit2Segments import Mit2Segment, SEGMENTS_BASE_PATH, SEGMENTS_NUMBER_TRAIN


def get_database(database_name, rdf, numRead=-1, is_debug=False):
	"""
	Return the database you want to obtain.
	:param list database_name: name of database
	:param int rdf: 0 means read raw ecg, 1 means denoised ecg.
	:param int numRead: the number you want read from database, -1 means read all data.
	:param bool is_debug: whether is debug mode.
	:return Mit2Segment list: database
	"""
	
	if database_name == ["apnea-ecg", "train"]:
		base_floder_path = SEGMENTS_BASE_PATH + "train/"
	elif database_name == ["apnea-ecg", "test"]:
		base_floder_path = SEGMENTS_BASE_PATH + "test/"
	else:
		raise Exception("Error database name.")
	
	# get the segment amount
	read_file_path = base_floder_path + "/extra_info.txt"
	with open(read_file_path) as f:
		_ = f.readline()
		attrs_value = f.readline().replace("\n", "").split(" ")
		segment_amount = int(attrs_value[0])
	# read ecg segment
	read_num = 0
	database = []
	for segment_number in range(segment_amount):
		if is_debug is True:
			print("now read file: " + str(segment_number))
		if numRead != -1 and read_num >= numRead:
			break
		eds = Mit2Segment()
		eds.global_id = segment_number
		eds.read_ecg_segment(rdf, database_name)
		database.append(eds)
		read_num += 1
	if is_debug is True:
		print("length of database: %s" % len(database))
	return database


def my_random_func(length, min_value, max_value):
	"""
	Given a range and the list length, return a no duplicates list.
	:param int length: list length.
	:param int min_value: min of range.
	:param int max_value: max of range.
	:return list: random list.
	"""
	random_list = []
	count = 0
	while count < length:
		random_value = random.randint(min_value, max_value)
		if random_value not in random_list:
			random_list.append(random_value)
			count = count + 1
	
	return random_list


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




def get_noise_dataset():
	"""
	读取ECG噪音片段.
	:return:
	"""
	
	id_path = "G:/Apnea-ecg/ecg_segments/data/denosing ecg data/" + "train/train_noise_id_matlab.txt"
	
	id_set = []
	with open(id_path) as f:
		lines = f.readlines()
		for line in lines:
			line = line.replace("\n", "")
			id_set.append(int(float(line)))
	
	# read ecg segment
	database = []
	for segment_number in id_set:
		print("now read file: " + str(segment_number))
		
		eds = ECGDataSegment()
		eds.global_id = segment_number
		# read_file_path = base_floder_path + str(segment_number) + "/" + "ecg segment data.txt"
		eds.read_denosing_ecg_segment("train")
		database.append(eds)
	
	print("length of database: %s" % len(database))
	
	return database


def get_some_ecg_segments(number):
	"""
	Return some ecg samples for debug.
	:param int number: the number of segments you want to sample from all ecg segments.
	:return list: ecg segments.
	"""
	
	random_list = my_random_func(number, 0, SEGMENTS_NUMBER_TRAIN)
	
	base_floder_path = SEGMENTS_BASE_PATH + "raw ecg data/train/"
	
	sample_segments = []
	for value in random_list:
		print("read %s" % value)
		eds = ECGDataSegment()
		eds.global_id = value
		read_file_path = base_floder_path + str(value) + "/" + "ecg segment data.txt"
		eds.read_raw_ecg_segment(read_file_path)
		sample_segments.append(eds)
	return sample_segments


def get_A_N_number(database):
	"""
	求出数据库database中A和N的片段数量.
	:param database:
	:return:
	"""
	
	A_number = 0
	N_number = 0
	for segment in database:
		if segment.label == 0:
			N_number += 1
		else:
			A_number += 1
	print("A number...")
	print(A_number)
	print("N number...")
	print(N_number)


if __name__ == '__main__':
	"""
	Test sentences:
	"""
	# Read trainset of apnea-ecg
	# trainset = get_database(["apnea-ecg", "train"], 0, is_debug=True)
	# Read testset of apnea-ecg
	testset = get_database(["apnea-ecg", "test"], 0, is_debug=True)


















