import wfdb
import os
import numpy as np

# train filename
apnea_ecg_train_filename = [
	"a01", "a02", "a03", "a04", "a05", "a06", "a07", "a08", "a09", "a10",
	"a11", "a12", "a13", "a14", "a15", "a16", "a17", "a18", "a19", "a20",
	"b01", "b02", "b03", "b04", "b05",
	"c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10"
]

# test filename
apnea_ecg_test_filename = [
	"x01", "x02", "x03", "x04", "x05", "x06", "x07", "x08", "x09", "x10",
	"x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
	"x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
	"x31", "x32", "x33", "x34", "x35"
]

# test label number
label_test = [523, 469, 465, 482, 505,
			  450, 509, 517, 508, 510,
			  457, 527, 506, 490, 498,
			  515, 400, 459, 487, 513,
			  510, 482, 527, 429, 510,
			  520, 498, 495, 470, 511,
			  557, 538, 473, 475, 483]


class ECGDataSegment:
	"""
	Minute-by-minute ECG segment.
	"""

	def __init__(self):
		self.data = None              # ECG segment data
		self.label = None             # ECG segment label
		self.database = "apnea-ecg"   # Database name
		self.filename = None          # Which file does it belong to?
		self.local_id = None          # The ID in file
		self.global_id = None         # global ID in database
	
	def write_ECG_Segment(self, file_path):
		"""
		Write Minute-by-minute ECG segment to txt file.
		:param string file_path: write path
		:return: None
		"""
		
		if not os.path.exists(file_path):
			os.makedirs(file_path)
			
		file_path += "/"
		filename = str(self.global_id) + ".txt"
		
		attr_name = "database_name file_name local_id global_id label\n"
		
		with open(file_path + filename, "w") as f:
			r"""attributes name """
			f.write(attr_name)
			
			r"""attributes value"""
			f.write(self.database + " " + self.filename + " " + str(self.local_id) + " " + str(
				self.global_id) + " " + self.label + "\n")
			
			r"""data"""
			for value in self.data:
				f.write(str(value[0]) + "\n")
	
	def read_ECG_Segment(self, file_path):
		"""
		Read Minute-by-minute ECG segment from TXT file
		:param string file_path: read path
		:return: None
		"""
		with open(file_path) as f:
			# attribute names
			_ = f.readline()
			
			# attribute values
			attrs_value = f.readline().replace("\n", "").split(" ")
			self.database = attrs_value[0]
			self.filename = attrs_value[1]
			self.local_id = int(attrs_value[2])
			self.global_id = int(attrs_value[3])
			self.label = attrs_value[4]
			# label_seg = attrs_value[2]
			
			# ECG segment data
			self.data = []
			data_value = f.readline().replace("\n", "")
			while data_value != "":
				self.data.append(float(data_value))
				data_value = f.readline().replace("\n", "")


def get_ecg_data_annotations(database_name, is_debug=False):
	"""
	Read files in specified database.
	:param string database_name: Database you want to read.
	:param bool is_debug: whether is debug mode.
	:return list: ecg data and annotations.
	
	example: data_set = get_ecg_data_annotations("train", True)
	"""
	
	data_annotations_set = []
	file_name_set = None
	no_apn = None
	
	if database_name == "train":
		file_name_set = apnea_ecg_train_filename
		no_apn = False
	elif database_name == "test":
		file_name_set = apnea_ecg_test_filename
		no_apn = True
	
	# if database name is test, we first read label file
	test_label_set = []
	if no_apn is True:
		# read event-2.txt, which is test label downloading from PhysioNet
		test_annotation_path = "D:/PhysioNet/Apnea/apnea-ecg/apnea-ecg/" + "event-2.txt"
		with open(test_annotation_path) as f:
			lines = f.readlines()
			for line in lines:
				line = line.replace("\n", "")
				for index_str in range(len(line)):
					if line[index_str] == "A" or line[index_str] == "N":
						test_label_set.append(line[index_str])
	
	file_count = 0		# use when the database name is test.
	test_label_index = 0		# use when the database name is test.
	for name in file_name_set:
		if is_debug:
			print("process file " + name + "...")
		
		file_path = "D:/PhysioNet/Apnea/apnea-ecg/apnea-ecg/" + name
		# use wfdb.rdrecord to read data
		ecg_data = wfdb.rdrecord(file_path)
		
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
			for index_label in range(label_test[file_count]):
				annotation_range_list.append(np.array(index_label*6000))
				annotation_list.append(test_label_set[test_label_index])
				test_label_index += 1
			file_count += 1
			annotation_range_list = np.array(annotation_range_list)

		data_annotations_set.append([ecg_data, annotation_range_list, annotation_list, name])
		
	return data_annotations_set
	

