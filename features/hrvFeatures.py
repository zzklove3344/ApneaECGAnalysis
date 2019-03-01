"""
	HRV: heart rate variability.
	Compute hrv including time domain, frequency domain, nonlinear features.
	
	Note:
		Before you run this file, you have to run rri.py to get the rr intervals of every ecg 60s segments.
"""

from hrv.rri import RRi
from hrv.filters import moving_average
from hrv.classical import time_domain, frequency_domain, non_linear
from constant import SEGMENTS_BASE_PATH
from fileIO import write_txt_file, read_txt_file
from fileIO import get_database, get_some_ecg_segments
from features.rri import read_rr_intervals


def plot_rri(rri, filt_rri):
	import matplotlib.pyplot as plt
	
	fig, ax = plt.subplots(1, 1)
	# fig, ax = plt.subplot(1, 1)
	ax.plot(rri.time, rri.rri)
	ax.plot(filt_rri.time, filt_rri.rri)
	ax.set(xlabel='Time (s)', ylabel='RRi (ms)')
	ax.legend()
	plt.show()


def compute_hrv_features(ecg_segment):
	"""
		
		:param ECGDataSegment ecg_segment: A ECGDataSegment object.
		:return: None
	"""
	
	if ecg_segment.is_clear_by_rr_intervals == "True":
		# change measure unit of rri into ms
		new_rri_list = []
		for value in ecg_segment.rr_intervals:
			new_value = int(value) * 10
			new_rri_list.append(new_value)
		
		rri = RRi(new_rri_list)
		filt_rri = moving_average(rri, order=3) 	# moving average
		# plot_rri(rri, filt_rri)
		
		# compute features
		time_feature = time_domain(filt_rri)
		frequency_features = frequency_domain(filt_rri, fs=60 / len(ecg_segment.rr_intervals))
		nonlinear_features = non_linear(filt_rri)
		features = {}
		features.update(time_feature)
		features.update(frequency_features)
		features.update(nonlinear_features)
		
		ecg_segment.hrv_set = list(features.values())
		write_hrv_set(ecg_segment)
	elif ecg_segment.is_clear_by_rr_intervals == "False":
		ecg_segment.hrv_set = []
		write_hrv_set(ecg_segment)
	

def write_hrv_set(ecg_segment):
	"""

		:param ECGDataSegment ecg_segment: A ECGDataSegment object.
		:return: None
	"""
	if ecg_segment.filename.find('x') >= 0:
		write_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_hrv_features.txt"
	else:
		write_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_hrv_features.txt"
	write_txt_file([ecg_segment.hrv_set], write_path)


def read_hrv_set(ecg_segment):
	if ecg_segment.filename.find('x') >= 0:
		read_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_hrv_features.txt"
	else:
		read_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_hrv_features.txt"
	read_line = read_txt_file(read_path)
	ecg_segment.hrv_set = read_line[0]


if __name__ == '__main__':
	r""" debug """
	# get some ecg segments samples.
	# ecg_segments_set = get_some_ecg_segments(20)
	# for segment in ecg_segments_set:
	# 	read_rr_intervals(segment)
	# 	compute_hrv_features(segment)
	
	r""" Example: compute train set hrv features. """
	train_set = get_database(["apnea-ecg", "train"], True)
	for segment in train_set:
		read_rr_intervals(segment)
		compute_hrv_features(segment)