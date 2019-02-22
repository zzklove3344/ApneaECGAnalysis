"""
	Before use this file, you first set the apnea_ecg_database_path, which the apnea-ecg database source files.
	This file include some functions about generate database and read database.

	Functions:
	produce_all_database: generate train and test minute-by-minute ecg segments.
							default folder: data/dataset/train and data/dataset/test
	get_database: external interface, get database("train", "test" or "all") which you want.
					note: before run get_database, you first run produce_train_database and produce_test_database.

	Note: you need first run function produce_all_database to generate ECG segments.
"""

import wfdb
import os
import numpy as np
from constant import *

import random


class ECGDataSegment:
	"""
	Minute-by-minute ECG segment.
	"""
	
	def __init__(self):
		r"""basic attributes"""
		self.data = None				# list
		self.label = None				# int, 0 or 1
		self.database_name = None		# string, "apnea ecg" or "ucddb"
		self.filename = None			# string, like "a01", "x02"
		self.local_id = None  			# int, the ID in filename, like 101 in "a01"
		self.global_id = None  			# int, global ID in database(train set or test set)
		self.is_clear_by_acf = "hold"  	# string, ECG clear label depended on acf vector.
												# "True", "False" or "hold", "hold" means this variable is intial state.
		self.is_clear_by_rr_intervals = "hold"  # string, "True", "False" or "hold", ECG clear label depended on rr intervals
		
		# feature attributes
		self.acf_vector = None  						# list, 1D, autocorrelation function vector
		self.wavelet_decomposition_result = None  		# ECG decomposition result
		self.rr_intervals = None						# rr intervals of self.data
		self.hrv_set = None  							# HRV analysis
		self.stockwell_tfr = None  						# st transform result
	
	def write_ecg_segment(self):
		"""
		Write minute-by-minute ECG segment to txt file.
		:return: None
		"""
		
		if self.filename.find('x') >= 0:
			file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id)
		else:
			file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id)
		
		if not os.path.exists(file_path):
			os.makedirs(file_path)
		
		file_path += "/"
		filename = "ecg segment data.txt"
		attr_name = "database_name file_name local_id global_id label clear_acf clear_rr\n"
		
		with open(file_path + filename, "w") as f:
			r"""attributes name """
			f.write(attr_name)

			r"""attributes value"""
			f.write(self.database_name + " " + self.filename + " " + str(self.local_id) + " " + str(self.global_id) + " " +
				self.label + " " + self.is_clear_by_acf + " " + self.is_clear_by_rr_intervals + "\n")

			r"""data"""
			for value in self.data:
				f.write(str(value[0]) + "\n")
	
	def read_ecg_segment(self, database_name_or_path):
		"""
		Read Minute-by-minute ECG segment from TXT file
		:param string database_name_or_path: the database or the file path you want to read
		:return: None
		"""
		
		if database_name_or_path == "train":
			file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id)
		elif database_name_or_path == "test":
			file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id)
		else:
			file_path = database_name_or_path + str(self.global_id)
		
		with open(file_path + "/ecg segment data.txt") as f:
			_ = f.readline()
			
			# attribute values
			attrs_value = f.readline().replace("\n", "").split(" ")
			self.database_name = attrs_value[0]
			self.filename = attrs_value[1]
			self.local_id = int(attrs_value[2])
			self.global_id = int(attrs_value[3])
			self.label = attrs_value[4]
			self.is_clear_by_acf = attrs_value[5]
			self.is_clear_by_rr_intervals = attrs_value[6]
			
			# label
			if self.label == "N":
				self.label = 0
			elif self.label == "A":
				self.label = 1
			
			# ECG segment data
			self.data = []
			data_value = f.readline().replace("\n", "")
			while data_value != "":
				self.data.append(float(data_value))
				data_value = f.readline().replace("\n", "")

	
