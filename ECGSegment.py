


import numpy as np
from preprocessOfApneaECG.mit2Segments import Mit2Segment, SEGMENTS_BASE_PATH, SEGMENTS_NUMBER_TRAIN


class ECGSegment(Mit2Segment):
	"""
		Every ECGSegment object includes some base informations and feature vectors.
	"""
	def __init__(self):
		# base attributions
		super(ECGSegment, self).__init__()
		# features
		self.RR_intervals = []
		self.R_peaks_amplitude = []
		self.EDR = []
	
	def read_rri_ramp_edr(self):
		self.RR_intervals = np.load(self.base_file_path + "/RRI.npy")  # RR intervals extracted from ECG.
		self.R_peaks_amplitude = np.load(self.base_file_path + "/RAMP.npy")  # R peaks amplitude extracted from ECG.
		self.EDR = np.load(self.base_file_path + "/EDR.npy")  # ECG-Derived Respiration signal
		
		