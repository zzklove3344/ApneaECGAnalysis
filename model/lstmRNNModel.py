"""
	LSTM-RNN model for  OSA detection.
"""

from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.utils import plot_model
import os
import numpy as np
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF

from model.common import TrainingMonitor, ModelCheckpoint, LossHistory

RR_INTERVALS_INTERPOLATION = 240
# handcraft_features

test_number = 1
base_floder_path = "result/lstm/" + "test_" + str(test_number) + "/"

if not os.path.exists(base_floder_path):
	os.makedirs(base_floder_path)
train_loss_path = base_floder_path + "train_loss.txt"
validation_loss_path = base_floder_path + "validation_loss.txt"
train_acc_path = base_floder_path + "train_acc.txt"
validation_acc_path = base_floder_path + "validation_acc.txt"

# GPU config
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.7
sess = tf.Session(config=config)
KTF.set_session(sess)


def get_dataset():
	train_rri_amp_edr = np.load("G:/python project/apneaECGCode/data/apnea-ecg_train_clear_rri_ramp_edr.npy")
	train_label = np.load("G:/python project/apneaECGCode/data/apnea-ecg_train_clear_label.npy")
	test_rri_amp_edr = np.load("G:/python project/apneaECGCode/data/apnea-ecg_test_clear_rri_ramp_edr.npy")
	test_label = np.load("G:/python project/apneaECGCode/data/apnea-ecg_test_clear_label.npy")
	
	train_label = train_label.astype(dtype=np.int)
	test_label = test_label.astype(dtype=np.int)
	return train_rri_amp_edr, train_label, test_rri_amp_edr, test_label


def create_lstm_model(input_shape):
	model = Sequential()
	model.add(LSTM(384, input_shape=input_shape, use_bias=True, dropout=0.1,
				   recurrent_dropout=0.05, return_sequences=True))
	# model.add(LeakyReLU(alpha=1))
	# model.add(BatchNormalization())
	model.add(LSTM(384, use_bias=True, dropout=0.2,
				   recurrent_dropout=0.05, return_sequences=True))
	# model.add(LeakyReLU(alpha=1))
	# model.add(BatchNormalization())
	model.add(LSTM(384, use_bias=True, dropout=0.3,
				   recurrent_dropout=0.05))
	# model.add(LeakyReLU(alpha=1))
	# model.add(BatchNormalization())
	# model.add(LSTM(64, use_bias=True,
	# 			   dropout=0.7, recurrent_dropout=0.7))
	# model.add(LeakyReLU(alpha=1))
	# model.add(BatchNormalization())
	model.add(Dense(128))
	# model.add(Dropout(0.8))
	# model.add(LeakyReLU(alpha=1))
	model.add(Dense(64))
	model.add(Dense(32))
	# model.add(Dropout(0.5))
	# model.add(LeakyReLU(alpha=1))
	model.add(Dense(1, activation="sigmoid"))
	
	model.compile(loss="binary_crossentropy", optimizer="adam", metrics=['accuracy'])
	
	model.summary()
	plot_model(model, to_file=base_floder_path + '/lstm_model.png', show_shapes=True)
	
	return model


def train_network():
	print("read data...")
	X_train1, y_train, X_test1, y_test = get_dataset()
	
	model = create_lstm_model(input_shape=(RR_INTERVALS_INTERPOLATION, 3))
	fig_path = base_floder_path
	model_file_path = base_floder_path + "/model"
	if not os.path.exists(model_file_path):
		os.makedirs(model_file_path)
	model_file_path += "/model_{epoch:02d}-{val_acc:.6f}.hdf5"
	checkpoint = ModelCheckpoint(model_file_path, monitor='val_acc', verbose=1, save_best_only=True)
	callbacks = [
		TrainingMonitor(fig_path, model, train_loss_path, validation_loss_path, train_acc_path, validation_acc_path)
		, checkpoint]
	print("Training")
	history = LossHistory()
	history.init()
	model.fit(X_train1, y_train, batch_size=128, epochs=500, callbacks=callbacks, validation_data=(X_test1, y_test))
	return model


if __name__ == '__main__':
	train_network()