def get_ecg_data_annotations(database_name, is_debug=False):
	"""
	Read files in specified database.
	:param list database_name: Database you want to read.
	:param bool is_debug: whether is debug mode.
	:return list: ecg data and annotations.

	example: data_set = get_ecg_data_annotations("train", True)
	"""
	
	data_annotations_set = []
	file_name_set = None
	no_apn = None
	
	if database_name[0] == "apnea-ecg":
		root_file_path = APNEA_ECG_DATABASE_PATH
		if database_name[1] == "train":
			file_name_set = APNEA_ECG_TRAIN_FILENAME
			no_apn = False
		elif database_name[1] == "test":
			file_name_set = APNEA_ECG_TEST_FILENAME
			no_apn = True
	
	# if database name is test, we first read label file
	test_label_set = []
	if no_apn is True:
		# read event-2.txt, which is test label downloading from PhysioNet
		test_annotation_path = root_file_path + "event-2.txt"
		with open(test_annotation_path) as f:
			lines = f.readlines()
			for line in lines:
				line = line.replace("\n", "")
				for index_str in range(len(line)):
					if line[index_str] == "A" or line[index_str] == "N":
						test_label_set.append(line[index_str])
	
	file_count = 0  # use when the database name is test.
	test_label_index = 0  # use when the database name is test.
	for name in file_name_set:
		if is_debug:
			print("process file " + name + "...")
		
		file_path = root_file_path + name
		ecg_data = wfdb.rdrecord(file_path)		# use wfdb.rdrecord to read data
		
		if no_apn is False:
			# use wfdb.rdann to read annotation
			annotation = wfdb.rdann(file_path, "apn")
			# annotation range
			annotation_range_list = annotation.sample
			# annotation
			annotation_list = annotation.symbol
		else:
			annotation_range_list = []
			annotation_list = []
			for index_label in range(TEST_LABEL_AMOUNT[file_count]):
				annotation_range_list.append(np.array(index_label * 6000))
				annotation_list.append(test_label_set[test_label_index])
				test_label_index += 1
			file_count += 1
			annotation_range_list = np.array(annotation_range_list)
		
		data_annotations_set.append([ecg_data, annotation_range_list, annotation_list, name])
	
	return data_annotations_set


def process_ecg_data_segments(database_name, data_annotations_set, is_debug=False):
	"""
	Divide ECG data to minute-by-minute ECG segment.
	:param list database_name: name of database.
	:param list data_annotations_set: output of function get_ecg_data_annotations.
	:param bool is_debug: whether is debug mode.
	:return: None
	"""
	
	data_set = []
	global_counter = 0  # use for global id
	
	base_floder_path = None
	
	if database_name[0] == "apnea-ecg":
		if database_name[1] == "train":
			base_floder_path = SEGMENTS_BASE_PATH + "/train"
		elif database_name[1] == "test":
			base_floder_path = SEGMENTS_BASE_PATH + "/test"
	
	# ecg data segments divide
	for data_annotation in data_annotations_set:
		segment_amount = len(data_annotation[2])
		for index_segment in range(segment_amount):
			eds = ECGDataSegment()
			eds.database_name = database_name[0]
			eds.data = data_annotation[0].p_signal[
					   data_annotation[1][index_segment]:(data_annotation[1][index_segment] + 6000)
					   ]
			eds.label = data_annotation[2][index_segment]
			eds.filename = data_annotation[3]
			eds.local_id = index_segment
			eds.global_id = global_counter
			
			eds.write_ecg_segment()
			global_counter += 1
			data_set.append(eds)
			if is_debug:
				print("---------------------------------------------------")
				print(("local id: %s,  file name: %s, local id: %s") % (
					str(eds.global_id), eds.filename, str(eds.local_id)))
				print("---------------------------------------------------")
	
	if not os.path.exists(base_floder_path):
		os.makedirs(base_floder_path)
		
	# extra_info
	with open(base_floder_path + "/extra_info.txt", "w") as f:
		f.write("Number of ECG segments\n")
		f.write(str(global_counter))
	
	return data_set


def produce_train_database():
	"""
	Produce train database.
	The source data in apnea-ecg database is a01-a35, learning set provided by physionet.
	:return: None
	"""
	
	# read files from a01-a35, every file including whole ecg data and the corresponding annotation
	data_annotations_set = get_ecg_data_annotations(["apnea-ecg", "train"], True)
	# divide ECG data to minute-by-minute ECG segments
	dataset = process_ecg_data_segments(["apnea-ecg", "train"], data_annotations_set, True)
	

def produce_test_database():
	"""
	Produce train database.
	The source data in apnea-ecg database is a01-a35, learning set provided by physionet.
	:return: None
	"""
	
	# read files from a01-a35, every file including whole ecg data and the corresponding annotation
	data_annotations_set = get_ecg_data_annotations(["apnea-ecg", "test"], True)
	
	# divide ECG data to minute-by-minute ECG segments
	dataset = process_ecg_data_segments(["apnea-ecg", "test"], data_annotations_set, True)


def produce_all_database():
	"""
	produce train database and test database.
	:return: None
	"""
	produce_train_database()
	produce_test_database()


