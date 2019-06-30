"""
	This file include some functions for converting raw Apnea-ECG database to many txt files, each txt file including
	 a 60s ECG segment corresponding with labels came from raw Apnea-ECG database.

	Before run this file, you first set path information.
	
	If you want to know more information about Apnea-ECG database, please see https://physionet.org/physiobank/database/apnea-ecg/.
	
"""

__version__ = '0.2'
__time__ = "2019.06.22"
__author__ = "zzklove3344"

import wfdb
import os
import numpy as np

# path information
# You need to set these file path before you run this file.
# Raw apnea-ecg database. You must download firstly.
APNEA_ECG_DATABASE_PATH = "G:/Apnea-ecg/raw records/"
# Folder for writing apnea-ecg 60s segments
SEGMENTS_BASE_PATH = "F:/Apnea-ecg/ecg segments/"

# The number of segments in train set
SEGMENTS_NUMBER_TRAIN = 17045
# The number of segments in test set
SEGMENTS_NUMBER_TEST = 17268

APNEA_ECG_TRAIN_FILENAME = [
	"a01", "a02", "a03", "a04", "a05", "a06", "a07", "a08", "a09", "a10",
	"a11", "a12", "a13", "a14", "a15", "a16", "a17", "a18", "a19", "a20",
	"b01", "b02", "b03", "b04", "b05",
	"c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10"
]

# The number of 60s segments for every subject in a01-a20, b01-b05, c01-c10
TRAIN_LABEL_AMOUNT = [489, 528, 519, 492, 454,
			  510, 511, 501, 495, 517,
			  466, 577, 495, 509, 510,
			  482, 485, 489, 502, 510,
			  487, 517, 441, 429, 433,
			  484, 502, 454, 482, 466,
			  468, 429, 513, 468, 431]

APNEA_ECG_TEST_FILENAME = [
	"x01", "x02", "x03", "x04", "x05", "x06", "x07", "x08", "x09", "x10",
	"x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
	"x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
	"x31", "x32", "x33", "x34", "x35"
]

# The number of 60s segments for every subject in x01-x35
TEST_LABEL_AMOUNT = [523, 469, 465, 482, 505,
			  450, 509, 517, 508, 510,
			  457, 527, 506, 490, 498,
			  515, 400, 459, 487, 513,
			  510, 482, 527, 429, 510,
			  520, 498, 495, 470, 511,
			  557, 538, 473, 475, 483]

ECG_RAW_FREQUENCY = 100


class Mit2Segment:
	"""
	Mit to 60s segments.
	"""
	
	def __init__(self):
		self.raw_ecg_data = None  # list, raw ecg data
		self.denoised_ecg_data = None 	# list, raw ecg data
		r"""basic attributes"""
		self.label = None  # int, 0 or 1
		self.database_name = None  # string, "apnea ecg"
		self.filename = None  # string, like "a01", "x02"
		self.local_id = None  # int, the ID in filename, like 101 in "a01"
		self.global_id = None  # int, global ID in database(train set or test set)
		self.samplefrom = None  # int, sample from where
		self.sampleto = None  # int, sample to where
		self.base_file_path = None		# string
		
	def write_ecg_segment(self, rdf):
		"""
		Write minute-by-minute ECG segment to txt file.
		:param int rdf: 0 means to write to raw ecg file, 1 means to write to denoised ecg file.
		:return: None
		"""
		
		# a01-a10, b01-b05 and c01-c10 belong to train set;
		# x01-x35 belong to test set.
		# if self.filename.find('x') >= 0:
		# 	file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id) + "/"
		# else:
		# 	file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id) + "/"
		if not os.path.exists(self.base_file_path):
			os.makedirs(self.base_file_path)
		if rdf == 0:
			filename = "raw_ecg_segment_data.txt"
			ecg_data = self.raw_ecg_data
		elif rdf == 1:
			filename = "denosing_ecg_segment_data.txt"
			ecg_data = self.denoised_ecg_data
		else:
			raise Exception("Error rdf value.")
		
		attr_name = "database_name file_name local_id samplefrom sampleto global_id label\n"
		# 将标签转化为数字
		if self.label == 'A':
			self.label = 1
		elif self.label == 'N':
			self.label = 0
		
		with open(self.base_file_path + filename, "w") as f:
			r"""attributes name """
			f.write(attr_name)
			
			r"""attributes value"""
			f.write(
				self.database_name[0] + " " + self.database_name[1] + " "
				+ self.filename + " " + str(self.local_id) + " "
				+ str(self.global_id) + " " + str(self.samplefrom) + " "
				+ str(self.sampleto) + " " + str(self.label) + "\n")
			
			r"""data"""
			for value in ecg_data:
				f.write(str(value[0]) + "\n")
	
	def read_ecg_segment(self, rdf, database_name_or_path):
		"""
		Read Minute-by-minute ECG segment from TXT file
		:param string or list database_name_or_path: the database or the file path you want to read
		:param int rdf: 0 means to read to raw ecg file, 1 means to read to denoised ecg file.
		:return: None
		"""
		
		if rdf == 0:
			filename = "raw_ecg_segment_data.txt"
		elif rdf == 1:
			filename = "denosing_ecg_segment_data.txt"
		else:
			raise Exception("Error rdf value.")
		if database_name_or_path == ["apnea-ecg", "train"]:
			file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id) + "/" + filename
		elif database_name_or_path == ["apnea-ecg", "test"]:
			file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id) + "/" + filename
		else:
			file_path = database_name_or_path
		
		with open(file_path) as f:
			_ = f.readline()
			
			# attribute values
			attrs_value = f.readline().replace("\n", "").split(" ")
			self.database_name = [attrs_value[0], attrs_value[1]]
			self.filename = attrs_value[2]
			self.local_id = int(attrs_value[3])
			self.global_id = int(attrs_value[4])
			self.samplefrom = int(attrs_value[5])
			self.sampleto = int(attrs_value[6])
			self.label = int(attrs_value[7])
			self.base_file_path = SEGMENTS_BASE_PATH + self.database_name[1] + "/" + str(self.global_id) + "/"
			
			# ECG segment data
			ecg_data = []
			data_value = f.readline().replace("\n", "")
			while data_value != "":
				ecg_data.append(float(data_value))
				data_value = f.readline().replace("\n", "")
			if rdf == 0:
				self.raw_ecg_data = ecg_data
			elif rdf == 1:
				self.denoised_ecg_data = ecg_data
	
	def read_edr(self, flag):
		"""
		flag为0时读取原始edr信号,为1时读取下采样之后的edr信号.
		:return: None
		"""
		
		edr = []
		if self.filename.find('x') >= 0:
			if flag == 0:
				file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id) + "/edr.txt"
			elif flag == 1:
				file_path = SEGMENTS_BASE_PATH + "test/" + str(self.global_id) + "/downsampling_EDR.txt"
			else:
				file_path = ""
				print("edr file path error....")
		else:
			if flag == 0:
				file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id) + "/edr.txt"
			elif flag == 1:
				file_path = SEGMENTS_BASE_PATH + "train/" + str(self.global_id) + "/downsampling_EDR.txt"
			else:
				file_path = ""
				print("edr file path error....")
		
		with open(file_path) as f:
			data_value = f.readline().replace("\n", "")
			while data_value != "":
				edr.append(float(data_value))
				data_value = f.readline().replace("\n", "")
			edr = np.array(edr)
		
		return edr


