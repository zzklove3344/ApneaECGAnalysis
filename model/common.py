"""
	conv1d与lstm结合, 输入数据为rri.
"""

import keras
import numpy as np
import time
import matplotlib.pyplot as plt
import json
import os
import random
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from keras.utils import plot_model
from keras.callbacks import *
from sklearn.model_selection import train_test_split


def write_txt_file(list_info, write_file_path):
	"""
	Write list object to TXT file.
	:param list list_info: List object you want to write.
	:param string write_file_path: TXT file path.
	:return: None
	"""
	with open(write_file_path, "w") as f:
		for info in list_info:
			f.write(str(info) + "\n")


def plot_fig(data, file_path="", title="", show_fig=False):
	if not os.path.exists(file_path) and file_path != "":
		os.makedirs(file_path)
	min, max = np.min(data, axis=0), np.max(data, axis=0)
	x = list(range(0, len(data), 1))
	f, ax = plt.subplots()
	ax.plot(x, data)
	ax.set_ylim([np.floor(min), np.ceil(max)])
	ax.set_title(title)
	if show_fig:
		plt.show()
	if title != "":
		plt.savefig(file_path + title + ".jpg")
	plt.close()
	

class LossHistory(keras.callbacks.Callback):
	def init(self):
		self.losses = []
	
	def on_epoch_end(self, batch, logs={}):
		self.losses.append(logs.get('loss'))


class TrainingMonitor(BaseLogger):
	"""
	https://blog.csdn.net/OliverkingLi/article/details/81214947
	"""
	
	def __init__(self, fig_path, model,
				 train_loss_path, test_loss_path, train_acc_path, test_acc_path, json_path=None, start_At=0):
		"""
		训练监控初始化
		:param fig_path: loss store path
		:param model:
		:param json_path: Json file path
		:param int start_At:
		:return: None
		"""
		
		super(TrainingMonitor, self).__init__()
		self.fig_path = fig_path + "/xxx.png"
		self.json_path = json_path
		self.start_At = start_At
		self.model = model
		self.epochs = 0
		
		self.train_loss_path = train_loss_path
		self.test_loss_path = test_loss_path
		self.train_acc_path = train_acc_path
		self.test_acc_path = test_acc_path
	
	def on_train_begin(self, logs={}):
		self.H = {}
		if self.json_path is not None:
			if os.path.exists(self.json_path):
				self.H = json.loads(open(self.json_path).read())
				if self.start_At > 0:
					for k in self.H.keys():
						self.H[k] = self.H[k][:self.start_At]
	
	def on_epoch_end(self, epoch, logs=None):
		for (k, v) in logs.items():
			l = self.H.get(k, [])
			l.append(v)
			self.H[k] = l
		if self.json_path is not None:
			f = open(self.json_path, 'w')
			f.write(json.dumps(self.H))
			f.close()
		if len(self.H["loss"]) > 1:
			N = np.arange(0, len(self.H["loss"]))
			plt.style.use("ggplot")
			plt.figure()
			plt.plot(N, self.H["loss"], label="train_loss")
			write_txt_file(self.H["loss"], self.train_loss_path)
			plt.plot(N, self.H["val_loss"], label="val_loss")
			write_txt_file(self.H["val_loss"], self.test_loss_path)
			plt.plot(N, self.H["acc"], label="train_acc")
			write_txt_file(self.H["acc"], self.train_acc_path)
			plt.plot(N, self.H["val_acc"], label="val_acc")
			write_txt_file(self.H["val_acc"], self.test_acc_path)
			plt.title("Training Loss and Accuracy [Epoch {}]".format(len(self.H["loss"])))
			plt.xlabel("Epoch #")
			plt.ylabel("Loss/Accuracy")
			plt.legend()
			plt.savefig(self.fig_path)
			plt.close()