def ecg_data_segments_divide(database_name, data_annotations_set, is_debug=False):
	"""
	Divide ECG data to minute-by-minute ECG segment.
	:param string database_name: name of database
	:param list data_annotations_set: output of function get_ecg_data_annotations.
	:param bool is_debug: whether is debug mode.
	:return: None
	"""
	
	global_counter = 0		# use for global id
	eds = ECGDataSegment()
	
	base_floder_path = None
	
	if database_name == "train":
		base_floder_path = "data/dataset/train"
	elif database_name == "test":
		base_floder_path = "data/dataset/test"
	
	# ecg data segments divide
	for data_annotation in data_annotations_set:
		segment_amount = len(data_annotation[2])
		for index_segment in range(segment_amount):
			eds.data = data_annotation[0].p_signal[
					  data_annotation[1][index_segment]:(data_annotation[1][index_segment] + 6000)
					  ]
			eds.label = data_annotation[2][index_segment]
			eds.filename = data_annotation[3]
			eds.local_id = index_segment
			eds.global_id = global_counter
			eds.write_ECG_Segment(base_floder_path)
			global_counter += 1
			if is_debug:
				print("---------------------------------------------------")
				print(("local id: %s,  file name: %s, local id: %s" ) % (str(eds.global_id), eds.filename, str(eds.local_id)))
				print("---------------------------------------------------")
	
	# extra_info
	with open(base_floder_path + "/extra_info.txt", "w") as f:
		f.write("Number of ECG segments\n")
		f.write(str(global_counter))
		

def produce_train_database():
	"""
	Produce train database.
	The source data in apnea-ecg database is a01-a35, learning set provided by physionet.
	:return: None
	"""
	
	# read files from a01-a35, every file including whole ecg data and the corresponding annotation
	data_annotations_set = get_ecg_data_annotations("train", True)
	
	# divide ECG data to minute-by-minute ECG segments
	ecg_data_segments_divide("train", data_annotations_set, True)


def produce_test_database():
	"""
	Produce train database.
	The source data in apnea-ecg database is a01-a35, learning set provided by physionet.
	:return: None
	"""
	
	# read files from a01-a35, every file including whole ecg data and the corresponding annotation
	data_annotations_set = get_ecg_data_annotations("test", True)
	
	# divide ECG data to minute-by-minute ECG segments
	ecg_data_segments_divide("test", data_annotations_set, True)


def get_database(database_name, is_debug=False):
	"""
	Return the database you want to obtain.
	:param string database_name: name of database
	:param bool is_debug: whether is debug mode.
	:return list: train set
	"""
	
	base_floder_path = None
	database = []
	
	if database_name == "train":
		base_floder_path = "data/dataset/train"
	elif database_name == "test":
		base_floder_path = "data/dataset/test"
	
	# get the segment amount
	read_file_path = base_floder_path + "/extra_info.txt"
	with open(read_file_path) as f:
		_ = f.readline()
		attrs_value = f.readline().replace("\n", "").split(" ")
		segment_amount = int(attrs_value[0])
	
	# read ecg segment
	for segment_number in range(segment_amount):
		if is_debug is True:
			print("now read file: " + str(segment_number))
		
		eds = ECGDataSegment()
		read_file_path = base_floder_path + "/" + str(segment_number) + ".txt"
		eds.read_ECG_Segment(read_file_path)
		database.append(eds)
		
	if is_debug is True:
		print("length of database: %s" % len(database))
	
	return database


if __name__ == '__main__':
	# produce_train_database()
	# produce_test_database()
	train_set = get_database("train")
	
















	