function [] = RRIRAMPEDR(file_path)
%UNTITLED2 此处显示有关此函数的摘要
%   此处显示详细说明
% outputArg1 = file_path;
% outputArg2 = write_file_path;

read_path = strcat(file_path, '\denoised_ecg_data.mat');
ecg_data = load(read_path);
ecg_data_1 = ecg_data.denoised_ecg_data;

Analysis = RunBioSigKit(ecg_data_1, 100, 0);          % Uses ECG1 as input,Fs=250
%-------------------- Call Pan Tompkins Algorithm ------------------- %
% Analysis.MTEO_qrstAlg;                        % Runs MTEO algorithm
% QRS = Analysis.Results.R;                     % Stores R peaks in QRS
%-------------------- Call MTEO QRS ------------------- %
try
    Analysis.MTEO_qrstAlg;                        % Runs MTEO algorithm
    Qwave = Analysis.Results.Q;
    Rwave = Analysis.Results.R;
    Swave = Analysis.Results.S;
    Twave = Analysis.Results.T;
    Pwave = Analysis.Results.P;
    EDR = Analysis.EDR_comp;
    save_path = strcat(file_path, '\Qwave.mat');
    save(save_path, 'Qwave');
    save_path = strcat(file_path, '\Rwave.mat');
    save(save_path, 'Rwave');
    save_path = strcat(file_path, '\Swave.mat');
    save(save_path, 'Swave');
    save_path = strcat(file_path, '\Twave.mat');
    save(save_path, 'Twave');
    save_path = strcat(file_path, '\Pwave.mat');
    save(save_path, 'Pwave');
    save_path = strcat(file_path, '\EDR.mat');
    save(save_path, 'EDR');
    % train_clear_id = [train_clear_id; index_train];
catch
    disp('it is noise.');
%     train_noise_id = [train_noise_id; index_train];
%     index_internal_record = index_internal_record + 1;
%     start_indice = start_indice + 6000;
%     continue
end

end