def get_database(database_name, is_debug=False):
	"""
	Return the database you want to obtain.
	:param string database_name: name of database
	:param bool is_debug: whether is debug mode.
	:return list: database
	"""
	
	def get_ecg_segments(database_name):
		database = []
		base_floder_path = SCREEN_SEGMENT_PATH + database_name + "/"
		# count = 0
		
		# # get the segment amount
		# read_file_path = base_floder_path + "/extra_info.txt"
		# with open(read_file_path) as f:
		# 	_ = f.readline()
		# 	attrs_value = f.readline().replace("\n", "").split(" ")
		# 	segment_amount = int(attrs_value[0])
		if database_name == "train":
			segment_amount = TRAIN_ALL_AMOUNT
		else:
			segment_amount = TEST_ALL_AMOUNT
		
		# read ecg segment
		for segment_number in range(segment_amount):
			if is_debug:
				print("now read file: " + str(segment_number))
			
			# if count > 10:
			# 	break
			
			eds = ECGDataSegment()
			eds.global_id = segment_number
			eds.read_ecg_segment(database_name)
			if len(eds.data) == 6000:
				database.append(eds)
		
		# count += 1
		
		if is_debug:
			print("length of database: %s" % len(database))
		return database
	
	if database_name == "train":
		train_set = get_ecg_segments("train")
		return train_set
	elif database_name == "test":
		test_set = get_ecg_segments("test")
		return test_set
	elif database_name == "all":
		train_set = get_ecg_segments("train")
		test_set = get_ecg_segments("test")
		return train_set, test_set


# if database_name == "train":
# 	base_floder_path = "data/dataset/train"
# 	train_database = get_ecg_segments(base_floder_path)
# 	return train_database
# elif database_name == "test":
# 	base_floder_path = "data/dataset/test"
# 	test_database = get_ecg_segments(base_floder_path)
# 	return test_database
# elif database_name == "all":
# 	base_floder_path = "data/dataset/train"
# 	train_database = get_ecg_segments(base_floder_path)
# 	base_floder_path = "data/dataset/test"
# 	test_database = get_ecg_segments(base_floder_path)
# 	return train_database, test_database


def get_database_length(database_name):
	"""
	Return the sample amount of specific database.
	:param database_name: specific database
	:return list or int:
			If database_name is train or test, int.
			If database_name is all, list, [train_length, test_length].
	"""
	
	read_path = "data/dataset/train/extra_info.txt"
	with open(read_path) as f:
		_ = f.readline()
		attrs_value = f.readline().replace("\n", "").split(" ")
		train_length = int(attrs_value[0])
	read_path = "data/dataset/test/extra_info.txt"
	with open(read_path) as f:
		_ = f.readline()
		attrs_value = f.readline().replace("\n", "").split(" ")
		test_length = int(attrs_value[0])
	if database_name == "train":
		return train_length
	elif database_name == "test":
		return test_length
	elif database_name == "all":
		return [train_length, test_length]
	else:
		print("WRONG Argument....")


def read_database(read_path, is_debug=False):
	"""
	For the specific read path, read all file in read folder path.
	:param string read_path: read folder path.
	:param bool is_debug: whether is debug mode.
	:return list: database
	"""
	
	database = []
	file_name_set = os.listdir(read_path)
	# read ecg segment
	for file_name in file_name_set:
		if is_debug is True:
			print("now read file: " + file_name)
		
		eds = ECGDataSegment()
		read_file_path = read_path + "/" + file_name
		eds.read_ecg_segment(read_file_path)
		database.append(eds)
	
	if is_debug is True:
		print("length of database: %s" % len(database))
	
	return database


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


def get_specific_segments(database_name, clear_or_noise, is_debug=False):
	"""
	Get the clear segments of specific database.
	:param sting database_name: specific database, "train", "test", "all"
	:param string clear_or_noise: clear segments or noise segments.
	:param is_debug: whether is debug mode.
	:return list: database
	"""
	
	if database_name == "train":
		if clear_or_noise == "clear":
			train_clear_set = read_database(SCREEN_SEGMENT_PATH + "train/clear segment/", is_debug)
			return train_clear_set
		elif clear_or_noise == "noise":
			train_noise_set = read_database(SCREEN_SEGMENT_PATH + "train/noise segment/", is_debug)
			return train_noise_set
	elif database_name == "test":
		if clear_or_noise == "clear":
			test_clear_set = read_database(SCREEN_SEGMENT_PATH + "test/clear segment/", is_debug)
			return test_clear_set
		elif clear_or_noise == "noise":
			test_noise_set = read_database(SCREEN_SEGMENT_PATH + "test/noise segment/", is_debug)
			return test_noise_set
	elif database_name == "all":
		if clear_or_noise == "clear":
			train_clear_set = read_database(SCREEN_SEGMENT_PATH + "train/clear segment/", is_debug)
			test_clear_set = read_database(SCREEN_SEGMENT_PATH + "test/clear segment/", is_debug)
			return [train_clear_set, test_clear_set]
		elif clear_or_noise == "noise":
			train_noise_set = read_database(SCREEN_SEGMENT_PATH + "train/noise segment/", is_debug)
			test_noise_set = read_database(SCREEN_SEGMENT_PATH + "test/noise segment/", is_debug)
			return [train_noise_set, test_noise_set]


