"""
	This file is to solve the problem of baseline drift of ECG signal.
	
	The methods come from Yildiz et al. paper, "An expert system for automated recognition of patients with obstructive sleep apnea using electrocardiogram recordings".
	
	Firstly, use wavelet decomposition on ECG signal to six level and get cD1 to cD6, cA6. Secondly, set the cD6 to zero.
	Lastly, use wavelet reconstruction on cD1 to cD6(zeros) and cA6, and achieve denoising ECG signal.
	
	I summarize frequency band of some waves in ECG signals.
	P wave: atrial depolarization, 心房除极.
	QRS complexes: ventricular depolarization，心室去极.
	T wave: ventricular repolarization, 心室复极.
	P and T waves range: 0.5hz-10hz.
	QRS complex range: 10hz-25hz.
	Detail signal D2 is used as a reference signal for the detection of QRS fiducial location.

	cD1: 25-50hz
	cD2: 12.5-25hz
	cD3: 6.25-12.5hz
	cD4: 3.125-6.25hz
	cD5: 1.5625-3.125hz
	cD6: 0.78125-1.5625hz
	cD7: 0.390625-0.78125hz
	cA7: 0-0.390625hz
	
"""

__version__ = '0.1'
__time__ = "2019.06.22"
__author__ = "zzklove3344"


import pywt
import numpy as np


def denoise_ecg(ecg_segment):
	"""
	Remove baseline drafts from ECG signal.
	:param ecg_segment: ecg record, a numpy array.
	:return: denoised ecg record, a numpy array.
	
	Example:
	denoising_ecg = denoise_ecg(raw_ecg)
	"""
	
	denoising_wd_level = 6
	denoising_wd_wavelet = "db6"
	coffes_set = []
	cA_signal = np.reshape(ecg_segment, len(ecg_segment))
	for index_dec in range(denoising_wd_level):
		cA, cD = pywt.dwt(cA_signal, denoising_wd_wavelet)
		coffes_set.append(cD)
		cA_signal = cA
	coffes_set.append(cA_signal)
	coffes_set[denoising_wd_level] = np.zeros(len(coffes_set[denoising_wd_level]))
	
	cA_signal = coffes_set[denoising_wd_level]
	for index_dec in range(denoising_wd_level):
		cD_signal = coffes_set[denoising_wd_level - 1 - index_dec]
		if len(cD_signal) != len(cA_signal):
			cA_signal = np.delete(cA_signal, len(cA_signal) - 1, axis=0)
		cA_signal = pywt.idwt(cA_signal, cD_signal, denoising_wd_wavelet)
	cA_signal = np.reshape(cA_signal, (len(ecg_segment), 1))
	return cA_signal


