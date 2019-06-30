"""
	主要包括去燥, 计算特征信号等
"""
from preprocessOfApneaECG.fileIO import get_database
from preprocessOfApneaECG.denoising import denoise_ecg
from preprocessOfApneaECG.list2mat import list2mat
import os
import numpy as np
import matlab.engine
import scipy.io as sio
from scipy import interpolate
from preprocessOfApneaECG.mit2Segments import ECG_RAW_FREQUENCY
from scipy.signal import decimate

eng = matlab.engine.start_matlab()

# interpolation algorithm.
# From https://github.com/rhenanbartels/hrv/blob/develop/hrv/classical.py


def create_time_info(rri):
	rri_time = np.cumsum(rri) / 1000.0  # make it seconds
	return rri_time - rri_time[0]   # force it to start at zero


def create_interp_time(rri, fs):
	time_rri = create_time_info(rri)
	# print(time_rri[-1])
	start, end = 0, 0
	if time_rri[-1] < 60:
		end = 60
	else:
		print("abnormal %s..." % time_rri[-1])
	return np.arange(0, end, 1 / float(fs))


def interp_cubic_spline(rri, fs):
	time_rri = create_time_info(rri)
	time_rri_interp = create_interp_time(rri, fs)
	tck_rri = interpolate.splrep(time_rri, rri, s=0)
	rri_interp = interpolate.splev(time_rri_interp, tck_rri, der=0)
	return rri_interp


def interp_cubic_spline_qrs(qrs_index, qrs_amp, fs):
	time_qrs = qrs_index / float(ECG_RAW_FREQUENCY)
	time_qrs = time_qrs - time_qrs[0]
	time_qrs_interp = np.arange(0, 60, 1 / float(fs))
	tck = interpolate.splrep(time_qrs, qrs_amp, s=0)
	qrs_interp = interpolate.splev(time_qrs_interp, tck, der=0)
	return qrs_interp


def smooth(a, WSZ):
	"""
	滑动平均.
	:param a:
	:param WSZ:
	:return:
	"""
	out0 = np.convolve(a, np.ones(WSZ, dtype=float), 'valid') / WSZ
	r = np.arange(1, WSZ - 1, 2)
	start = np.cumsum(a[:WSZ - 1])[::2] / r
	stop = (np.cumsum(a[:-WSZ:-1])[::2] / r)[::-1]
	return np.concatenate((start, out0, stop))



def mat2npy(dict_data):
	print("........")

def rricheck(ecg_data, rr_intervals):
	"""
	# Check ECG data and RR intervals.
	:param numpy array ecg_data: ECG signal.
	:param numpy array rr_intervals: RR intervals.
	:return bool:
	"""
	noise_flag = rr_intervals > 180
	noise_flag1 = rr_intervals < 30
	if len(rr_intervals) < 40 \
			or np.sum(noise_flag) > 0 \
			or np.sum(noise_flag1) > 0 \
			or len(ecg_data) != 6000:
		return False
	else:
		return True


def compute_r_peak_amplitude(ecg_data, rwave):
	"""
	Compute R peaks amplitude based on R waves indices.
	:param numpy array ecg_data: ECG signal.
	:param numpy array rwave: R waves indices.
	:return numpy array: R peak amplitude.
	"""
	
	wave_amp = []
	for peak_ind in rwave.tolist():
		interval = 25
		if peak_ind - interval < 0:
			start = 0
		else:
			start = peak_ind - interval
		
		if peak_ind + interval > len(ecg_data):
			end = len(ecg_data)
		else:
			end = peak_ind + interval
		
		amp = np.max(ecg_data[start:end])
		wave_amp.append(amp)
	return np.array(wave_amp)


def pre_proc(dataset, database_name, is_debug=False):
	"""
	
	:param Mit2Segment list dataset: ECG segments.
	:return None:
	"""
	
	clear_id_set, noise_id_set = [], []
	for segment in dataset:
		if is_debug:
			print("now process %s	id=%s." % (segment.database_name, str(segment.global_id)))
		# denoising and write to txt file
		segment.denoised_ecg_data = denoise_ecg(segment.raw_ecg_data)
		segment.write_ecg_segment(rdf=1)
		# ecg data list to .mat
		list2mat(segment, is_debug=True)
		# compute RRI, RAMP and EDR.
		eng.computeFeatures(segment.base_file_path)
		if os.path.exists(segment.base_file_path + "/Rwave.mat"):
			RwaveMat = sio.loadmat(segment.base_file_path + "/Rwave.mat")
			Rwave = np.transpose(RwaveMat['Rwave'])
			Rwave = np.reshape(Rwave, len(Rwave))
			# RR intervals
			RR_intervals = np.diff(Rwave)
			# store RR intervals
			np.save(segment.base_file_path + "/RRI.npy", RR_intervals)
			# RRI validity check
			rri_flag = rricheck(segment.denoised_ecg_data, RR_intervals)
			if rri_flag:
				clear_id_set.append(segment.global_id)
			else:
				noise_id_set.append(segment.global_id)
				continue
			# compute R peaks amplitude(RAMP)
			RAMP = compute_r_peak_amplitude(segment.denoised_ecg_data, Rwave)
			# smoothing filtering
			RRI = smooth(RR_intervals, 3)
			RAMP = smooth(RAMP, 3)
			# spline interpolation
			RRI = RRI / ECG_RAW_FREQUENCY * 1000.0
			RRI = interp_cubic_spline(RRI, fs=4)
			RAMP = interp_cubic_spline_qrs(Rwave, RAMP, fs=4)
			# store RRI and RAMP
			np.save(segment.base_file_path + "/RRI.npy", RRI)
			np.save(segment.base_file_path + "/RAMP.npy", RAMP)
			# EDR
			EDRMat = sio.loadmat(segment.base_file_path + "/EDR.mat")
			EDR = np.transpose(EDRMat['EDR'])
			EDR = np.reshape(EDR, len(EDR))
			# downsampling
			EDR = decimate(EDR, 25)
			np.save(segment.base_file_path + "/EDR.npy", EDR)
			# print(".............")
		else:
			noise_id_set.append(segment.global_id)
	print(len(noise_id_set))
	print(len(clear_id_set))
	np.save(database_name[0] + "_" + database_name[1] + "_clear_id.npy", np.array(clear_id_set))
	np.save(database_name[0] + "_" + database_name[1] + "_noise_id.npy", np.array(noise_id_set))
	

if __name__ == '__main__':
	# train_set = get_database(["apnea-ecg", "train"], rdf=0,is_debug=True)
	# pre_proc(train_set, ["apnea-ecg", "train"], is_debug=True)
	test_set = get_database(["apnea-ecg", "test"], rdf=0, is_debug=True)
	pre_proc(test_set, ["apnea-ecg", "test"], is_debug=True)
	