def read_sample_records(sample_number):
	"""
	Read some sample record from apnea-ecg database, as default in apnea-ecg train database.
	:param
		int sample_number: the number of records you want.
	:return:
		list: sample records.
	"""
	
	data_set = []
	for index in range(sample_number):
		file_path = apnea_ecg_database_path + apnea_ecg_train_filename[index]
		data = wfdb.rdrecord(file_path)
		data_set.append(data.p_signal)
	return data_set


def read_screening_result_by_acf():
	# noise_id_set = []
	# clear_id_set = []
	line = read_txt_file("train" + "noise set id.txt")
	train_noise_id_set = line[0]
	line = read_txt_file("train" + "clear set id.txt")
	train_clear_id_set = line[0]
	line = read_txt_file("test" + "noise set id.txt")
	test_noise_id_set = line[0]
	line = read_txt_file("test" + "clear set id.txt")
	test_clear_id_set = line[0]
	
	# print("--------------")
	return [[train_noise_id_set, train_clear_id_set], [test_noise_id_set, test_clear_id_set]]


def read_screening_result_by_rri():
	line = read_txt_file("train" + "noise set id by rri.txt")
	train_noise_id_set = line[0]
	line = read_txt_file("train" + "clear set id by rri.txt")
	train_clear_id_set = line[0]
	line = read_txt_file("test" + "noise set id by rri.txt")
	test_noise_id_set = line[0]
	line = read_txt_file("test" + "clear set id by rri.txt")
	test_clear_id_set = line[0]
	
	# print("--------------")
	return [[train_noise_id_set, train_clear_id_set], [test_noise_id_set, test_clear_id_set]]


def read_dict(read_path, number):
	config_dict = {}
	read_path = read_path + "test_" + str(number) + "/config.txt"
	with open(read_path) as f:
		line = f.readline().replace("\n", "")
		while line != "":
			line = line.split(": ")
			item_name = line[0]
			item_value = int(line[1])
			config_dict.update({item_name: item_value})
			line = f.readline().replace("\n", "")
	
	return config_dict


def write_dict(config_dict, write_path, number):
	write_path = write_path + "test_" + str(number)
	if not os.path.exists(write_path):
		os.makedirs(write_path)
	
	write_path += "/config.txt"
	
	with open(write_path, "w") as f:
		for item in config_dict:
			f.write(item + ": " + str(config_dict[item]) + "\n")


def my_random_func(length, min_value, max_value):
	random_list = []
	count = 0
	while count < length:
		random_value = random.randint(min_value, max_value)
		if random_value not in random_list:
			random_list.append(random_value)
			count = count + 1
	
	return random_list


def read_random_samples(samples_number, database_name):
	# train_set, test_set = get_database(database_name, is_debug=True)
	random_values_train = my_random_func(samples_number, 0, TRAIN_ALL_AMOUNT)
	random_values_test = my_random_func(samples_number, 0, TEST_ALL_AMOUNT)
	
	train_samples = []
	test_samples = []
	for value in random_values_train:
		print("read %s" % value)
		eds = ECGDataSegment()
		eds.global_id = value
		eds.read_ecg_segment("train")
		train_samples.append(eds)
	
	for value in random_values_test:
		print("read %s" % value)
		eds = ECGDataSegment()
		eds.global_id = value
		eds.read_ecg_segment("test")
		train_samples.append(eds)
	# test_samples.append(test_set[value])
	
	return train_samples, test_samples


if __name__ == '__main__':
	# dy = np.array([3])
	# print(dy)
	print("fileIO test statements")
	# if you want to generate train database, you can run follow statement.
	# produce_train_database()
	
	# if you want to generate test database, you can run follow statement.
	# produce_test_database()
	
	# if you want to generate train and test database, you can run follow statement.
	produce_all_database()
	
	# train_set, test_set = get_database("all", True)
	
	print(".........")
	# You can run the follow statement in external file to get the database you want.
	"""
	Example:
		from common.fileIO import get_database
		train_set = get_database("train")
	"""
	
	# eds = ECGDataSegment()
	# eds.global_id = 1541
	# eds.read_ecg_segment("train")
	# eds.compute_rr_intervals()