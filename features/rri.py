"""
	Compute rr intervals from R peaks which found Pan-Tomkins algorithm.

	https://zenodo.org/badge/latestdoi/55516257
	https://zenodo.org/record/583770
	source code: https://github.com/c-labpl/qrs_detector.
	We modified some codes for adapting apnea-ecg database.

	Author: Zhaokun Zhu
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from constant import SEGMENTS_BASE_PATH
from fileIO import write_txt_file, read_txt_file
from fileIO import get_some_ecg_segments, get_database


class MovingWindows(object):
	"""
	Moving window class.
	"""
	
	def __init__(self, windows_size, data, min_index, max_index):
		self.data = data
		self.size = windows_size
		self.min_index = min_index
		self.max_index = max_index
		self.max_value_index = np.argmax(self.data) + self.min_index  # 最大值下标
	
	def get_max_value(self):
		return np.max(self.data)


class QRSDetectorOffline(object):
	"""
	Python Offline ECG QRS Detector based on the Pan-Tomkins algorithm.

	Michał Sznajder (Jagiellonian University) - technical contact (msznajder@gmail.com)
	Marta Łukowska (Jagiellonian University)


	The module is offline Python implementation of QRS complex detection in the ECG signal based
	on the Pan-Tomkins algorithm: Pan J, Tompkins W.J., A real-time QRS detection algorithm,
	IEEE Transactions on Biomedical Engineering, Vol. BME-32, No. 3, March 1985, pp. 230-236.

	The QRS complex corresponds to the depolarization of the right and left ventricles of the human heart. It is the most visually obvious part of the ECG signal. QRS complex detection is essential for time-domain ECG signal analyses, namely heart rate variability. It makes it possible to compute inter-beat interval (RR interval) values that correspond to the time between two consecutive R peaks. Thus, a QRS complex detector is an ECG-based heart contraction detector.

	Offline version detects QRS complexes in a pre-recorded ECG signal dataset (e.g. stored in .csv format).

	This implementation of a QRS Complex Detector is by no means a certified medical tool and should not be used in health monitoring. It was created and used for experimental purposes in psychophysiology and psychology.

	You can find more information in module documentation:
	https://github.com/c-labpl/qrs_detector

	If you use these modules in a research project, please consider citing it:
	https://zenodo.org/record/583770

	If you use these modules in any other project, please refer to MIT open-source license.


	MIT License

	Copyright (c) 2017 Michał Sznajder, Marta Łukowska

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
	"""
	
	def __init__(self, ecg_data, write_path, verbose=True, log_data=False, plot_data=False, show_plot=False):
		"""
		Note by Zhaokun Zhu:
			In this function, we replaced ecg_data_path with ecg_data, which means we pass the data instead of data path.

		QRSDetectorOffline class initialisation method.
		:param ECGDataSegment ecg_data: input ecg data
		:param list write_path: [pic_path, indices_path]
					write path of store picture and R peaks indices
		:param bool verbose: flag for printing the results
		:param bool log_data: flag for logging the results
		:param bool plot_data: flag for plotting the results to a file
		:param bool show_plot: flag for showing generated results plot - will not show anything if plot is not generated
		"""
		# Configuration parameters.
		self.ecg_data_path = ""
		
		# self.signal_frequency = 250  # Set ECG device frequency in samples per second here.
		self.signal_frequency = 100  # samples per second in apnea-ecg is 100hz.
		
		self.filter_lowcut = 0.1
		self.filter_highcut = 15.0
		self.filter_order = 1
		
		self.integration_window = 7  # Change proportionally when adjusting frequency (in samples).
		
		self.findpeaks_limit = 0.25
		self.findpeaks_spacing = 20  # Change proportionally when adjusting frequency (in samples).
		
		self.refractory_period = 20  # Change proportionally when adjusting frequency (in samples).
		
		self.qrs_peak_filtering_factor = 0.125
		self.noise_peak_filtering_factor = 0.125
		self.qrs_noise_diff_weight = 0.25
		
		# Loaded ECG data.
		self.ecg_data_raw = None
		
		# Measured and calculated values.
		self.filtered_ecg_measurements = None
		self.differentiated_ecg_measurements = None
		self.squared_ecg_measurements = None
		self.integrated_ecg_measurements = None
		self.detected_peaks_indices = None
		self.detected_peaks_values = None
		
		self.qrs_peak_value = 0.0
		self.noise_peak_value = 0.0
		self.threshold_value = 0.0
		
		# Detection results.
		self.qrs_peaks_indices = np.array([], dtype=int)
		self.noise_peaks_indices = np.array([], dtype=int)
		
		# RR_intervals
		self.RR_intervals = np.array([], dtype=int)
		
		# Final ECG data and QRS detection results array - samples with detected QRS are marked with 1 value.
		self.ecg_data_detected = None
		
		# Run whole detector flow.
		self.load_ecg_data(ecg_data.data)
		self.detect_peaks()
		if len(self.detected_peaks_indices) != 0:
			self.detect_qrs()
			# Add by zzk.
			self.compute_RR_intervals()
		
		if verbose:
			self.print_detection_data()
		
		if log_data:
			self.peaks_indices_log_path = write_path[1]
			self.RR_intervals_log_path = write_path[3]
			self.log_detection_data()
		
		if plot_data:
			self.peaks_indices_plot_path = write_path[0]
			self.RR_intervals_plot_path = write_path[2]
			self.plot_detection_data(show_plot=show_plot)
	
	"""Loading ECG measurements data methods."""
	
	def load_ecg_data(self, data):
		"""
		Method loading ECG data set from a file.
		"""
		# self.ecg_data_raw = np.loadtxt(self.ecg_data_path, skiprows=1, delimiter=',')
		self.ecg_data_raw = np.array(data).reshape(len(data), 1)
	
	"""ECG measurements data processing methods."""
	
	def detect_peaks(self):
		"""
		Method responsible for extracting peaks from loaded ECG measurements data through measurements processing.
		"""
		# Extract measurements from loaded ECG data.
		ecg_measurements = self.ecg_data_raw
		
		# abandon by zzk. Measurements filtering - 0-15 Hz band pass filter.
		# Measurements filtering - 5-12 Hz band pass filter.
		self.filtered_ecg_measurements = self.bandpass_filter(ecg_measurements, lowcut=self.filter_lowcut,
															  highcut=self.filter_highcut,
															  signal_freq=self.signal_frequency,
															  filter_order=self.filter_order)
		self.filtered_ecg_measurements[:5] = self.filtered_ecg_measurements[5]
		
		# Derivative - provides QRS slope information.
		self.differentiated_ecg_measurements = np.ediff1d(self.filtered_ecg_measurements)
		
		# Squaring - intensifies values received in derivative.
		self.squared_ecg_measurements = self.differentiated_ecg_measurements ** 2
		
		# Moving-window integration.
		self.integrated_ecg_measurements = np.convolve(self.squared_ecg_measurements, np.ones(self.integration_window))
		
		# Fiducial mark - peak detection on integrated measurements.
		self.detected_peaks_indices = self.findpeaks_modify(data=self.integrated_ecg_measurements)
		
		if len(self.detected_peaks_indices) != 0:
			self.detected_peaks_values = self.integrated_ecg_measurements[self.detected_peaks_indices]
	
	"""QRS detection methods."""
	
	def detect_qrs(self):
		"""
		Method responsible for classifying detected ECG measurements peaks either as noise or as QRS complex (heart beat).
		"""
		for detected_peak_index, detected_peaks_value in zip(self.detected_peaks_indices, self.detected_peaks_values):
			
			try:
				last_qrs_index = self.qrs_peaks_indices[-1]
			except IndexError:
				last_qrs_index = 0
			
			# After a valid QRS complex detection, there is a 200 ms refractory period before next one can be detected.
			if detected_peak_index - last_qrs_index > self.refractory_period or not self.qrs_peaks_indices.size:
				# Peak must be classified either as a noise peak or a QRS peak.
				# To be classified as a QRS peak it must exceed dynamically set threshold value.
				if detected_peaks_value > self.threshold_value:
					self.qrs_peaks_indices = np.append(self.qrs_peaks_indices, detected_peak_index)
					
					# Adjust QRS peak value used later for setting QRS-noise threshold.
					self.qrs_peak_value = self.qrs_peak_filtering_factor * detected_peaks_value + \
										  (1 - self.qrs_peak_filtering_factor) * self.qrs_peak_value
				else:
					self.noise_peaks_indices = np.append(self.noise_peaks_indices, detected_peak_index)
					
					# Adjust noise peak value used later for setting QRS-noise threshold.
					self.noise_peak_value = self.noise_peak_filtering_factor * detected_peaks_value + \
											(1 - self.noise_peak_filtering_factor) * self.noise_peak_value
				
				# Adjust QRS-noise threshold value based on previously detected QRS or noise peaks value.
				self.threshold_value = self.noise_peak_value + \
									   self.qrs_noise_diff_weight * (self.qrs_peak_value - self.noise_peak_value)
		
		# Create array containing both input ECG measurements data and QRS detection indication column.
		# We mark QRS detection with '1' flag in 'qrs_detected' log column ('0' otherwise).
		measurement_qrs_detection_flag = np.zeros([len(self.ecg_data_raw), 1])
		measurement_qrs_detection_flag[self.qrs_peaks_indices] = 1
		self.ecg_data_detected = np.append(self.ecg_data_raw, measurement_qrs_detection_flag, 1)
	
	# print("..................")
	
	"""Results reporting methods."""
	
	def print_detection_data(self):
		"""
		Method responsible for printing the results.
		"""
		print("qrs peaks indices")
		print(self.qrs_peaks_indices)
		print("noise peaks indices")
		print(self.noise_peaks_indices)
	
	def log_detection_data(self):
		"""
		Method responsible for logging measured ECG and detection results to a TXT file.
		"""
		with open(self.peaks_indices_log_path, "w") as f:
			f.write(str(self.qrs_peaks_indices.tolist()))
		with open(self.RR_intervals_log_path, "w") as f:
			f.write(str(self.RR_intervals.tolist()))
	
	# print(".....................")
	# np.save(self.log_path, self.qrs_peaks_indices)
	# with open(self.log_path, "wb") as fin:
	# fin.write(b"timestamp,ecg_measurement,qrs_detected\n")
	# np.savetxt(fin, self.ecg_data_detected, delimiter=",")
	
	def plot_detection_data(self, show_plot=False):
		"""
		Method responsible for plotting detection results.
		:param bool show_plot: flag for plotting the results and showing plot
		"""
		
		def plot_data(axis, data, title='', fontsize=10):
			axis.set_title(title, fontsize=fontsize)
			axis.grid(which='both', axis='both', linestyle='--')
			axis.plot(data, color="salmon", zorder=1)
		
		def plot_points(axis, values, indices):
			# axis.scatter(x=indices, y=values[indices], c="black", s=50, zorder=2)
			# new_indices = []
			# for xx in range(len(indices)):
			# 	if indices[xx] < 1200:
			# 		new_indices.append(indices[xx])
			# new_indices = np.array(new_indices)
			axis.scatter(x=indices, y=values[indices], c="black", s=50, zorder=2)
		
		plt.close('all')
		fig, axarr = plt.subplots(1, sharex=True, figsize=(24, 18))
		
		# plot_data(axis=axarr[0], data=self.ecg_data_raw[:, 1], title='Raw ECG measurements')
		# plot_data(axis=axarr[0], data=self.ecg_data_raw, title='Raw ECG measurements') 	# add by zzk
		# plot_data(axis=axarr[1], data=self.filtered_ecg_measurements, title='Filtered ECG measurements')
		# plot_data(axis=axarr[2], data=self.differentiated_ecg_measurements, title='Differentiated ECG measurements')
		# plot_data(axis=axarr[3], data=self.squared_ecg_measurements, title='Squared ECG measurements')
		# plot_data(axis=axarr[4], data=self.integrated_ecg_measurements,
		# 		  title='Integrated ECG measurements with QRS peaks marked (black)')
		# plot_points(axis=axarr[4], values=self.integrated_ecg_measurements, indices=self.qrs_peaks_indices)
		plot_data(axis=axarr, data=self.ecg_data_raw,
				  title='Raw ECG measurements with QRS peaks marked (black)')
		plot_points(axis=axarr, values=self.ecg_data_raw, indices=self.qrs_peaks_indices)
		
		plt.tight_layout()
		fig.savefig(self.peaks_indices_plot_path)
		
		# plot RR intervals
		fig, axarr = plt.subplots(1, figsize=(8, 6))
		axarr.set_title("RR_intervals", fontsize=12)
		axarr.grid(which='both', axis='both', linestyle='--')
		axarr.plot(self.RR_intervals, color="salmon", zorder=1)
		fig.savefig(self.RR_intervals_plot_path)
		
		if show_plot:
			plt.show()
		
		plt.close()
	
	"""Tools methods."""
	
	def bandpass_filter(self, data, lowcut, highcut, signal_freq, filter_order):
		"""
		Method responsible for creating and applying Butterworth filter.
		:param deque data: raw data
		:param float lowcut: filter lowcut frequency value
		:param float highcut: filter highcut frequency value
		:param int signal_freq: signal frequency in samples per second (Hz)
		:param int filter_order: filter order
		:return array: filtered data
		"""
		nyquist_freq = 0.5 * signal_freq
		low = lowcut / nyquist_freq
		high = highcut / nyquist_freq
		b, a = butter(filter_order, [low, high], btype="band")
		y = lfilter(b, a, data)
		return y
	
	def findpeaks_modify(self, data):
		"""
		We use a window to replace one point. If the maximum value in a window both greater than the maximum value of its left
		window and its right window, this window will be chosen as a candidate window.
		Based on:
			Janko Slavic peak detection algorithm and implementation.
			https://github.com/jankoslavic/py-tools/tree/master/findpeaks
		Author: Zhaokun Zhu.

		:param ndarray data: data
		:return array: detected peaks indexes array
		"""
		
		limit = np.max(data) * 0.2  # adaptive value
		peak_windows_candidate = []  # candidate windows
		peaks_ind = []  # peaks indices
		
		window_size = 6  # window size of every window
		max_window_number = int(np.ceil(len(data) / window_size))
		windows_set = []  # all windows
		
		for index in range(max_window_number):
			min_index = index * window_size
			if (index + 1) * window_size > len(data):
				# In the end of data, it might not have enough data to divide. The window size will lower than window_size.
				data_t = data[index * window_size:len(data)]
				max_index = len(data)
			else:
				data_t = data[index * window_size:(index + 1) * window_size]
				max_index = (index + 1) * window_size - 1
			
			mws = MovingWindows(max_index - min_index, data_t, min_index, max_index)
			windows_set.append(mws)
		
		# find candidate windows
		for index in range(max_window_number):
			current_window_max_value = windows_set[index].get_max_value()
			if index == 0:
				left_window_max_value = 1.e-6
				right_window_max_value = windows_set[index + 1].get_max_value()
			elif index == max_window_number - 1:
				left_window_max_value = windows_set[index - 1].get_max_value()
				right_window_max_value = 1.e-6
			else:
				left_window_max_value = windows_set[index - 1].get_max_value()
				right_window_max_value = windows_set[index + 1].get_max_value()
			if current_window_max_value > left_window_max_value and current_window_max_value > right_window_max_value:
				peak_windows_candidate.append(windows_set[index])
		
		# The maximum of every candidate window are peaks.
		for index in range(len(peak_windows_candidate)):
			if peak_windows_candidate[index].get_max_value() > limit:
				peaks_ind.append(peak_windows_candidate[index].max_value_index)
		peaks_ind = np.array(peaks_ind)
		
		# redundancy detection and missing detection
		average_point_number = 8
		RR_set = []
		new_RR = []  # missing peaks
		prepare_del_RR = []  # redundancy peaks
		current_index = 0
		for index_ind in range(len(peaks_ind) - 1):
			current_RR_interval = peaks_ind[index_ind + 1] - peaks_ind[current_index]
			if len(RR_set) == 0:
				RR_average_interval = 0
			else:
				sum = 0
				for value in RR_set:
					sum += value
				RR_average_interval = sum / len(RR_set)
			
			if RR_average_interval == 0:
				RR_set.append(current_RR_interval)
				current_index = 1
			else:
				if current_RR_interval < RR_average_interval * 0.7:
					value_1 = data[peaks_ind[index_ind]]
					value_2 = data[peaks_ind[index_ind + 1]]
					if value_1 > value_2:
						if not ((index_ind + 1) in prepare_del_RR):
							prepare_del_RR.append(index_ind + 1)
						current_index = index_ind
					else:
						if not (index_ind in prepare_del_RR):
							prepare_del_RR.append(index_ind)
						current_index = index_ind + 1
				
				elif current_RR_interval > RR_average_interval * 1.66:
					if peaks_ind[index_ind + 1] - peaks_ind[index_ind] > 16:
						new_peak_ind = np.argmax(data[(peaks_ind[index_ind] + 8):(peaks_ind[index_ind + 1] - 8)]) + \
									   peaks_ind[index_ind] + 8
						new_RR.append(new_peak_ind)
						current_index = index_ind + 1
				else:
					if len(RR_set) >= average_point_number:
						del RR_set[0]
					RR_set.append(current_RR_interval)
					current_index = index_ind + 1
		
		# delete redundancy peaks and add missing peaks
		if len(prepare_del_RR) != 0:
			peaks_ind = np.delete(peaks_ind, prepare_del_RR)
		if len(new_RR) != 0:
			peaks_ind = np.append(peaks_ind, new_RR)
		
		peaks_ind.sort()
		peaks_ind = np.array(peaks_ind)
		return peaks_ind
	
	def compute_RR_intervals(self):
		"""
		Compute RR intervals based on R peaks indices.
		:return: None
		"""
		def smooth(a, WSZ):
			out0 = np.convolve(a, np.ones(WSZ, dtype=float), 'valid') / WSZ
			r = np.arange(1, WSZ - 1, 2)
			start = np.cumsum(a[:WSZ - 1])[::2] / r
			stop = (np.cumsum(a[:-WSZ:-1])[::2] / r)[::-1]
			return np.concatenate((start, out0, stop))
		
		def plot_rri(rri, title, fontsize):
			fig, axis = plt.subplots(1, 1)
			axis.set_title(title, fontsize=fontsize)
			axis.grid(which='both', axis='both', linestyle='--')
			axis.plot(rri, color="salmon", zorder=1)
		
		RR_intervals = []
		for index in range(len(self.qrs_peaks_indices) - 1):
			RR_intervals.append(self.qrs_peaks_indices[index + 1] - self.qrs_peaks_indices[index])
		
		# plot_rri(np.array(RR_intervals), "naive rri", 12)
		# plt.show()
		# plt.close()
		# ax.plot(rri)
		# ax.set(xlabel='Time (s)', ylabel='RRi (ms)')
		# # ax.legend()
		# plt.show(block=False)
		
		if not len(RR_intervals):
			self.RR_intervals = np.array(RR_intervals)
		else:
			self.RR_intervals = smooth(np.array(RR_intervals), 3)
		# plot_rri(self.RR_intervals, "ma rri", 12)
		# plt.show()
		# plt.close()
		# print("..........")
		# self.RR_intervals = np.array(RR_intervals)


def screen_segments_rr(dataset, name):
	noise_id_set = []
	clear_id_set = []
	
	for eds in dataset:
		print("process " + str(eds.global_id))
		if len(eds.rr_intervals) >= 40:
			eds.is_clear_by_rr_intervals = "True"
			for rri in eds.rr_intervals:
				if rri < 50 or \
						rri > 150:
					eds.is_clear_by_rr_intervals = "False"
		else:
			eds.is_clear_by_rr_intervals = "False"
		# update the base information file.
		eds.write_ecg_segment()
		if eds.is_clear_by_rr_intervals == "True":
			clear_id_set.append(eds.global_id)
		else:
			noise_id_set.append(eds.global_id)
	
	print("noise amount: %s, clear amount: %s" % (len(noise_id_set), len(clear_id_set)))
	with open(SEGMENTS_BASE_PATH + name + "/noise set id by rri.txt", "w") as f:
		f.write("noise id length" + str(len(noise_id_set)) + "\n")
		f.write(str(noise_id_set) + "\n")
	
	with open(SEGMENTS_BASE_PATH + name + "/clear set id by rri.txt", "w") as f:
		f.write("clear id length" + str(len(clear_id_set)) + "\n")
		f.write(str(clear_id_set) + "\n")


def compute_rr_intervals(ecg_segment):
	"""
	:param ECGDataSegment ecg_segment: A ECGDataSegment object.
	:return: None
	"""
	
	print(ecg_segment.global_id)
	
	if ecg_segment.filename.find('x') >= 0:
		peaks_pic_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_peaks_pic"
		peaks_indices_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_peaks.txt"
		rr_intervals_pic_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri_pic"
		rr_intervals_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri.txt"
	else:
		peaks_pic_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_peaks_pic"
		peaks_indices_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_peaks.txt"
		rr_intervals_pic_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri_pic"
		rr_intervals_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri.txt"
	qrs_detector = QRSDetectorOffline(ecg_data=ecg_segment,
									  write_path=[peaks_pic_path, peaks_indices_path,
												  rr_intervals_pic_path, rr_intervals_path],
									  verbose=False, log_data=True, plot_data=True, show_plot=False)
	ecg_segment.rr_intervals = qrs_detector.RR_intervals.tolist()


def write_rr_intervals(ecg_segment):
	"""
		:param ECGDataSegment ecg_segment: A ECGDataSegment object.
		:return: None
		
		Note:
			Abandoned 2019.2.23
	"""
	if ecg_segment.filename.find('x') >= 0:
		write_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/rr intervals.txt"
	else:
		write_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/rr intervals.txt"
	write_txt_file([ecg_segment.rr_intervals], write_path)


def read_rr_intervals(ecg_segment):
	"""
		:param ECGDataSegment ecg_segment: A ECGDataSegment object.
		:return: None
	"""
	if ecg_segment.filename.find('x') >= 0:
		read_path = SEGMENTS_BASE_PATH + "test/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri.txt"
	else:
		read_path = SEGMENTS_BASE_PATH + "train/" + str(ecg_segment.global_id) + "/" + str(ecg_segment.global_id) + "_rri.txt"
	read_line = read_txt_file(read_path)
	ecg_segment.rr_intervals = read_line[0]


if __name__ == "__main__":
	r""" debug """
	# get some ecg segments samples.
	# ecg_segments_set = get_some_ecg_segments(20)
	# for segment in ecg_segments_set:
	# 	compute_rr_intervals(segment)
		
	r""" compute rri for every 60s segments. """
	train_set = get_database(["apnea-ecg", "train"], True)
	for segment in train_set:
		compute_rr_intervals(segment)
	# test_set = get_database(["apnea-ecg", "test"], True)
	# for segment in test_set:
	# 	compute_rr_intervals(segment)
	
	