"""
	This file includes some preprocess methods about 60s ecg segments.
	
	functions:
		compute_features, including rr intervals,hrv, wavelet decomposition, tfr
	
	
"""

from features.rri import screen_segments_rr
from fileIO import get_database, get_some_ecg_segments
from features.rri import read_rr_intervals
from features.hrvFeatures import compute_hrv_features
from features.acf import compute_acf_vector, screen_segments_acf, read_acf_vector
from constant import ACF_LAGS, FMIN, FMAX
from features.wd import compute_wavelet_decomposition_result, write_wavelet_decomposition_result
from features.tfr import compute_st

import os


def compute_tfr_auxiliary(segments_set):
	"""
	Calculate tfr and write it to specific .npy file.
	We create a txt file, tfr_id_done.txt, to avoid repetitive calculation for saving time.
	:param list segments_set: a smaller ecg segments set than train set or test set.
	:return: None
	"""
	if not os.path.exists("tfr_id_done.txt"):
		with open("tfr_id_done.txt", "w"):
			print("create tfr_id_done.txt")
	
	for segment in segments_set:
		with open("tfr_id_done.txt", "r") as f:
			lines = f.readlines()
			id_set = []
			for line in lines:
				id_set.append(int(line.replace("\n", "")))
			if segment.global_id in id_set:
				# This segment had computed the tfr.
				continue
		
		compute_st(segment, FMIN, FMAX)
		
		# update the tfr_id file.
		with open("tfr_id_done.txt", "a+") as f:
			f.write(str(segment.global_id) + "\n")


def compute_features():
	"""
	Features including rr intervals, hrv, wavelet decomposition, tfr.
	:return: None
	"""
	# read database
	train_set = get_database(["apnea-ecg", "train"], True)
	test_set = get_database(["apnea-ecg", "test"], True) 
	
	# read rr intervals
	for segment in train_set:
		read_rr_intervals(segment)
	for segment in test_set:
		read_rr_intervals(segment)
	# screen ecg segments by rr intervals(label ecg segments noise or clear).
	screen_segments_rr(train_set, "train")
	screen_segments_rr(test_set, "test")
	# computer hrv features
	for segment in train_set:
		compute_hrv_features(segment)
	for segment in test_set:
		compute_hrv_features(segment)

	# compute acf vector
	for segment in train_set:
		compute_acf_vector(segment, ACF_LAGS, True)
	for segment in test_set:
		compute_acf_vector(segment, ACF_LAGS, True)
	# read acf vector
	for segment in train_set:
		read_acf_vector(segment)
	for segment in test_set:
		read_acf_vector(segment)
	# screen ecg segments by acf(label ecg segments noise or clear).
	screen_segments_acf(train_set, "train", True)
	screen_segments_acf(test_set, "test", True)

	# compute wavelet decomposition result of ecg segments.
	for segment in train_set:
		compute_wavelet_decomposition_result(segment)
	for segment in test_set:
		compute_wavelet_decomposition_result(segment)
	
	# compute time-frequency representation
	### Note: This step will consume much time and RAM, and memery error may happen.
	# start_indice, step, end_indice = 0, 100, 0
	# while end_indice < len(train_set):
	# 	if start_indice + step > len(train_set):
	# 		end_indice = len(train_set)
	# 	else:
	# 		end_indice = start_indice + step
	# 	compute_tfr(train_set[start_indice:end_indice])
	# 	start_indice = end_indice
	

if __name__ == '__main__':
	print("test statements...")
	compute_features()