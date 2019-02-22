"""
	This file contains some constant including file path, file name, etc.

"""

r""" relating to file path """
# raw apnea-ecg database
APNEA_ECG_DATABASE_PATH = "D:/PhysioNet/Apnea/apnea-ecg-test-label/apnea-ecg/"
# folder for writing apnea-ecg 60s segments
SEGMENTS_BASE_PATH = "D:/PhysioNet/Apnea/ecg segments/"

r""" relating to apnea-ecg database """
APNEA_ECG_TRAIN_FILENAME = [
	"a01", "a02", "a03", "a04", "a05", "a06", "a07", "a08", "a09", "a10",
	"a11", "a12", "a13", "a14", "a15", "a16", "a17", "a18", "a19", "a20",
	"b01", "b02", "b03", "b04", "b05",
	"c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10"
]
APNEA_ECG_TEST_FILENAME = [
	"x01", "x02", "x03", "x04", "x05", "x06", "x07", "x08", "x09", "x10",
	"x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
	"x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
	"x31", "x32", "x33", "x34", "x35"
]
# the number of 60s segments for every subject in x01-x35
TEST_LABEL_AMOUNT = [523, 469, 465, 482, 505,
			  450, 509, 517, 508, 510,
			  457, 527, 506, 490, 498,
			  515, 400, 459, 487, 513,
			  510, 482, 527, 429, 510,
			  520, 498, 495, 470, 511,
			  557, 538, 473, 475, 483]
# the number of segments in train set
SEGMENTS_NUMBER_TRAIN = 17045
# the number of segments in test set
SEGMENTS_NUMBER_TEST = 17268


r""" relating to acf """
# ACF vector length
ACF_LAGS = 13

r""" relating to wavelet decomposition """
WAVELET_NAME = "sym8"
DECOMPOSITION_LEVEL = 8

r""" relating to rr intervals """
# folder for storing R peaks of ecg segments
R_PEAKS_DIR = "D:/Apnea Analysis features/Peaks indices/"
# folder for storing plot of R peaks ecg segments
R_PEAKS_PLOT_DIR = "D:/Apnea Analysis pic/QRS detection/"
# folder for storing RRI of ecg segments
RR_INTERVALS_DIR = "D:/Apnea Analysis features/RR intervals/"
# folder for storing plot of RRI
RR_INTERVALS_PLOT_DIR = "D:/Apnea Analysis pic/RR intervals/"
