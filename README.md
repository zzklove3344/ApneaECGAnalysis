# Code for OSA Detection Based on Apnea-ECG 
This project includes a preprocessing method for Apnea-ECG and a LSTM-RNN model for per-segment OSA detection.

## Introduction
If you want to use this program, you should download the Apnea-ecg database firstly. Here we provide a download link, https://pan.baidu.com/s/1xmzjY9rsdWTuO0qMKSv2Kg, code: 8fuq.

## Usage
Then, follow these steps and you will get the OSA detection model.

1. **Use matlab functions in python**. Follow the official documents [Matlab_Link](https://www.mathworks.com/help/matlab/matlab_external/get-started-with-matlab-engine-for-python.html).
 
1. **Run preprocessOfApneaECG.mit2Segments.py**. This python file convert Apnea-ECG database to minute-by-minute ECG segments, both train set(a01-a20,b01-b05,c01-c10) and test set(x01-x35). Don't forget to set path information in mit2Segments.py.
2. **Run preprocessOfApneaECG.preProcessing.py**. This python file process minute-by-minute ECG segments, including ECG denoising, extracting RRI,RAMP and EDR signal from ECG, smoothing and spline interpolation on RRI and RAMP and downsampling on EDR signal. In addition, we classify these segments into two kinds based on RRI, noise and clear.
3. **Run produceDatabase.py**. This python file produce train set and test set formatting .npy file. It will be stored in "data/" folder.
4. **Run model.lstmRNNModel.py**. This python file train LSTM-RNN network for per-segment OSA detection.

## Author
* zzklove3344 (Heilongjiang University), if you have any questions about codes, please contact zzklove3344@hotmail.com

## Citation information
If you use these modules in any other project, please refer to MIT open-source license.

## Dependencies
* wfdb
* numpy
* os
* BioSigKit
* keras, backend tensorflow