def get_ecg_data_annotations(database_name, is_debug=False):
	"""
	Read files in specified database.
	:param list database_name: Database you want to read.
							    Reserved paras, it must be ["apnea-ecg", "train"] or ["apnea-ecg", "test"] now.
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
		ecg_data = wfdb.rdrecord(file_path)  # use wfdb.rdrecord to read data
		
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
	                           Reserved paras, it must be ["apnea-ecg", "train"] or ["apnea-ecg", "test"] now.
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
			eds = Mit2Segment()
			eds.database_name = database_name
			eds.samplefrom = data_annotation[1][index_segment]
			if (data_annotation[1][index_segment] + 6000) > len(data_annotation[0].p_signal):
				eds.sampleto = len(data_annotation[0].p_signal)
			else:
				eds.sampleto = data_annotation[1][index_segment] + 6000
			eds.raw_ecg_data = data_annotation[0].p_signal[eds.samplefrom:eds.sampleto]
			eds.label = data_annotation[2][index_segment]
			eds.filename = data_annotation[3]
			eds.local_id = index_segment
			eds.global_id = global_counter
			eds.base_file_path = SEGMENTS_BASE_PATH + "/" + database_name[1] + "/" + str(eds.global_id) + "/"
			eds.write_ecg_segment(rdf=0)
			global_counter += 1
			data_set.append(eds)
			if is_debug:
				print("---------------------------------------------------")
				print(("global id: %s,  file name: %s, local id: %s") % (
					str(eds.global_id), eds.filename, str(eds.local_id)))
				print("---------------------------------------------------")
	
	if not os.path.exists(base_floder_path):
		os.makedirs(base_floder_path)
	
	# extra_info, this file store number of all ECG segments.
	with open(base_floder_path + "/extra_info.txt", "w") as f:
		f.write("Number of ECG segments\n")
		f.write(str(global_counter))
	
	return data_set


def produce_database(database_name, is_debug):
	"""
	Produce database. It will write many txt files in SEGMENTS_BASE_PATH.
	:param list database_name: name of database.
	                           Reserved paras, it must be ["apnea-ecg", "train"] or ["apnea-ecg", "test"] now.
	:param bool is_debug: whether is debug mode.
	:return: None
	"""
	
	# read files from a01-a35, every file including whole ecg data and the corresponding annotation
	data_annotations_set = get_ecg_data_annotations(database_name, is_debug)
	# divide ECG data to minute-by-minute ECG segments
	_ = process_ecg_data_segments(database_name, data_annotations_set, is_debug)


def produce_all_database(is_debug):
	"""
	Produce train database and test database.
	:param bool is_debug: whether is debug mode.
	:return: None
	"""
	produce_database(["apnea-ecg", "train"], is_debug)
	produce_database(["apnea-ecg", "test"], is_debug)


if __name__ == '__main__':
	print("fileIO test statements")
	# if you want to generate train database, you can run follow statement.
	# produce_database(["apnea-ecg", "train"], is_debug)
	
	# if you want to generate test database, you can run follow statement.
	# produce_database(["apnea-ecg", "test"], is_debug)
	
	# if you want to generate train and test database, you can run follow statement.
	produce_all_database(True)
