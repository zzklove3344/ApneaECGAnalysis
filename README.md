# CodeForReadingApneaECG
**Convert ECGs with corresponding annotations to ECG segments.**

## Introduction
If you want to use this program, you should download the Apnea-ecg database firstly. Here we provide a download link, https://pan.baidu.com/s/1xmzjY9rsdWTuO0qMKSv2Kg, code: 8fuq.

Then you must set two basic variable in constant.py, **APNEA_ECG_DATABASE_PATH** and **SEGMENTS_BASE_PATH**. APNEA_ECG_DATABASE_PATH is the raw apnea-ecg database file path, and SEGMENTS_BASE_PATH is the file path which you want to store the ecg segments. After you can run divideSegments.py which can divide ecg record to 60s segments, it will consume a couple of minutes. Lastly, you can use function **get_database** to read ecg segments.

## Author
* zzklove3344 (Heilongjiang University), if you have any questions about codes, please contact zzklove3344@hotmail.com


## Dependencies
* wfdb
* numpy
* os
