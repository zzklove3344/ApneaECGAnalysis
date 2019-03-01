"""
	Compute autocorrelation function vector.
	
	Note:
		When you run function screen_segments_acf, it will consume about four hours per 10 thousands ecg segments.
"""

import numpy as np
from constant import SEGMENTS_BASE_PATH, NOISE_THRESHOLD, ACF_LAGS
from fileIO import write_txt_file, read_txt_file, get_database
from sklearn import preprocessing
import os


def compute_acf_vector(ecg_segment, lags, is_debug=False):
	"""
	:param ECGDataSegment ecg_segment: A ECGDataSegment object.
	:param int lags: length of acf vector.
	:param bool is_debug: True or False
	:return: None
	"""
	
	def compute_auto_corr(data, lag_k):
		data = np.reshape(data, len(data))
		mean = np.mean(data)  # mean of series
		var = np.var(data) * len(data)  # var of series
		length = len(data)
		sub_series_1 = data[0: length - lag_k]
		sub_series_2 = data[lag_k:]
		auto_corr = 0
		if var == 0:
			return 0.0
		else:
			for index in range(length - lag_k):
				auto_corr += (sub_series_1[index] - mean) * (sub_series_2[index] - mean) / var
			return auto_corr
	
	if is_debug:
		print("now process %s" % str(ecg_segment.global_id))
	ACF_vector = []
	for index_lags in range(lags):
		temp_auto_corr = compute_auto_corr(ecg_segment.data, index_lags + 1)
		ACF_vector.append(temp_auto_corr)
	ecg_segment.acf_vector = ACF_vector
	write_acf_vector(ecg_segment)


def write_acf_vector(ecg_segment):
	"""
	Write acf vector to specific txt file.
	:param ECGDataSegment ecg_segment: A ECGDataSegment object.
	:return: None
	"""
	
	if ecg_segment.filename.find('x') >= 0:
		write_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_acf_vector.txt"
	else:
		write_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_acf_vector.txt"
	write_txt_file([ecg_segment.acf_vector], write_path)


def read_acf_vector(ecg_segment):
	"""
		Read acf vector from specific txt file.
		:param ECGDataSegment ecg_segment: A ECGDataSegment object.
		:return: None
	"""
	
	if ecg_segment.filename.find('x') >= 0:
		read_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_acf_vector.txt"
	else:
		read_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_acf_vector.txt"
	ecg_segment.acf_vector = read_txt_file(read_path)


def compute_distance_auto_corr_vector(ecg_segment1, ecg_segment2):
	"""
	dst = (Xs - Xs_) * (Xt - Xt_)' / (sqrt((Xs - Xs_)*(Xs - Xs_)')) * (sqrt((Xt - Xt_)*(Xt - Xt_)')))
	Xs and Xt are ACF of two different ECG segments.
	Xs_ and Xt_ are the mean of the Xs and Xt.
	:param ECGDataSegment ecg_segment1: ECG minute-by-minute segment1
	:param ECGDataSegment ecg_segment2: ECG minute-by-minute segment2
	:return float: distance of two segment autocorrelation vector.
	"""
	
	v1, v2 = np.array(ecg_segment1.acf_vector), np.array(ecg_segment2.acf_vector)
	
	if len(v1) != len(v1):
		print("Abnormal!!! %s and %s" % (str(ecg_segment1.globao_id), str(ecg_segment2.globao_id)))
	mean_1 = np.mean(v1)
	std_1 = np.std(v1, ddof=1)
	mean_2 = np.mean(v2)
	std_2 = np.std(v2, ddof=1)
	
	if std_1 == 0 or std_2 == 0:
		return 0.0
	else:
		dst = np.sum((v1 - mean_1) * (v2 - mean_2)) / (
				std_1 * std_2 * len(v1 - 1))
		return dst


