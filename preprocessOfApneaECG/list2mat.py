"""

"""

import scipy.io as sio
from preprocessOfApneaECG.mit2Segments import Mit2Segment


def list2mat(segment, is_debug=False):
	"""
	Convert python list to matlab .mat file.
	:param Mit2Segment segment: python list of ecg data.
	:param bool is_debug: python list of ecg data.
	:return None:
	"""
	
	if is_debug:
		print("Convert list to .mat %s" % str(segment.global_id))
	name = segment.base_file_path + 'denoised_ecg_data.mat'
	sio.savemat(name, {'denoised_ecg_data': segment.denoised_ecg_data})