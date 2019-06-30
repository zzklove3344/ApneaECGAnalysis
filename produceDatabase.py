"""
	Produce train set and test set based on Apnea-ECG database.
"""
import numpy as np
from ECGSegment import ECGSegment
import os

def produce_database(database_name):
	"""
	
	:param database_name:
	:return None:
	"""
	
	if database_name == ["apnea-ecg", "train"] or database_name == ["apnea-ecg", "test"]:
		clear_id_set = np.load(database_name[0] + "_" + database_name[1] + "_clear_id.npy")
	else:
		raise Exception("Error database name.")
	dataset = []
	RRI_set = []
	RAMP_set = []
	EDR_set = []
	label_set = []
	for id in clear_id_set:
		eds = ECGSegment()
		eds.global_id = id
		eds.read_ecg_segment(1, database_name)
		eds.read_rri_ramp_edr()
		label_set.append(eds.label)
		RRI_set.append(eds.RR_intervals)
		RAMP_set.append(eds.R_peaks_amplitude)
		EDR_set.append(eds.EDR)
		dataset.append(eds)
		
	# substract mean of RRI,RAMP and EDR, RAMP * 10， EDR * 10000
	mean = np.mean(RRI_set, axis=1)
	mean = np.reshape(mean, (mean.shape[0], 1))
	rri_set = RRI_set - mean
	rri_set = np.reshape(rri_set, (rri_set.shape[0], rri_set.shape[1], 1))
	mean = np.mean(RAMP_set, axis=1)
	mean = np.reshape(mean, (mean.shape[0], 1))
	ramp_set = RAMP_set - mean
	ramp_set = np.reshape(ramp_set, (ramp_set.shape[0], ramp_set.shape[1], 1))
	ramp_set = ramp_set * 100
	mean = np.mean(EDR_set, axis=1)
	mean = np.reshape(mean, (mean.shape[0], 1))
	edr_set = EDR_set - mean
	edr_set = np.reshape(edr_set, (edr_set.shape[0], edr_set.shape[1], 1))
	edr_set = edr_set * 10000
	rri_amp_edr_set = np.concatenate([rri_set, ramp_set, edr_set], axis=2)
	
	if not os.path.exists("data/"):
		os.makedirs("data/")
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_dataset.npy", np.array(dataset))
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_rri.npy", np.array(rri_set))
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_ramp.npy", np.array(ramp_set))
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_edr.npy", np.array(edr_set))
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_rri_ramp_edr.npy", np.array(rri_amp_edr_set))
	np.save("data/" + database_name[0] + "_" + database_name[1] + "_clear_label.npy", np.array(label_set))


if __name__ == '__main__':
	# produce_database(["apnea-ecg", "train"])
	produce_database(["apnea-ecg", "test"])
	
		