def screen_segments_acf(ecg_segments_set, database_name, is_debug=False):
	"""
	A method based on auto_corr screen ECG segments(clear or noise)
	:param list ecg_segments_set: ECG segment database, "train" or "test".
	:param string database_name: "train" or "test".
	:param bool is_debug: True or False.
	:return: None
	"""
	
	# compute acf distance between two acf vectors.
	if not os.path.exists(SEGMENTS_BASE_PATH + database_name + "/" + database_name +  "_sum_minmax_info.txt"):
		sum_vector = []
		i = 0
		while i < len(ecg_segments_set):
			if is_debug:
				print("column is " + str(i))
			column = []
			j = 0
			while j < len(ecg_segments_set):
				distance_s_t = compute_distance_auto_corr_vector(ecg_segments_set[i], ecg_segments_set[j])
				if distance_s_t == 0.0:
					column.append(distance_s_t)
					print("find a abnormal segment....")
				else:
					column.append(distance_s_t)
				j += 1
			# if mean of one segment distances with other segments low than 0.8, it will be removed.
			column = np.array(column)
			sum_column = np.sum(column)
			sum_vector.append(sum_column)
			i += 1
		
		with open(SEGMENTS_BASE_PATH + database_name + "/" + database_name + "_sum_info.txt", "w") as f:
			for sum in sum_vector:
				f.write(str(sum) + "\n")
		
		min_max_scaler = preprocessing.MinMaxScaler()
		sum_vector_minmax = min_max_scaler.fit_transform(sum_vector)
		sum_vector_minmax_list = sum_vector_minmax.tolist()
		
		with open(SEGMENTS_BASE_PATH + database_name + "/" + database_name + "_sum_minmax_info.txt", "w") as f:
			for sum_minmax in sum_vector_minmax_list:
				f.write(str(sum_minmax) + "\n")
	else:
		# read ...sum_minmax_info.txt
		sum_vector_minmax_list = []
		with open(SEGMENTS_BASE_PATH + database_name + "/" + database_name + "_sum_minmax_info.txt", "r") as f:
			lines = f.readlines()
			for line in lines:
				sum_vector_minmax_list.append(float(line.replace('\n', ' ')))
	
	# compute or read clear set id and noise set id
	if not os.path.exists(SEGMENTS_BASE_PATH + database_name + "/noise set id by acf.txt"):
		noise_id_set = []
		clear_id_set = []
		index = 0
		for sum_minmax in sum_vector_minmax_list:
			# you can change the NOISE_THRESHOLD in constant.py.
			if sum_minmax < NOISE_THRESHOLD:
				ecg_segments_set[index].is_clear = False
				noise_id_set.append(ecg_segments_set[index].global_id)
			else:
				ecg_segments_set[index].is_clear = True
				clear_id_set.append(ecg_segments_set[index].global_id)
			index += 1
		
		if is_debug:
			print("noise amount: %s, clear amount: %s" % (len(noise_id_set), len(clear_id_set)))
		with open(SEGMENTS_BASE_PATH + database_name + "/noise set id by acf.txt", "w") as f:
			f.write("length " + str(len(noise_id_set)) + "\n")
			f.write(str(noise_id_set) + "\n")
		with open(SEGMENTS_BASE_PATH + database_name + "/clear set id by acf.txt", "w") as f:
			f.write("length " + str(len(clear_id_set)) + "\n")
			f.write(str(clear_id_set) + "\n")
	else:
		# read clear set id by acf and noise set id by acf
		noise_id_set = []
		clear_id_set = []
		with open(SEGMENTS_BASE_PATH + database_name + "/noise set id by acf.txt", "r") as f:
			_ = f.readline()
			lines = f.readline().replace("[", "").replace("]", "").split(",")
			for line in lines:
				noise_id_set.append(int(line))
		with open(SEGMENTS_BASE_PATH + database_name + "/clear set id by acf.txt", "r") as f:
			_ = f.readline()
			lines = f.readline().replace("[", "").replace("]", "").split(",")
			for line in lines:
				clear_id_set.append(int(line))
				
	# update clear flag depended on acf distances.
	for segment in ecg_segments_set:
		if is_debug:
			print("now process %s" % str(segment.global_id))
		if segment.global_id in clear_id_set:
			segment.is_clear_by_acf = "True"
			segment.write_ecg_segment()
		elif segment.global_id in noise_id_set:
			segment.is_clear_by_acf = "False"
			segment.write_ecg_segment()
		else:
			print("Fatal error in screen_segments_acf")


if __name__ == '__main__':
	print("test statements")
	# Firstly, you should compute acf vector
	train_set = get_database(["apnea-ecg", "train"], True)
	for segment in train_set:
		compute_acf_vector(segment, ACF_LAGS)
	# Secondly, you can use acf vectors to label noise or clear segments based on acf vectors.
	for segment in train_set:
		read_acf_vector(segment)
	screen_segments_acf(train_set, "train", True)
	# You can also use acf vectors as features. We will upload some examples later.
